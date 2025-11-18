"""
Quick fix script to configure OpenResearch to use Ollama (local LLM)
Run this before using the MCP server if you're getting API key errors.
"""
import requests

API_URL = "http://localhost:8082"

print("Configuring OpenResearch to use Ollama...")

response = requests.post(
    f"{API_URL}/api/settings",
    json={
        "llm_provider": "ollama",
        "search_provider": "searxng"
    }
)

if response.status_code == 200:
    print("✓ Successfully configured!")
    print("\nCurrent settings:")
    
    settings = requests.get(f"{API_URL}/api/settings").json()
    print(f"  LLM Provider: {settings['llm_provider']}")
    print(f"  Search Provider: {settings['search_provider']}")
    print(f"  Ollama URL: {settings['ollama_base_url']}")
    print(f"  SearxNG URL: {settings['searxng_base_url']}")
    print("\nYou can now use the MCP server!")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
