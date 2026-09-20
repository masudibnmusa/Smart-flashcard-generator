"""
Thin wrapper around the Anthropic API. Centralizes retries, JSON parsing,
and error handling so concept_extractor.py and question_generator.py don't
each reimplement it.
"""
import json
import re
import time

import anthropic

from app.config import config


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self):
        config.validate()
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def complete(self, system: str, prompt: str, max_retries: int = 3) -> str:
        """Send a prompt and return the raw text response."""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self._client.messages.create(
                    model=config.model,
                    max_tokens=config.max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                return "".join(
                    block.text for block in response.content if block.type == "text"
                )
            except anthropic.APIError as e:
                last_error = e
                wait = 2 ** attempt
                time.sleep(wait)
        raise LLMError(f"LLM call failed after {max_retries} attempts: {last_error}")

    def complete_json(self, system: str, prompt: str, max_retries: int = 3) -> dict | list:
        """
        Send a prompt expecting a JSON response and parse it.
        Strips markdown code fences if the model wraps its output in them.
        """
        raw = self.complete(system, prompt, max_retries=max_retries)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise LLMError(f"Model did not return valid JSON: {e}\nRaw output:\n{raw}")


llm_client = LLMClient()