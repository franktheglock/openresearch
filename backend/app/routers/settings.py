from fastapi import APIRouter, HTTPException
import requests
from typing import Optional

from ..config import settings
from ..models.settings import SettingsResponse, SettingsUpdate, OllamaModelsResponse
from ..services.ollama_service import ollama
from ..services.openrouter_service import openrouter
from ..services.openai_service import openai_client
from ..services.anthropic_service import anthropic
from ..services.gemini_service import gemini
from ..services.mistral_service import mistral
from ..services.groq_service import groq
from ..services.lmstudio_service import lmstudio_client

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings():
    return SettingsResponse(
        llm_provider=settings.llm_provider,
        search_provider=settings.search_provider,
        ollama_base_url=settings.ollama_base_url,
        ollama_thinking_model=settings.ollama_thinking_model,
        ollama_task_model=settings.ollama_task_model,
        openrouter_api_key=settings.openrouter_api_key,
        openrouter_thinking_model=settings.openrouter_thinking_model,
        openrouter_task_model=settings.openrouter_task_model,
        openrouter_max_tokens=settings.openrouter_max_tokens,
        # OpenAI
        openai_api_key=settings.openai_api_key,
        openai_base_url=settings.openai_base_url,
        openai_thinking_model=settings.openai_thinking_model,
        openai_task_model=settings.openai_task_model,
        openai_max_tokens=settings.openai_max_tokens,
        # Anthropic
        anthropic_api_key=settings.anthropic_api_key,
        anthropic_base_url=settings.anthropic_base_url,
        anthropic_thinking_model=settings.anthropic_thinking_model,
        anthropic_task_model=settings.anthropic_task_model,
        anthropic_max_tokens=settings.anthropic_max_tokens,
        # Gemini
        gemini_api_key=settings.gemini_api_key,
        gemini_base_url=settings.gemini_base_url,
        gemini_thinking_model=settings.gemini_thinking_model,
        gemini_task_model=settings.gemini_task_model,
        gemini_max_tokens=settings.gemini_max_tokens,
        # Mistral
        mistral_api_key=settings.mistral_api_key,
        mistral_base_url=settings.mistral_base_url,
        mistral_thinking_model=settings.mistral_thinking_model,
        mistral_task_model=settings.mistral_task_model,
        mistral_max_tokens=settings.mistral_max_tokens,
        # Groq
        groq_api_key=settings.groq_api_key,
        groq_base_url=settings.groq_base_url,
        groq_thinking_model=settings.groq_thinking_model,
        groq_task_model=settings.groq_task_model,
        groq_max_tokens=settings.groq_max_tokens,
        lmstudio_base_url=settings.lmstudio_base_url,
        lmstudio_thinking_model=settings.lmstudio_thinking_model,
        lmstudio_task_model=settings.lmstudio_task_model,
        lmstudio_max_tokens=settings.lmstudio_max_tokens,
        searxng_base_url=settings.searxng_base_url,
        searxng_language=settings.searxng_language,
        searxng_results=settings.searxng_results,
        duckduckgo_region=settings.duckduckgo_region,
        duckduckgo_results=settings.duckduckgo_results,
    )


