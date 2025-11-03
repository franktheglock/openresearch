from __future__ import annotations

from typing import List
import requests
from bs4 import BeautifulSoup

from ..config import settings
from ..models.research import SearchHit


class DuckDuckGoService:
	def __init__(self, base_url: str | None = None):
		# DuckDuckGo doesn't have a configurable base URL like SearxNG
		# but we keep the parameter for consistency
		self.base_url = base_url or "https://duckduckgo.com"

	def search(self, query: str, language: str | None = None, num_results: int | None = None) -> List[SearchHit]:
		# DuckDuckGo search URL
		params = {
			"q": query,
			"kl": language or settings.duckduckgo_region or "us-en",
		}

		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
		}

		url = f"{self.base_url}/html"
		resp = requests.get(url, params=params, headers=headers, timeout=30)
		resp.raise_for_status()

		# Parse HTML results
		soup = BeautifulSoup(resp.text, 'html.parser')
		results = []

		# DuckDuckGo HTML structure: results are in .result elements
		result_elements = soup.select('.result')

		max_results = num_results or settings.duckduckgo_results or 8

		for result in result_elements[:max_results]:
			title_elem = result.select_one('.result__title')
			url_elem = result.select_one('.result__url')
			snippet_elem = result.select_one('.result__snippet')

			if title_elem:
				title = title_elem.get_text(strip=True)
				url = ""
				snippet = ""

				if url_elem:
					url = url_elem.get_text(strip=True)
					# Clean up the URL (remove leading/trailing dots, etc.)
					url = url.strip('.')

				if snippet_elem:
					snippet = snippet_elem.get_text(strip=True)

				# Skip if we don't have at least a title
				if title:
					results.append(
						SearchHit(
							title=title,
							url=url,
							snippet=snippet,
						)
					)

		return results


duckduckgo = DuckDuckGoService()