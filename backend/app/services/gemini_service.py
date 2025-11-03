from __future__ import annotations

import requests
from typing import Optional

from ..config import settings


class GeminiService:
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 thinking_model: Optional[str] = None,
                 task_model: Optional[str] = None,
                 max_tokens: Optional[int] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.base_url = (base_url or settings.gemini_base_url).rstrip('/')
        self.thinking_model = thinking_model or settings.gemini_thinking_model
        self.task_model = task_model or settings.gemini_task_model
        self.max_tokens = max_tokens or settings.gemini_max_tokens

    def _generate(self, prompt: str, model: str) -> str:
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": self.max_tokens}
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        return text.strip()

    def think(self, prompt: str) -> str:
        return self._generate(prompt, self.thinking_model)

    def complete(self, prompt: str) -> str:
        return self._generate(prompt, self.task_model)


gemini = GeminiService()