@router.post("")
def update_settings(update: SettingsUpdate):
    # In a real app, you'd persist these to a database or config file
    # For now, we'll update the settings object directly (note: this won't persist across restarts)
    if update.llm_provider is not None:
        settings.llm_provider = update.llm_provider
    if update.search_provider is not None:
        settings.search_provider = update.search_provider
    if update.ollama_base_url is not None:
        settings.ollama_base_url = update.ollama_base_url
        ollama.base_url = update.ollama_base_url.rstrip("/")
    if update.ollama_thinking_model is not None:
        settings.ollama_thinking_model = update.ollama_thinking_model
        ollama.thinking_model = update.ollama_thinking_model
    if update.ollama_task_model is not None:
        settings.ollama_task_model = update.ollama_task_model
        ollama.task_model = update.ollama_task_model
    if update.openrouter_api_key is not None:
        settings.openrouter_api_key = update.openrouter_api_key
        openrouter.api_key = update.openrouter_api_key
    if update.openrouter_thinking_model is not None:
        settings.openrouter_thinking_model = update.openrouter_thinking_model
        openrouter.thinking_model = update.openrouter_thinking_model
    if update.openrouter_task_model is not None:
        settings.openrouter_task_model = update.openrouter_task_model
        openrouter.task_model = update.openrouter_task_model
    if update.openrouter_max_tokens is not None:
        settings.openrouter_max_tokens = update.openrouter_max_tokens
        openrouter.max_tokens = update.openrouter_max_tokens

    # OpenAI
    if update.openai_api_key is not None:
        settings.openai_api_key = update.openai_api_key
        openai_client.api_key = update.openai_api_key
    if update.openai_base_url is not None:
        settings.openai_base_url = update.openai_base_url
        openai_client.base_url = update.openai_base_url.rstrip('/')
    if update.openai_thinking_model is not None:
        settings.openai_thinking_model = update.openai_thinking_model
        openai_client.thinking_model = update.openai_thinking_model
    if update.openai_task_model is not None:
        settings.openai_task_model = update.openai_task_model
        openai_client.task_model = update.openai_task_model
    if update.openai_max_tokens is not None:
        settings.openai_max_tokens = update.openai_max_tokens
        openai_client.max_tokens = update.openai_max_tokens

    # Anthropic
    if update.anthropic_api_key is not None:
        settings.anthropic_api_key = update.anthropic_api_key
        anthropic.api_key = update.anthropic_api_key
    if update.anthropic_base_url is not None:
        settings.anthropic_base_url = update.anthropic_base_url
        anthropic.base_url = update.anthropic_base_url.rstrip('/')
    if update.anthropic_thinking_model is not None:
        settings.anthropic_thinking_model = update.anthropic_thinking_model
        anthropic.thinking_model = update.anthropic_thinking_model
    if update.anthropic_task_model is not None:
        settings.anthropic_task_model = update.anthropic_task_model
        anthropic.task_model = update.anthropic_task_model
    if update.anthropic_max_tokens is not None:
        settings.anthropic_max_tokens = update.anthropic_max_tokens
        anthropic.max_tokens = update.anthropic_max_tokens

    # Gemini
    if update.gemini_api_key is not None:
        settings.gemini_api_key = update.gemini_api_key
        gemini.api_key = update.gemini_api_key
    if update.gemini_base_url is not None:
        settings.gemini_base_url = update.gemini_base_url
        gemini.base_url = update.gemini_base_url.rstrip('/')
    if update.gemini_thinking_model is not None:
        settings.gemini_thinking_model = update.gemini_thinking_model
        gemini.thinking_model = update.gemini_thinking_model
    if update.gemini_task_model is not None:
        settings.gemini_task_model = update.gemini_task_model
        gemini.task_model = update.gemini_task_model
    if update.gemini_max_tokens is not None:
        settings.gemini_max_tokens = update.gemini_max_tokens
        gemini.max_tokens = update.gemini_max_tokens

    # Mistral
    if update.mistral_api_key is not None:
        settings.mistral_api_key = update.mistral_api_key
        mistral.api_key = update.mistral_api_key
    if update.mistral_base_url is not None:
        settings.mistral_base_url = update.mistral_base_url
        mistral.base_url = update.mistral_base_url.rstrip('/')
    if update.mistral_thinking_model is not None:
        settings.mistral_thinking_model = update.mistral_thinking_model
        mistral.thinking_model = update.mistral_thinking_model
    if update.mistral_task_model is not None:
        settings.mistral_task_model = update.mistral_task_model
        mistral.task_model = update.mistral_task_model
    if update.mistral_max_tokens is not None:
        settings.mistral_max_tokens = update.mistral_max_tokens
        mistral.max_tokens = update.mistral_max_tokens

    # Groq
    if update.groq_api_key is not None:
        settings.groq_api_key = update.groq_api_key
        groq.api_key = update.groq_api_key
    if update.groq_base_url is not None:
        settings.groq_base_url = update.groq_base_url
        groq.base_url = update.groq_base_url.rstrip('/')
    if update.groq_thinking_model is not None:
        settings.groq_thinking_model = update.groq_thinking_model
        groq.thinking_model = update.groq_thinking_model
    if update.groq_task_model is not None:
        settings.groq_task_model = update.groq_task_model
        groq.task_model = update.groq_task_model
    if update.groq_max_tokens is not None:
        settings.groq_max_tokens = update.groq_max_tokens
        groq.max_tokens = update.groq_max_tokens
    # LMStudio
    if update.lmstudio_base_url is not None:
        settings.lmstudio_base_url = update.lmstudio_base_url
        lmstudio_client.base_url = update.lmstudio_base_url
    if update.lmstudio_thinking_model is not None:
        settings.lmstudio_thinking_model = update.lmstudio_thinking_model
        lmstudio_client.thinking_model = update.lmstudio_thinking_model
    if update.lmstudio_task_model is not None:
        settings.lmstudio_task_model = update.lmstudio_task_model
        lmstudio_client.task_model = update.lmstudio_task_model
    if update.lmstudio_max_tokens is not None:
        settings.lmstudio_max_tokens = update.lmstudio_max_tokens
        lmstudio_client.max_tokens = update.lmstudio_max_tokens
    if update.searxng_base_url is not None:
        settings.searxng_base_url = update.searxng_base_url
    if update.searxng_language is not None:
        settings.searxng_language = update.searxng_language
    if update.searxng_results is not None:
        settings.searxng_results = update.searxng_results
    if update.duckduckgo_region is not None:
        settings.duckduckgo_region = update.duckduckgo_region
    if update.duckduckgo_results is not None:
        settings.duckduckgo_results = update.duckduckgo_results
    
    return {"message": "Settings updated"}


@router.get("/ollama/models", response_model=OllamaModelsResponse)
def get_ollama_models():
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        models = [model["name"] for model in data.get("models", [])]
        return OllamaModelsResponse(models=models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.get("/openrouter/models", response_model=OllamaModelsResponse)
def get_openrouter_models():
    try:
        models = openrouter.get_models()
        return OllamaModelsResponse(models=models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch OpenRouter models: {str(e)}")


@router.get("/lmstudio/models", response_model=OllamaModelsResponse)
def get_lmstudio_models(force_refresh: Optional[bool] = False):
    try:
        models = lmstudio_client.list_models(force_refresh=force_refresh or False)
        return OllamaModelsResponse(models=models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch LMStudio models: {str(e)}")