from __future__ import annotations

from typing import List
import requests

from ..config import settings
from ..models.research import SearchHit


class SearxNGService:
	def __init__(self, base_url: str | None = None):
		self.base_url = (base_url or settings.searxng_base_url).rstrip("/")

	def search(self, query: str, language: str | None = None, num_results: int | None = None) -> List[SearchHit]:
		params = {
			"q": query,
			"format": "json",
			"language": language or settings.searxng_language,
			"categories": settings.searxng_engine,
			"safesearch": 1,
		}
		url = f"{self.base_url}/search"
		resp = requests.get(url, params=params, timeout=45)
		resp.raise_for_status()
		data = resp.json()
		results = []
		for r in data.get("results", [])[: (num_results or settings.searxng_results)]:
			results.append(
				SearchHit(
					title=r.get("title") or r.get("url") or "Untitled",
					url=r.get("url", ""),
					snippet=r.get("content"),
				)
			)
		return results


searx = SearxNGService()

