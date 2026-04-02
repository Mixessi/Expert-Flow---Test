import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import generate
from app.core.prompt_templates import OUTLINE_SYSTEM_PROMPT
from app.models.interview import Interview
from app.models.outline import Outline
from app.models.research_result import ResearchResult
from app.services.document_service import get_documents_text


async def generate_outline(
    db: AsyncSession,
    interview_id: uuid.UUID,
    feedback: str | None = None,
) -> Outline:
    """Generate interview outline integrating research results and reference documents."""
    # Load interview
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise ValueError("Interview not found")

    # Load research results
    result = await db.execute(
        select(ResearchResult).where(
            ResearchResult.interview_id == interview_id,
            ResearchResult.status == "completed",
        ).order_by(ResearchResult.created_at.desc())
    )
    research = result.scalars().first()

    # Load reference document texts
    doc_text = await get_documents_text(db, interview_id)

    # Build context for outline generation
    user_message = _build_outline_prompt(interview, research, doc_text, feedback)

    raw_response = await generate(
        system_prompt=OUTLINE_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=4096,
        temperature=0.7,
    )

    # Parse JSON content
    content = _extract_json(raw_response)

    # Deactivate previous outlines
    prev_result = await db.execute(
        select(Outline).where(
            Outline.interview_id == interview_id,
            Outline.is_active == True,
        )
    )
    for prev in prev_result.scalars().all():
        prev.is_active = False

    # Get next version number
    ver_result = await db.execute(
        select(Outline).where(Outline.interview_id == interview_id)
    )
    version = len(ver_result.scalars().all()) + 1

    outline = Outline(
        interview_id=interview_id,
        version=version,
        content=content,
        is_active=True,
    )
    db.add(outline)
    await db.commit()
    await db.refresh(outline)
    return outline


def _build_outline_prompt(
    interview: Interview,
    research: ResearchResult | None,
    doc_text: str,
    feedback: str | None,
) -> str:
    parts = []

    parts.append(f"## 核心研究问题\n{interview.core_questions or '未指定'}")

    if interview.expert_name:
        parts.append(f"## 专家信息\n- 姓名: {interview.expert_name}")
        if interview.expert_title:
            parts.append(f"- 职位: {interview.expert_title}")
        if interview.expert_company:
            parts.append(f"- 公司: {interview.expert_company}")
        if interview.expert_bio:
            parts.append(f"- 背景: {interview.expert_bio}")

    if research:
        parts.append("## AI调研结果")
        if research.company_overview:
            parts.append(f"### 公司概览\n{research.company_overview}")
        if research.industry_data:
            parts.append(f"### 行业数据\n{research.industry_data}")
        if research.key_numbers:
            parts.append(f"### 关键数字\n{json.dumps(research.key_numbers, ensure_ascii=False)}")
        if research.info_gaps:
            parts.append(f"### 信息空白点\n{json.dumps(research.info_gaps, ensure_ascii=False)}")

    if doc_text:
        parts.append(f"## 参考文档内容\n{doc_text[:8000]}")

    if feedback:
        parts.append(f"## 用户反馈（请据此调整提纲）\n{feedback}")

    parts.append("\n请基于以上信息生成结构化的访谈提纲，按要求的JSON格式输出。")
    return "\n\n".join(parts)


def _extract_json(text: str) -> dict:
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
    return {"sections": [], "raw_text": text}
