import anthropic

from app.config import settings


def get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def generate(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


async def generate_with_thinking(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 16000,
    thinking_budget: int = 10000,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Generate with extended thinking for deep research tasks."""
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        thinking={
            "type": "enabled",
            "budget_tokens": thinking_budget,
        },
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    # Return the text block (skip thinking blocks)
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


async def generate_with_search(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 16000,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Generate with web search tool for research tasks."""
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        tools=[{"type": "web_search_20250305"}],
        messages=[{"role": "user", "content": user_message}],
    )
    # Extract text blocks from response
    texts = []
    for block in response.content:
        if block.type == "text":
            texts.append(block.text)
    return "\n".join(texts)


async def stream_generate(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 8192,
    temperature: float = 0.3,
    model: str = "claude-sonnet-4-20250514",
):
    """Stream generation for long-form content like meeting notes."""
    client = get_client()
    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
