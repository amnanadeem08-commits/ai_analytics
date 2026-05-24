"""
llm_client.py — Shared LLM calls for Anthropic and OpenAI (no Streamlit).
"""

import httpx
import logging
from config import AI_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY, AI_MODEL, AI_MAX_TOKENS

logger = logging.getLogger(__name__)


def _build_http_client() -> httpx.Client:
    """Build an HTTP client that ignores system proxy settings for local execution."""
    return httpx.Client(proxy=None, follow_redirects=True)


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
