import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import generate
from app.core.prompt_templates import NOTES_SYSTEM_PROMPT
from app.models.interview import Interview
from app.models.note import Note
from app.models.number_record import NumberRecord
from app.models.outline import Outline
from app.models.transcript import TranscriptSegment
from app.services.document_service import get_documents_text


async def generate_notes(
    db: AsyncSession,
    interview_id: uuid.UUID,
) -> Note:
    """Generate comprehensive meeting notes after interview."""
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise ValueError("Interview not found")

    # Load full transcript
    result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.interview_id == interview_id)
        .order_by(TranscriptSegment.segment_index)
    )
    segments = result.scalars().all()
    full_transcript = "\n".join(
        f"[{s.speaker or 'unknown'}] {s.text}" for s in segments
    )

    # Load outline
    outline_result = await db.execute(
        select(Outline).where(
            Outline.interview_id == interview_id,
            Outline.is_active == True,
        )
    )
    outline = outline_result.scalars().first()

    # Load extracted numbers
    nums_result = await db.execute(
        select(NumberRecord).where(NumberRecord.interview_id == interview_id)
    )
    numbers = nums_result.scalars().all()

    # Load reference documents
    doc_text = await get_documents_text(db, interview_id)

    # Build prompt
    user_message = _build_notes_prompt(interview, full_transcript, outline, numbers, doc_text)

    raw_response = await generate(
        system_prompt=NOTES_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=8192,
        temperature=0.3,
    )

    # Parse structured parts from the response
    key_numbers_json = _extract_key_numbers(numbers)

    # Check or update existing note
    existing = await db.execute(
        select(Note).where(Note.interview_id == interview_id)
    )
    note = existing.scalars().first()

    if note:
        note.summary = _extract_summary(raw_response)
        note.full_notes = raw_response
        note.key_numbers = key_numbers_json
    else:
        note = Note(
            interview_id=interview_id,
            summary=_extract_summary(raw_response),
            full_notes=raw_response,
            key_numbers=key_numbers_json,
            key_insights=[],
            action_items=[],
        )
        db.add(note)

    await db.commit()
    await db.refresh(note)
    return note


def _build_notes_prompt(
    interview: Interview,
    transcript: str,
    outline: Outline | None,
    numbers: list[NumberRecord],
    doc_text: str,
) -> str:
    parts = []

    # Basic info
    parts.append(f"## 访谈基本信息")
    parts.append(f"- 专家: {interview.expert_name or '未知'}")
    parts.append(f"- 公司: {interview.expert_company or '未知'}")
    parts.append(f"- 职位: {interview.expert_title or '未知'}")
    parts.append(f"- 核心问题: {interview.core_questions or '未指定'}")

    if outline:
        parts.append(f"\n## 访谈提纲\n{json.dumps(outline.content, ensure_ascii=False)[:3000]}")

    parts.append(f"\n## 完整转录文本\n{transcript[:20000]}")

    if numbers:
        nums_data = [
            {"value": n.value, "context": n.context, "verification": n.verification, "category": n.category}
            for n in numbers
        ]
        parts.append(f"\n## 实时提取的关键数字\n{json.dumps(nums_data, ensure_ascii=False)}")

    if doc_text:
        parts.append(f"\n## 参考文档\n{doc_text[:3000]}")

    parts.append("\n请生成完整的结构化访谈纪要。特别注意：所有专家提及的数字必须无一遗漏地记录在关键数字汇总表中。")
    return "\n\n".join(parts)


def _extract_summary(notes_text: str) -> str:
    """Extract summary section from notes."""
    lines = notes_text.split("\n")
    in_summary = False
    summary_lines = []
    for line in lines:
        if "核心发现" in line or "摘要" in line:
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## "):
                break
            summary_lines.append(line)
    return "\n".join(summary_lines).strip() or notes_text[:500]


def _extract_key_numbers(numbers: list[NumberRecord]) -> list[dict]:
    """Create key numbers JSON from extracted number records."""
    return [
        {
            "value": n.value,
            "context": n.context,
            "category": n.category,
            "verification": n.verification,
            "flag_reason": n.flag_reason,
        }
        for n in numbers
    ]
