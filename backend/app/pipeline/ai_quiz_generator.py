"""AI Dynamic Quiz Generator: Uses LLM to continuously invent unique Python coding quizzes.
Ensures zero duplicates by checking existing database history before returning.
"""

import ast
import json
import re
import uuid
import hashlib
from typing import Dict, Any, Optional, List
import httpx

from backend.app.config import settings
from backend.app.core.logging import logger

FALLBACK_MODELS = [
    "cohere/north-mini-code:free",
    "liquid/lfm-2.5-2.6b:free",
    "qwen/qwen3.8-27b:free"
]

TOPIC_IDEAS = [
    "walrus operator ':=' inside list comprehension",
    "dictionary union operator '|' with key precedence",
    "isinstance with tuple of types and bool inheritance",
    "default argument trap with set instead of list",
    "generator expression vs list comprehension scoping in Python 3",
    "string formatting with '!r' vs '!s'",
    "unpacking with starred expression '*rest, last'",
    "math.fsum vs sum on list of floating points",
    "zip with strict=True vs default zip behavior",
    "enumerate with custom start offset index",
    "re.sub with lambda replacer function",
    "list.sort with custom lambda key reversing",
    "functools.partial argument binding precedence",
    "namedtuple defaults and attribute access",
    "try/except/else/finally block execution sequence",
    "object identity trap with empty tuple vs empty list '() is ()'",
    "closure variable mutation with nonlocal keyword",
    "class variable vs instance variable shadow trap",
    "round(2.5) vs round(3.5) round-to-even Bankers rounding",
    "bitwise XOR '^' swap trick behavior",
    "set intersection '&' with dictionary keys view",
    "itertools.accumulate default vs custom function",
    "any() with generator containing side effects",
    "bytes vs bytearray immutability differences"
]


