import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import generate_with_search
from app.core.prompt_templates import RESEARCH_SYSTEM_PROMPT
from app.models.research_result import ResearchResult

logger = logging.getLogger(__name__)


async def run_research(
    db: AsyncSession,
    interview_id: uuid.UUID,
    query: str,
    company: str | None = None,
    industry: str | None = None,
) -> ResearchResult:
    """Run AI-powered research based on core questions."""
    # Create research record
    research = ResearchResult(
        interview_id=interview_id,
        query=query,
        status="running",
    )
    db.add(research)
    await db.commit()
    await db.refresh(research)

    # Build the research prompt
    user_message = f"核心研究问题：{query}"
    if company:
        user_message += f"\n目标公司：{company}"
    if industry:
        user_message += f"\n所属行业：{industry}"
    user_message += "\n\n请进行深度调研，搜索相关公开信息，并按要求的JSON格式输出结构化分析结果。"

    try:
        raw_response = await generate_with_search(
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=16000,
        )

        # Try to parse JSON from response
        parsed = _extract_json(raw_response)
        research.company_overview = parsed.get("company_overview", "")
        research.industry_data = parsed.get("industry_data", "")
        research.key_numbers = parsed.get("key_numbers", [])
        research.info_gaps = parsed.get("info_gaps", [])
        research.raw_response = raw_response
        research.status = "completed"
    except Exception as e:
        logger.error(f"Research failed: {type(e).__name__}: {e}")
        research.status = "failed"
        research.raw_response = str(e)

    await db.commit()
    await db.refresh(research)
    return research


def _extract_json(text: str) -> dict:
    """Try to extract JSON from a text response."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find JSON block in markdown
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"company_overview": text, "industry_data": "", "key_numbers": [], "info_gaps": []}
