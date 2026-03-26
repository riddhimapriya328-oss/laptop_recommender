import os
import json
from openai import OpenAI
from models.query import QueryIntent

_client: OpenAI | None = None

SAFE_DEFAULTS = QueryIntent(
    budget_inr=60000,
    use_case="general",
    priorities=[],
    brand_pref=None,
)

SYSTEM_PROMPT = """You are a laptop requirements parser.
Extract structured intent from the user's message.
Return ONLY valid JSON with these exact keys:
- budget_inr: integer (default 60000 if not mentioned; convert any currency to INR, 1 USD ≈ 83 INR)
- use_case: one of [gaming, coding, student, design, budget, general]
- priorities: list, each item one of [performance, battery, portability, display, price, storage]
- brand_pref: string brand name or null

Return ONLY the JSON object. No explanation, no markdown, no backticks."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def parse_query(user_query: str) -> QueryIntent:
    """Agent 1: parse natural language query → structured intent."""
    try:
        client = _get_client()
        model  = os.getenv("LLM_MODEL", "gpt-4o-mini")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_query},
            ],
            max_tokens=200,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        parsed = json.loads(raw)

        # Validate and coerce with Pydantic
        return QueryIntent(**parsed)

    except Exception as exc:
        print(f"[query_parser] LLM error: {exc} — using defaults")
        return SAFE_DEFAULTS