class AIQuizGenerator:
    """Generates novel, tricky Python multiple-choice quizzes using AI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.preferred_model = settings.openrouter_model

    def _get_models(self) -> List[str]:
        models = []
        if self.preferred_model:
            models.append(self.preferred_model)
        for m in FALLBACK_MODELS:
            if m not in models:
                models.append(m)
        return models

    async def generate_quiz(
        self,
        exclude_titles: Optional[List[str]] = None,
        exclude_hashes: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a brand-new, unique Python quiz guaranteed not to duplicate existing content."""
        if not self.api_key:
            logger.warning("[AIQuizGenerator] No OpenRouter API key found. Skipping AI generation.")
            return None

        import random
        random_topic = random.choice(TOPIC_IDEAS)
        exclude_sample = (exclude_titles or [])[:15]
        exclude_prompt = "\n".join([f"- {t}" for t in exclude_sample])

        prompt = f"""You are a master Python educator creating viral Instagram Reels programming quiz challenges.
Create a brand new, tricky, educational Python multiple-choice quiz about: '{random_topic}'.

CRITICAL RULES:
1. The quiz MUST test a real, subtle Python feature (output puzzle or gotcha).
2. The code must be compact (2 to 5 lines maximum), clean, and 100% syntactically valid Python.
3. DO NOT repeat or create anything similar to these already-published quizzes:
{exclude_prompt}
4. Provide exactly 4 options (A, B, C, D) where only 1 is correct.
5. Provide a clear, short explanation.

Return ONLY a valid JSON object matching this schema (no markdown formatting, no code fences):
{{
  "quiz_id": "{random_topic.replace(' ', '_')[:20]}",
  "title": "Python Quiz: Topic Name",
  "question": "What is the output of this code?",
  "file_tab": "main.py",
  "code": "# Python code testing " + "{random_topic}",
  "badge_text": "Tricky Trap!",
  "options": [
    {{"letter": "A", "text": "Option A"}},
    {{"letter": "B", "text": "Option B"}},
    {{"letter": "C", "text": "Option C"}},
    {{"letter": "D", "text": "Option D"}}
  ],
  "correct_idx": 0,
  "explanation_lines": [
    "- Explanation line 1",
    "- Explanation line 2"
  ],
  "caption": "🔥 Python Quiz: Question topic!\\n\\nComment your answer before the reveal! 👇\\n\\n#python #coding #programming #developer"
}}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            for model in self._get_models():
                try:
                    logger.info(f"[AIQuizGenerator] Attempting quiz generation with model '{model}'...")
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful Python code assistant. You always respond in raw valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if response.status_code != 200:
                        logger.warning(f"[AIQuizGenerator] Model {model} returned HTTP {response.status_code}: {response.text[:120]}")
                        continue

                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        continue
                    msg = choices[0].get("message", {})
                    content = msg.get("content") or msg.get("reasoning") or choices[0].get("text") or ""
                    content = str(content).strip()

                    match = re.search(r"\{.*\}", content, re.DOTALL)
                    if not match:
                        logger.warning(f"[AIQuizGenerator] No JSON object found in response from {model}")
                        continue

                    quiz_json = None
                    try:
                        quiz_json = json.loads(match.group(0))
                    except Exception:
                        try:
                            quiz_json = ast.literal_eval(match.group(0))
                        except Exception as jde:
                            logger.warning(f"[AIQuizGenerator] JSON/literal_eval parse error: {jde}")
                            continue

                    if not isinstance(quiz_json, dict):
                        continue

                    # Validate required fields
                    if not self._validate_quiz_schema(quiz_json):
                        logger.warning("[AIQuizGenerator] JSON output did not meet schema requirements.")
                        continue

                    # Validate Python syntax
                    code_str = quiz_json["code"]
                    try:
                        ast.parse(code_str)
                    except SyntaxError as syn_err:
                        logger.warning(f"[AIQuizGenerator] Generated code has invalid syntax: {syn_err}")
                        continue

                    # Ensure unique ID
                    base_id = re.sub(r"[^a-z0-9_]", "", quiz_json.get("quiz_id", "").lower())
                    if not base_id or len(base_id) < 3:
                        base_id = f"ai_quiz_{uuid.uuid4().hex[:8]}"
                    else:
                        base_id = f"ai_{base_id}_{uuid.uuid4().hex[:6]}"
                    quiz_json["quiz_id"] = base_id

                    # Check title deduplication
                    title_norm = quiz_json["title"].strip().lower()
                    if exclude_titles and any(title_norm == t.strip().lower() for t in exclude_titles):
                        logger.warning(f"[AIQuizGenerator] Generated title '{quiz_json['title']}' was previously used. Skipping.")
                        continue

                    # Check code hash deduplication
                    code_hash = hashlib.sha256(code_str.strip().encode()).hexdigest()
                    if exclude_hashes and code_hash in exclude_hashes:
                        logger.warning("[AIQuizGenerator] Generated code hash matched existing quiz. Skipping.")
                        continue

                    quiz_json["code_hash"] = code_hash
                    logger.info(f"[AIQuizGenerator] Successfully generated fresh novel quiz: '{quiz_json['title']}'")
                    return quiz_json

                except Exception as e:
                    logger.warning(f"[AIQuizGenerator] Error with model {model}: {e}")

        logger.warning("[AIQuizGenerator] All AI models failed. Falling back to expanded curated pool.")
        return None

    def _validate_quiz_schema(self, q: Dict[str, Any]) -> bool:
        """Validate structure of quiz dictionary."""
        required = ["title", "question", "code", "options", "correct_idx", "explanation_lines"]
        if not all(k in q for k in required):
            return False
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
        if not (0 <= q["correct_idx"] <= 3):
            return False
        if not isinstance(q["code"], str) or len(q["code"].strip()) == 0:
            return False

        # Reject generic placeholder text
        title_lower = q["title"].lower()
        if any(p in title_lower for p in ["short catchy title", "topic name", "sample title", "insert title"]):
            return False
        if any(p in q["code"].lower() for p in ["# python code testing"]):
            return False

        return True
