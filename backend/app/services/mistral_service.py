from __future__ import annotations

import requests
from typing import Optional

from ..config import settings


class MistralService:
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 thinking_model: Optional[str] = None,
                 task_model: Optional[str] = None,
                 max_tokens: Optional[int] = None):
        self.api_key = api_key or settings.mistral_api_key
        self.base_url = (base_url or settings.mistral_base_url).rstrip('/')
        self.thinking_model = thinking_model or settings.mistral_thinking_model
        self.task_model = task_model or settings.mistral_task_model
        self.max_tokens = max_tokens or settings.mistral_max_tokens

    def _generate(self, prompt: str, model: str) -> str:
        if not self.api_key:
            raise ValueError("Mistral API key is required")
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": self.max_tokens,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def think(self, prompt: str) -> str:
        return self._generate(prompt, self.thinking_model)

    def complete(self, prompt: str) -> str:
        return self._generate(prompt, self.task_model)


mistral = MistralService()
