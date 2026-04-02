import json
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import generate
from app.core.prompt_templates import NUMBER_CROSSCHECK_SYSTEM_PROMPT
from app.models.number_record import NumberRecord
from app.models.research_result import ResearchResult
from app.services.document_service import get_documents_text

# Regex patterns for number extraction
NUMBER_PATTERNS = [
    # Chinese currency amounts: X亿, X万, X百万
    r'(\d+(?:\.\d+)?)\s*(?:亿|万亿|百万|千万|万)',
    # Percentages
    r'(\d+(?:\.\d+)?)\s*[%％]',
    # Currency: $X, ¥X
    r'[\$¥￥]\s*(\d+(?:\.\d+)?(?:\s*(?:billion|million|亿|万))?)',
    # Plain large numbers with context
    r'(\d{2,}(?:\.\d+)?)',
    # Growth rates: 增长XX%, 下降XX%
    r'(?:增长|下降|增速|同比|环比)\s*(\d+(?:\.\d+)?)\s*[%％]?',
]


def extract_numbers(text: str) -> list[dict]:
    """Extract numbers from transcript text using regex."""
    numbers = []
    seen_values = set()

    for pattern in NUMBER_PATTERNS:
        for match in re.finditer(pattern, text):
            value = match.group(0).strip()
            if value not in seen_values and len(value) > 1:
                seen_values.add(value)
                # Get surrounding context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                numbers.append({
                    "value": value,
                    "context": context,
                    "position": match.start(),
                })

    return numbers


async def save_extracted_numbers(
    db: AsyncSession,
    interview_id: uuid.UUID,
    segment_id: uuid.UUID,
    numbers: list[dict],
) -> list[NumberRecord]:
    """Save extracted numbers to database."""
    records = []
    for num in numbers:
        record = NumberRecord(
            interview_id=interview_id,
            segment_id=segment_id,
            value=num["value"],
            context=num["context"],
            category=_categorize_number(num["context"]),
        )
        db.add(record)
        records.append(record)

    await db.commit()
    for r in records:
        await db.refresh(r)
    return records


async def cross_check_numbers(
    db: AsyncSession,
    interview_id: uuid.UUID,
) -> dict:
    """Cross-check all extracted numbers against reference data."""
    # Load all numbers
    result = await db.execute(
        select(NumberRecord).where(NumberRecord.interview_id == interview_id)
    )
    numbers = result.scalars().all()
    if not numbers:
        return {"checks": [], "inconsistencies": []}

    # Load research results for reference
    res_result = await db.execute(
        select(ResearchResult).where(
            ResearchResult.interview_id == interview_id,
            ResearchResult.status == "completed",
        )
    )
    research = res_result.scalars().first()

    # Load reference documents
    doc_text = await get_documents_text(db, interview_id)

    # Build prompt
    user_message = _build_crosscheck_prompt(numbers, research, doc_text)

    raw_response = await generate(
        system_prompt=NUMBER_CROSSCHECK_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=2048,
        temperature=0.1,
    )

    check_result = _parse_crosscheck(raw_response)

    # Update number records with verification results
    for check in check_result.get("checks", []):
        num_id = check.get("number_id")
        if num_id:
            for num in numbers:
                if str(num.id) == num_id:
                    num.verification = check.get("verification", "unverified")
                    num.flag_reason = check.get("reason")
                    break

    await db.commit()
    return check_result


def _categorize_number(context: str) -> str:
    """Categorize a number based on its context."""
    categories = {
        "revenue": ["收入", "营收", "营业额", "销售额", "revenue"],
        "profit": ["利润", "净利", "毛利", "profit", "margin"],
        "market_size": ["市场规模", "市场", "market size"],
        "growth_rate": ["增长", "增速", "同比", "环比", "growth"],
        "market_share": ["份额", "占比", "市占率", "share"],
        "headcount": ["员工", "人数", "团队", "headcount"],
        "valuation": ["估值", "市值", "valuation"],
    }
    for cat, keywords in categories.items():
        if any(kw in context.lower() for kw in keywords):
            return cat
    return "other"


def _build_crosscheck_prompt(
    numbers: list[NumberRecord],
    research: ResearchResult | None,
    doc_text: str,
) -> str:
    parts = []

    nums_list = [
        {"number_id": str(n.id), "value": n.value, "context": n.context or "", "category": n.category or ""}
        for n in numbers
    ]
    parts.append(f"## 访谈中提取的数字\n{json.dumps(nums_list, ensure_ascii=False)}")

    if research and research.key_numbers:
        parts.append(f"## 调研结果中的参考数字\n{json.dumps(research.key_numbers, ensure_ascii=False)}")

    if doc_text:
        parts.append(f"## 参考文档数据\n{doc_text[:3000]}")

    parts.append("\n请对每个数字进行交叉校验，按要求的JSON格式输出。")
    return "\n\n".join(parts)


def _parse_crosscheck(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"checks": [], "inconsistencies": []}
