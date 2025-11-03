from pydantic import BaseModel
from typing import List


class SettingsResponse(BaseModel):
    llm_provider: str
    search_provider: str
    ollama_base_url: str
    ollama_thinking_model: str
    ollama_task_model: str
    openrouter_api_key: str
    openrouter_thinking_model: str
    openrouter_task_model: str
    openrouter_max_tokens: int
    # Additional providers
    openai_api_key: str
    openai_base_url: str
    openai_thinking_model: str
    openai_task_model: str
    openai_max_tokens: int
    anthropic_api_key: str
    anthropic_base_url: str
    anthropic_thinking_model: str
    anthropic_task_model: str
    anthropic_max_tokens: int
    gemini_api_key: str
    gemini_base_url: str
    gemini_thinking_model: str
    gemini_task_model: str
    gemini_max_tokens: int
    mistral_api_key: str
    mistral_base_url: str
    mistral_thinking_model: str
    mistral_task_model: str
    mistral_max_tokens: int
    groq_api_key: str
    groq_base_url: str
    groq_thinking_model: str
    groq_task_model: str
    groq_max_tokens: int
    lmstudio_base_url: str
    lmstudio_thinking_model: str
    lmstudio_task_model: str
    lmstudio_max_tokens: int
    searxng_base_url: str
    searxng_language: str
    searxng_results: int
    duckduckgo_region: str
    duckduckgo_results: int


class SettingsUpdate(BaseModel):
    llm_provider: str = None
    search_provider: str = None
    ollama_base_url: str = None
    ollama_thinking_model: str = None
    ollama_task_model: str = None
    openrouter_api_key: str = None
    openrouter_thinking_model: str = None
    openrouter_task_model: str = None
    openrouter_max_tokens: int = None
    openai_api_key: str = None
    openai_base_url: str = None
    openai_thinking_model: str = None
    openai_task_model: str = None
    openai_max_tokens: int = None
    anthropic_api_key: str = None
    anthropic_base_url: str = None
    anthropic_thinking_model: str = None
    anthropic_task_model: str = None
    anthropic_max_tokens: int = None
    gemini_api_key: str = None
    gemini_base_url: str = None
    gemini_thinking_model: str = None
    gemini_task_model: str = None
    gemini_max_tokens: int = None
    mistral_api_key: str = None
    mistral_base_url: str = None
    mistral_thinking_model: str = None
    mistral_task_model: str = None
    mistral_max_tokens: int = None
    groq_api_key: str = None
    groq_base_url: str = None
    groq_thinking_model: str = None
    groq_task_model: str = None
    groq_max_tokens: int = None
    lmstudio_base_url: str = None
    lmstudio_thinking_model: str = None
    lmstudio_task_model: str = None
    lmstudio_max_tokens: int = None
    searxng_base_url: str = None
    searxng_language: str = None
    searxng_results: int = None
    duckduckgo_region: str = None
    duckduckgo_results: int = None


class OllamaModelsResponse(BaseModel):
    models: List[str]