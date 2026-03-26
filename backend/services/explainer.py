import os
import json
from typing import List, Dict, Any
from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _laptop_summary(laptop: dict) -> str:
    return (
        f"{laptop.get('name')} "
        f"(₹{laptop.get('price_inr', '?'):,}, "
        f"CPU: {laptop.get('cpu', '?')}, "
        f"GPU: {laptop.get('gpu', 'Integrated')}, "
        f"RAM: {laptop.get('ram_gb', '?')}GB, "
        f"Battery: ~{laptop.get('battery_hrs', '?')}h)"
    )


def generate_explanations(
    laptops: List[Dict[str, Any]],
    user_query: str,
    intent: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Agent 3: given scored laptops + user context, produce
    plain-English explanations for each recommendation and
    a 'why not' sentence for the others.
    """
    if not laptops:
        return {"explanations": {}, "why_not": ""}

    recommended_summaries = "\n".join(
        f"{i+1}. {_laptop_summary(l)}" for i, l in enumerate(laptops)
    )

    prompt = f"""You are a friendly laptop expert helping a user choose their next laptop.

The user asked: "{user_query}"
Their priorities: {intent.get('priorities', [])}, budget: ₹{intent.get('budget_inr', 60000):,}
Their use case: {intent.get('use_case', 'general')}

We are recommending these laptops:
{recommended_summaries}

For EACH recommended laptop, write exactly 2 sentences explaining why it suits this user's
specific needs. Be conversational, mention specific specs, and keep language simple and friendly.

Also write 1 sentence explaining why cheaper or lower-spec alternatives were not recommended
(mention tradeoffs like weak GPU, poor battery, etc.).

Return ONLY valid JSON in this exact format (no markdown, no backticks):
{{
  "explanations": {{
    "<laptop name exactly as given>": "2-sentence explanation here"
  }},
  "why_not": "1-sentence dismissal of alternatives"
}}"""

    try:
        client = _get_client()
        model  = os.getenv("LLM_MODEL", "gpt-4o-mini")

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.4,
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        result = json.loads(raw)

        # Normalise keys: also map by laptop id for frontend lookup
        explanations = result.get("explanations", {})
        for laptop in laptops:
            name = laptop.get("name", "")
            lid  = laptop.get("id", "")
            text = explanations.get(name, "")
            if text and lid:
                explanations[lid] = text

        return {
            "explanations": explanations,
            "why_not": result.get("why_not", ""),
        }

    except Exception as exc:
        print(f"[explainer] LLM error: {exc} — using generic explanations")
        generic = {
            l.get("name", ""): (
                f"The {l.get('name')} is a strong match for your budget and use case. "
                f"Its specs align well with what you described."
            )
            for l in laptops
        }
        # Also key by id
        for l in laptops:
            lid = l.get("id", "")
            if lid:
                generic[lid] = generic.get(l.get("name", ""), "")

        return {
            "explanations": generic,
            "why_not": "Other options were skipped due to weaker specs or poor value for money.",
        }
