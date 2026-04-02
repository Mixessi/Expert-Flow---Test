import json

from app.core.claude_client import generate
from app.core.prompt_templates import CREDIBILITY_SYSTEM_PROMPT


async def evaluate_credibility(
    expert_bio: str,
    transcript_window: str,
    number_flags: list[dict] | None = None,
) -> dict:
    """Evaluate expert credibility based on interview content."""
    parts = []

    if expert_bio:
        parts.append(f"## 专家背景\n{expert_bio}")

    parts.append(f"## 访谈内容（最近片段）\n{transcript_window[-3000:]}")

    if number_flags:
        parts.append(f"## 数字校验异常\n{json.dumps(number_flags, ensure_ascii=False)}")

    user_message = "\n\n".join(parts)
    user_message += "\n\n请评估该专家的可信度，按要求的JSON格式输出。"

    raw_response = await generate(
        system_prompt=CREDIBILITY_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=1024,
        temperature=0.2,
    )

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw_response[start:end])
            except json.JSONDecodeError:
                pass
    return {"score": 0.5, "level": "medium", "factors": [], "recommendation": "数据不足，继续观察"}
