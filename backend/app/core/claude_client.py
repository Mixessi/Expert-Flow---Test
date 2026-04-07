import json
import logging
from typing import AsyncIterator

import anthropic
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# --- Provider detection ---

def _get_provider() -> str:
    """Return 'openrouter', 'anthropic', or 'none'."""
    if settings.openrouter_api_key:
        return "openrouter"
    if settings.anthropic_api_key:
        return "anthropic"
    return "none"


def _has_api_key() -> bool:
    provider = _get_provider()
    logger.info(f"API provider: {provider}")
    return provider != "none"


def _get_model(default: str = "claude-sonnet-4-20250514") -> str:
    """Return model name, adapting for OpenRouter if needed."""
    if settings.ai_model:
        return settings.ai_model
    provider = _get_provider()
    if provider == "openrouter":
        return "anthropic/claude-3.5-sonnet"
    return default


def get_client() -> anthropic.AsyncAnthropic:
    """Get Anthropic client (only for direct Anthropic API)."""
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


# --- OpenRouter API calls via httpx ---

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _openrouter_call(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model: str | None = None,
) -> str:
    """Call OpenRouter's OpenAI-compatible API."""
    model = model or _get_model()
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _openrouter_stream(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 8192,
    temperature: float = 0.3,
    model: str | None = None,
) -> AsyncIterator[str]:
    """Stream from OpenRouter's API."""
    model = model or _get_model()
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", OPENROUTER_URL, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


# --- Mock responses for demo without API key ---

MOCK_RESEARCH = json.dumps({
    "company_overview": "[Demo 模式] 这是一个模拟的公司概览。配置 ANTHROPIC_API_KEY 或 OPENROUTER_API_KEY 后将使用真实 AI 分析。\n\n示例：该公司成立于2015年，主营业务为新能源汽车动力电池研发与制造，2025年营收约120亿元。",
    "industry_data": "[Demo 模式] 模拟行业数据。\n\n全球动力电池市场规模约5000亿元，年增长率25%。市场格局呈头部集中趋势，CR3 约65%。",
    "key_numbers": [
        {"metric": "市场规模", "value": "5000亿元", "source": "Demo数据", "date": "2025"},
        {"metric": "行业增速", "value": "25%", "source": "Demo数据", "date": "2025"},
        {"metric": "CR3集中度", "value": "65%", "source": "Demo数据", "date": "2025"}
    ],
    "info_gaps": [
        "该公司2026年产能扩张计划的具体细节",
        "新一代电池技术的量产时间表",
        "海外市场拓展的实际进展"
    ]
}, ensure_ascii=False)

MOCK_OUTLINE = json.dumps({
    "sections": [
        {
            "title": "开场验证（TQ 测试问题）",
            "purpose": "快速验证专家可信度",
            "questions": [
                {"text": "[Demo] 贵公司2025年的动力电池出货量大约是多少GWh？", "rationale": "验证专家对基础数据的掌握程度", "priority": "high", "type": "test_question", "expected_info": "具体出货量数字"}
            ]
        },
        {
            "title": "核心业务与竞争格局",
            "purpose": "了解公司在行业中的定位与竞争优势",
            "questions": [
                {"text": "[Demo] 目前公司最大的竞争优势体现在哪些方面？", "rationale": "了解核心竞争力", "priority": "high", "type": "core", "expected_info": "技术/成本/客户关系等维度"},
                {"text": "[Demo] 与主要竞争对手相比，成本结构上有什么差异？", "rationale": "量化竞争优势", "priority": "medium", "type": "core", "expected_info": "具体成本数据"}
            ]
        },
        {
            "title": "未来发展与风险",
            "purpose": "评估增长前景和潜在风险",
            "questions": [
                {"text": "[Demo] 未来2年的产能扩张计划是怎样的？", "rationale": "评估增长潜力", "priority": "high", "type": "core", "expected_info": "产能数字和时间表"},
                {"text": "[Demo] 目前面临的最大挑战或风险是什么？", "rationale": "识别风险因素", "priority": "medium", "type": "follow_up", "expected_info": "风险描述"}
            ]
        }
    ],
    "estimated_duration_minutes": 60,
    "key_hypotheses": [
        "[Demo] 假设1: 该公司有望在2026年实现市场份额提升",
        "[Demo] 假设2: 新技术路线将带来成本优势"
    ]
}, ensure_ascii=False)

