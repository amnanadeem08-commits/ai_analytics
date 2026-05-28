# services/llm_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv


class LLMService:
    """
    Centralized OpenRouter/OpenAI service layer.

    Responsibilities:
    - Load API credentials
    - Initialize OpenRouter client
    - Handle AI requests
    - Provide reusable AI helper methods
    """

    def __init__(self):
        env_path = r"D:\ai_analytics\ai_analytics\api.env"

        load_dotenv(dotenv_path=env_path)

        self.api_key = os.environ.get("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in api.env"
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )

    # ─────────────────────────────────────────────────────────────
    # Generic Chat Completion
    # ─────────────────────────────────────────────────────────────
    def generate_response(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = "openai/gpt-4.1"
    ) -> str:
        """
        Generic AI response generator.
        """

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt or (
                            "You are a senior AI analytics engineer."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"LLM Error: {str(e)}"

    # ─────────────────────────────────────────────────────────────
    # Codex-Style Code Generation
    # ─────────────────────────────────────────────────────────────
    def generate_code(
        self,
        prompt: str,
        model: str = "openai/gpt-4.1"
    ) -> str:
        """
        Generate production-quality code.
        """

        system_prompt = """
        You are a senior software engineer.

        Return:
        - clean production-ready code
        - modular architecture
        - maintainable structure
        - no unnecessary explanation
        """

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )

    # ─────────────────────────────────────────────────────────────
    # Analytics Insight Generation
    # ─────────────────────────────────────────────────────────────
    def generate_business_insight(
        self,
        prompt: str,
        model: str = "openai/gpt-4.1"
    ) -> str:
        """
        Generate business intelligence insights.
        """

        system_prompt = """
        You are a senior business intelligence analyst.

        Focus on:
        - trends
        - anomalies
        - executive summaries
        - actionable recommendations
        - business value
        """

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )