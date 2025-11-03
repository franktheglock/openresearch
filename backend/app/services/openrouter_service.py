from __future__ import annotations

import requests
from typing import Optional

from ..config import settings


class OpenRouterService:
    def __init__(self, api_key: Optional[str] = None, thinking_model: Optional[str] = None, task_model: Optional[str] = None, max_tokens: Optional[int] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.thinking_model = thinking_model or settings.openrouter_thinking_model
        self.task_model = task_model or settings.openrouter_task_model
        self.max_tokens = max_tokens or settings.openrouter_max_tokens

    def _generate(self, prompt: str, model: str) -> str:
        """Generate text using OpenRouter API (OpenAI-compatible)"""
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8081",  # Required by OpenRouter
            "X-Title": "OpenResearch"  # Optional but recommended
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": self.max_tokens
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        if "error" in data:
            raise Exception(f"OpenRouter API error: {data['error']['message']}")
        
        return data["choices"][0]["message"]["content"].strip()

    def think(self, prompt: str) -> str:
        """Use thinking model for planning and reasoning"""
        return self._generate(prompt, model=self.thinking_model)

    def complete(self, prompt: str) -> str:
        """Use task model for completion and writing"""
        return self._generate(prompt, model=self.task_model)

    def get_models(self) -> list[str]:
        """Get available models from OpenRouter"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return [model["id"] for model in data.get("data", [])]
        except Exception:
            return []


# Global instance
openrouter = OpenRouterService()