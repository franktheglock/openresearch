from __future__ import annotations

import requests
from typing import Optional

from ..config import settings


class OllamaService:
	def __init__(self, base_url: Optional[str] = None, thinking_model: Optional[str] = None, task_model: Optional[str] = None):
		self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
		self.thinking_model = thinking_model or settings.ollama_thinking_model
		self.task_model = task_model or settings.ollama_task_model

	def _generate(self, prompt: str, model: str, stream: bool = False) -> str:
		url = f"{self.base_url}/api/generate"
		payload = {
			"model": model,
			"prompt": prompt,
			"stream": False if not stream else True,
		}
		resp = requests.post(url, json=payload, timeout=120)
		resp.raise_for_status()
		data = resp.json()
		# Ollama returns { 'response': '...' }
		return data.get("response", "").strip()

	def think(self, prompt: str) -> str:
		return self._generate(prompt, model=self.thinking_model)

	def complete(self, prompt: str) -> str:
		return self._generate(prompt, model=self.task_model)


ollama = OllamaService()

