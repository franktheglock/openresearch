from __future__ import annotations

import requests
from typing import Optional

from ..config import settings


class AnthropicService:
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 thinking_model: Optional[str] = None,
                 task_model: Optional[str] = None,
                 max_tokens: Optional[int] = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.base_url = (base_url or settings.anthropic_base_url).rstrip('/')
        self.thinking_model = thinking_model or settings.anthropic_thinking_model
        self.task_model = task_model or settings.anthropic_task_model
        self.max_tokens = max_tokens or settings.anthropic_max_tokens

    def _generate(self, prompt: str, model: str) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Messages API returns content as a list of parts
        parts = data.get("content", [])
        text = "".join(p.get("text", "") for p in parts if p.get("type") in (None, "text"))
        return text.strip()

    def think(self, prompt: str) -> str:
        return self._generate(prompt, self.thinking_model)

    def complete(self, prompt: str) -> str:
        return self._generate(prompt, self.task_model)


anthropic = AnthropicService()
