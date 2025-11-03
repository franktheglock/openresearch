import time
import requests
from typing import List

from ..config import settings

class LMStudioService:
    """Service wrapper for a local LMStudio OpenAI-compatible API."""
    def __init__(self):
        self._base_url = settings.lmstudio_base_url.rstrip('/')
        self.thinking_model = settings.lmstudio_thinking_model
        self.task_model = settings.lmstudio_task_model
        self.max_tokens = settings.lmstudio_max_tokens
        self._model_cache: dict[str, object] = {"ts": 0.0, "models": []}

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._base_url = (value or "").rstrip("/")
        # Reset cache when base URL changes
        self._model_cache = {"ts": 0.0, "models": []}

    def list_models(self, force_refresh: bool = False) -> List[str]:
        """Return LMStudio's available model identifiers."""
        now = time.time()
        cached = self._model_cache
        if (not force_refresh) and cached["models"] and now - cached["ts"] < 60:
            return cached["models"]  # type: ignore[index]

        try:
            resp = requests.get(f"{self.base_url}/models", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            models: List[str] = []
            if isinstance(data, dict):
                if isinstance(data.get("data"), list):
                    for item in data["data"]:
                        if isinstance(item, dict) and item.get("id"):
                            models.append(str(item["id"]))
                elif isinstance(data.get("models"), list):
                    for item in data["models"]:
                        if isinstance(item, dict) and item.get("name"):
                            models.append(str(item["name"]))
                        elif isinstance(item, str):
                            models.append(item)
            elif isinstance(data, list):
                models = [str(item) for item in data]
            self._model_cache = {"ts": now, "models": models}
            return models
        except Exception:
            # Keep previous cache (if any) and fall back to empty list
            return cached.get("models", [])  # type: ignore[return-value]

    @staticmethod
    def _normalize(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

    def _resolve_model_name(self, requested: str) -> str:
        if not requested:
            return requested
        available = self.list_models()
        if not available:
            return requested

        requested_norm = self._normalize(requested)
        # Prefer exact match
        for candidate in available:
            if candidate == requested:
                return candidate
        # Case-insensitive exact
        for candidate in available:
            if candidate.lower() == requested.lower():
                return candidate
        # Normalized (strip symbols/spaces)
        for candidate in available:
            if self._normalize(candidate) == requested_norm:
                return candidate
        # Substring containment (normalized)
        for candidate in available:
            if requested_norm in self._normalize(candidate):
                return candidate
        return requested

    def _chat(self, model: str, prompt: str) -> str:
        resolved_model = self._resolve_model_name(model)
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": resolved_model,
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": self.max_tokens,
        }
        resp = requests.post(url, json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        # OpenAI style: data["choices"][0]["message"]["content"]
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return str(data)

    def think(self, prompt: str) -> str:
        return self._chat(self.thinking_model, prompt)

    def complete(self, prompt: str) -> str:
        return self._chat(self.task_model, prompt)


lmstudio_client = LMStudioService()
