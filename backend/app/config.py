from functools import lru_cache
from typing import List, Any
import sys
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	# API & CORS
	allowed_origins: List[str] = Field(default_factory=lambda: [
		"*"
	])

	# LLM Provider Selection
	llm_provider: str = Field(default="openrouter", description="Provider key: ollama | openrouter | openai | anthropic | gemini | mistral | groq | lmstudio")

	# Search Provider Selection
	search_provider: str = Field(default="searxng", description="Search provider: searxng | duckduckgo")

	# Ollama Services
	ollama_base_url: str = Field(default="http://localhost:11434")
	ollama_thinking_model: str = Field(default="deepseek-r1:1.5b")
	ollama_task_model: str = Field(default="llama3.1:8b")

	# OpenRouter Services  
	openrouter_api_key: str = Field(default="", description="OpenRouter API key")
	openrouter_thinking_model: str = Field(default="openai/gpt-oss-120b", description="Model for reasoning/planning")
	openrouter_task_model: str = Field(default="openai/gpt-oss-120b", description="Model for writing/completion")
	openrouter_max_tokens: int = Field(default=4096, description="Maximum tokens for OpenRouter responses")

	# OpenAI
	openai_api_key: str = Field(default="", description="OpenAI API key")
	openai_base_url: str = Field(default="https://api.openai.com/v1")
	openai_thinking_model: str = Field(default="gpt-4o-mini")
	openai_task_model: str = Field(default="gpt-4o-mini")
	openai_max_tokens: int = Field(default=4096)

	# Anthropic
	anthropic_api_key: str = Field(default="", description="Anthropic API key")
	anthropic_base_url: str = Field(default="https://api.anthropic.com")
	anthropic_thinking_model: str = Field(default="claude-3-5-sonnet-latest")
	anthropic_task_model: str = Field(default="claude-3-5-sonnet-latest")
	anthropic_max_tokens: int = Field(default=4096)

	# Google Gemini
	gemini_api_key: str = Field(default="", description="Google Gemini API key")
	gemini_base_url: str = Field(default="https://generativelanguage.googleapis.com")
	gemini_thinking_model: str = Field(default="gemini-1.5-pro-latest")
	gemini_task_model: str = Field(default="gemini-1.5-pro-latest")
	gemini_max_tokens: int = Field(default=4096)

	# Mistral
	mistral_api_key: str = Field(default="", description="Mistral API key")
	mistral_base_url: str = Field(default="https://api.mistral.ai/v1")
	mistral_thinking_model: str = Field(default="mistral-large-latest")
	mistral_task_model: str = Field(default="mistral-large-latest")
	mistral_max_tokens: int = Field(default=4096)

	# Groq
	groq_api_key: str = Field(default="", description="Groq API key")
	groq_base_url: str = Field(default="https://api.groq.com/openai/v1")
	groq_thinking_model: str = Field(default="llama-3.1-70b-versatile")
	groq_task_model: str = Field(default="llama-3.1-70b-versatile")
	groq_max_tokens: int = Field(default=4096)

	# LMStudio (OpenAI-compatible local server)
	lmstudio_base_url: str = Field(default="http://localhost:1234/v1", description="LMStudio API base (OpenAI-compatible)")
	lmstudio_thinking_model: str = Field(default="deepseek-r1:1.5b", description="Local reasoning model name")
	lmstudio_task_model: str = Field(default="llama3.1:8b", description="Local task model name")
	lmstudio_max_tokens: int = Field(default=2048, description="Max tokens for LMStudio completions")

	# SearxNG
	searxng_base_url: str = Field(default="http://192.168.1.142:55001")
	searxng_engine: str = Field(default="general")
	searxng_language: str = Field(default="en-US")
	searxng_results: int = Field(default=8)

	# DuckDuckGo
	duckduckgo_region: str = Field(default="us-en", description="DuckDuckGo region/language code (e.g., us-en, uk-en, de-de)")
	duckduckgo_results: int = Field(default=8, description="Number of search results to return")

	model_config = SettingsConfigDict(
		env_file=".env",
		case_sensitive=False,
		extra="ignore",
	)

	@field_validator("allowed_origins", mode="before")
	@classmethod
	def _split_origins(cls, v):
		# Accept multiple input formats for allowed_origins
		# - comma-separated string: "https://a.com,https://b.com"
		# - JSON array string: '["https://a.com"]'
		# - already a list
		if v is None:
			return ["*"]
		if isinstance(v, list):
			return v
		if isinstance(v, str):
			v = v.strip()
			if not v:
				return ["*"]
			# try JSON-style list first
			if v.startswith("[") and v.endswith("]"):
				try:
					import json
					parsed = json.loads(v)
					if isinstance(parsed, list):
						return parsed
				except Exception:
					# fall back to comma split
					pass
			# comma-separated fallback
			return [s.strip() for s in v.split(",") if s.strip()]
		# anything else - coerce to string
		return [str(v)]


@lru_cache()
def get_settings() -> Settings:
	# Try to load settings normally; if the .env contains malformed complex
	# values (common with list-like fields) pydantic-settings may raise when
	# decoding. In that case, warn and retry without the env file so the app
	# can still start with defaults.
	try:
		return Settings()
	except Exception as e:
		print("Warning: failed to load .env settings — falling back to defaults.\nError: %s" % (e,), file=sys.stderr)
		# Retry ignoring the env file
		try:
			return Settings(_env_file=None)
		except Exception as e2:
			# If we still can't load, re-raise the original error to help debugging
			raise


settings = get_settings()

