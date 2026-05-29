"""
llm_client.py — Shared LLM calls for Anthropic and OpenAI (no Streamlit).
"""

import httpx
import logging
from config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    AI_MODEL,
    OPENROUTER_MODEL,
    AI_MAX_TOKENS,
)

logger = logging.getLogger(__name__)

# Free OpenRouter models tried in order when the primary is rate-limited/unavailable.
_OPENROUTER_FALLBACKS = [
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-v4-flash:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
]


def _build_http_client() -> httpx.Client:
    """Build an HTTP client that ignores system proxy settings for local execution."""
    return httpx.Client(
        proxy=None,
        follow_redirects=True,
        timeout=httpx.Timeout(25.0, connect=8.0),
    )


def _openrouter_models() -> list[str]:
    """Primary model first, then unique fallbacks."""
    models = [OPENROUTER_MODEL] if OPENROUTER_MODEL else []
    for m in _OPENROUTER_FALLBACKS:
        if m not in models:
            models.append(m)
    return models


def _call_openrouter(messages: list[dict[str, str]], tokens: int) -> str | None:
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        http_client=_build_http_client(),
        max_retries=0,  # we manage fallback/retry ourselves; avoid SDK backoff stacking
    )

    last_error: Exception | None = None
    for model in _openrouter_models():
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=tokens,
                messages=messages,
            )
            content = resp.choices[0].message.content
            if content:
                return content
            logger.info("OpenRouter model %s returned empty content; trying next.", model)
        except Exception as e:  # includes rate-limit (429) and provider errors
            last_error = e
            status = getattr(getattr(e, "response", None), "status_code", None) or getattr(e, "status_code", None)
            logger.info("OpenRouter model %s failed (%s); trying next.", model, status or e)

    if last_error:
        logger.warning("All OpenRouter models failed. Last error: %s", last_error)
    return None


def call_llm(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int | None = None,
    history: list[dict[str, str]] | None = None,
) -> str | None:
    """
    Call the configured AI provider. Returns response text, or None if unavailable.
    """
    tokens = max_tokens or AI_MAX_TOKENS
    try:
        if AI_PROVIDER == "openrouter":
            if not OPENROUTER_API_KEY:
                logger.warning("OpenRouter provider configured but OPENROUTER_API_KEY is missing.")
                return None

            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": user_prompt})
            return _call_openrouter(messages, tokens)

        if AI_PROVIDER == "anthropic":
            if not ANTHROPIC_API_KEY:
                logger.warning("Anthropic provider configured but ANTHROPIC_API_KEY is missing.")
                return None

            import anthropic

            client = anthropic.Anthropic(
                api_key=ANTHROPIC_API_KEY,
                http_client=_build_http_client(),
            )
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": user_prompt})
            resp = client.messages.create(
                model=AI_MODEL,
                max_tokens=tokens,
                messages=messages,
            )
            return resp.content[0].text

        if AI_PROVIDER == "openai":
            if not OPENAI_API_KEY:
                logger.warning("OpenAI provider configured but OPENAI_API_KEY is missing.")
                return None

            from openai import OpenAI

            client = OpenAI(
                api_key=OPENAI_API_KEY,
                http_client=_build_http_client(),
            )
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": user_prompt})
            resp = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=tokens,
                messages=messages,
            )
            return resp.choices[0].message.content

        logger.warning("AI_PROVIDER '%s' is not supported or is not configured.", AI_PROVIDER)
    except httpx.HTTPStatusError as e:
        logger.warning("LLM call returned HTTP error %s: %s", e.response.status_code if e.response else "unknown", e)
    except Exception as e:
        logger.warning("LLM call failed: %s", e)

    return None
