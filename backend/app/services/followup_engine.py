import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import generate
from app.core.prompt_templates import FOLLOWUP_SYSTEM_PROMPT
from app.models.outline import Outline
from app.services.document_service import get_documents_text


async def generate_followup_prompts(
    db: AsyncSession,
    interview_id: uuid.UUID,
    recent_transcript: str,
    covered_topics: list[str] | None = None,
) -> list[dict]:
    """Generate JIT follow-up prompts based on recent transcript."""
    # Load active outline
    result = await db.execute(
        select(Outline).where(
            Outline.interview_id == interview_id,
            Outline.is_active == True,
        )
    )
    outline = result.scalars().first()

    # Load reference documents
    doc_text = await get_documents_text(db, interview_id)

    user_message = _build_followup_prompt(recent_transcript, outline, doc_text, covered_topics)

    raw_response = await generate(
        system_prompt=FOLLOWUP_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=1024,
        temperature=0.5,
    )

    return _parse_followup_response(raw_response)


def _build_followup_prompt(
    recent_transcript: str,
    outline: Outline | None,
    doc_text: str,
    covered_topics: list[str] | None,
) -> str:
    parts = []

    if outline:
        parts.append(f"## 访谈提纲\n{json.dumps(outline.content, ensure_ascii=False)[:3000]}")

    parts.append(f"## 最新转录文本（最近2分钟）\n{recent_transcript[-2000:]}")

    if doc_text:
        parts.append(f"## 参考文档关键数据\n{doc_text[:2000]}")

    if covered_topics:
        parts.append(f"## 已覆盖话题\n{', '.join(covered_topics)}")

    parts.append("\n请基于以上信息生成追问建议，按要求的JSON数组格式输出。")
    return "\n\n".join(parts)


def _parse_followup_response(text: str) -> list[dict]:
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return []