MOCK_FOLLOWUP = json.dumps([
    {"text": "[Demo] 您刚才提到的增长数字，能否具体说明是哪个业务板块的？", "rationale": "专家提到增长但未展开细节", "priority": "high", "trigger": "信息未展开"},
    {"text": "[Demo] 这个利润率水平在行业中处于什么位置？", "rationale": "需要横向对比来验证数据合理性", "priority": "medium", "trigger": "缺乏对比"}
], ensure_ascii=False)

MOCK_CROSSCHECK = json.dumps({
    "checks": [],
    "inconsistencies": []
}, ensure_ascii=False)

MOCK_CREDIBILITY = json.dumps({
    "score": 0.7,
    "level": "medium",
    "factors": [
        {"dimension": "信息具体性", "score": 0.7, "evidence": "[Demo] 等待更多数据", "concern": ""},
        {"dimension": "内部一致性", "score": 0.8, "evidence": "[Demo] 暂无矛盾", "concern": ""},
        {"dimension": "领域匹配度", "score": 0.6, "evidence": "[Demo] 待评估", "concern": ""}
    ],
    "recommendation": "[Demo 模式] 配置 API Key 后将提供真实的可信度评估"
}, ensure_ascii=False)

MOCK_NOTES = """# 访谈纪要 [Demo 模式]

> 配置 ANTHROPIC_API_KEY 或 OPENROUTER_API_KEY 后将生成真实的 AI 访谈纪要

## 基本信息
- 本纪要为 Demo 演示数据

## 核心发现摘要
1. [Demo] 这里将展示基于访谈内容的核心发现
2. [Demo] AI 会按主题维度组织关键信息

## 关键数字汇总表
| 数字 | 上下文 | Cross Check | 可信度 |
|------|--------|-------------|--------|
| [Demo] | 示例数据 | 待验证 | - |

## 待跟进问题
- [Demo] 需要在后续访谈中深入了解的问题

## 行动建议
- [Demo] 建议安排后续访谈验证关键假设
"""


def _get_mock(system_prompt: str) -> str:
    """Return appropriate mock response based on the prompt type."""
    prompt_lower = system_prompt[:100].lower()
    if "调研" in prompt_lower or "research" in prompt_lower:
        return MOCK_RESEARCH
    elif "提纲" in prompt_lower or "outline" in prompt_lower:
        return MOCK_OUTLINE
    elif "追问" in prompt_lower or "follow" in prompt_lower:
        return MOCK_FOLLOWUP
    elif "校验" in prompt_lower or "cross" in prompt_lower or "数字" in prompt_lower:
        return MOCK_CROSSCHECK
    elif "可信度" in prompt_lower or "credib" in prompt_lower:
        return MOCK_CREDIBILITY
    elif "纪要" in prompt_lower or "note" in prompt_lower:
        return MOCK_NOTES
    return '{"message": "[Demo 模式] 请配置 API Key 启用 AI 功能"}'


# --- Public API functions ---

async def generate(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    if not _has_api_key():
        return _get_mock(system_prompt)

    provider = _get_provider()
    if provider == "openrouter":
        return await _openrouter_call(system_prompt, user_message, max_tokens, temperature)

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
    if not _has_api_key():
        return _get_mock(system_prompt)

    provider = _get_provider()
    if provider == "openrouter":
        # OpenRouter doesn't support extended thinking, use regular call
        return await _openrouter_call(system_prompt, user_message, max_tokens, temperature=0.7)

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
    if not _has_api_key():
        return _get_mock(system_prompt)

    provider = _get_provider()
    if provider == "openrouter":
        # OpenRouter doesn't support Anthropic's web_search tool,
        # use regular generation with instruction to provide detailed analysis
        enhanced_prompt = system_prompt + "\n\n注意：当前无法使用网络搜索，请基于你的训练知识尽可能提供详细的分析和数据。"
        return await _openrouter_call(enhanced_prompt, user_message, max_tokens, temperature=0.7)

    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        tools=[{"type": "web_search_20250305"}],
        messages=[{"role": "user", "content": user_message}],
    )
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
    if not _has_api_key():
        yield _get_mock(system_prompt)
        return

    provider = _get_provider()
    if provider == "openrouter":
        async for chunk in _openrouter_stream(system_prompt, user_message, max_tokens, temperature):
            yield chunk
        return

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
