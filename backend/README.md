# Deep Research App - Backend# Deep Research App - Backend



FastAPI backend for the Deep Research App. This directory contains the Python server that handles LLM interactions, search integration, and research orchestration.FastAPI backend for the Deep Research App. This directory contains the Python server that handles LLM interactions, search integration, and research orchestration.



## Quick Start## Quick Start



### Windows (One-click)### Windows (One-click)

```bash```bash

start.batstart.bat

``````



### Manual Setup### Manual Setup

```bash```bash

# Install dependencies# Install dependencies

pip install -r requirements.txtpip install -r requirements.txt



# Start server# Start server

uvicorn app.main:app --host 0.0.0.0 --port 8081 --reloaduvicorn app.main:app --host 0.0.0.0 --port 8081 --reload

``````



## Configuration## Configuration



See the main [README.md](../README.md) for detailed configuration instructions.See the main [README.md](../README.md) for detailed configuration instructions.



## API Documentation## API Documentation



Once running, visit `http://localhost:8081/docs` for interactive API documentation.Once running, visit `http://localhost:8081/docs` for interactive API documentation.



## Development## Development



### Project Structure### Project Structure

``````

backend/backend/

├── app/├── app/

│   ├── config.py          # Settings & environment variables│   ├── config.py          # Settings & environment variables

│   ├── main.py           # FastAPI application│   ├── main.py           # FastAPI application

│   ├── models/           # Pydantic data models│   ├── models/           # Pydantic data models

│   ├── routers/          # API endpoints│   ├── routers/          # API endpoints

│   └── services/         # LLM & search service integrations│   └── services/         # LLM & search service integrations

├── requirements.txt      # Python dependencies├── requirements.txt      # Python dependencies

├── .env.example         # Environment template├── .env.example         # Environment template

└── start.bat           # Windows startup script└── start.bat           # Windows startup script

``````



### Adding New Providers### Adding New Providers



1. Create service in `app/services/`1. Create service in `app/services/`

2. Add config fields in `app/config.py`2. Add config fields in `app/config.py`

3. Update models in `app/models/settings.py`3. Update models in `app/models/settings.py`

4. Add router endpoints in `app/routers/settings.py`4. Add router endpoints in `app/routers/settings.py`

5. Update frontend UI in `../frontend/index.html`5. Update frontend UI in `../frontend/index.html`



## Dependencies## Dependencies



- **FastAPI**: Web framework- **FastAPI**: Web framework

- **Pydantic**: Data validation- **Pydantic**: Data validation

- **Requests**: HTTP client- **Requests**: HTTP client

- **BeautifulSoup4**: HTML parsing (for DuckDuckGo)- **BeautifulSoup4**: HTML parsing (for DuckDuckGo)

- **Uvicorn**: ASGI server- **Uvicorn**: ASGI server



---## Requirements



*For complete setup instructions, configuration details, and troubleshooting, see the main [README.md](../README.md)*- Python 3.10+
- At least one LLM provider configured (see below)
- SearxNG instance accessible (optional, for web search)

## Supported LLM Providers

### Local Providers
- **Ollama**: Requires Ollama running locally with models like `deepseek-r1` and `llama3.1`
- **LMStudio**: Local OpenAI-compatible server

### Cloud Providers
- **OpenRouter**: Unified API for multiple models
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **Google Gemini**: Gemini models
- **Mistral**: Mistral models
- **Groq**: Fast inference with Llama models

## Setup

### 1. Clone and Install

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**IMPORTANT**: Never commit API keys to version control!

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys for desired providers:

   ```bash
   # Choose your primary provider
   LLM_PROVIDER=openrouter  # or ollama, openai, anthropic, etc.

   # Add API keys for cloud providers you want to use
   OPENROUTER_API_KEY=your_openrouter_key_here
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   # ... etc for other providers
   ```

3. For local providers:
   - **Ollama**: Ensure Ollama is running with required models
   - **LMStudio**: Start LMStudio server on default port 1234

### 3. Start the Server

#### Option A: Using the batch file (Windows)
```bash
start_backend.bat
```

#### Option B: Manual start
```bash
# From backend directory
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

### 4. Open the Frontend

Open `frontend/index.html` in your browser. The app will connect to the backend automatically.

## Configuration Details

### Provider Selection
Set `LLM_PROVIDER` in `.env` to your preferred provider:
- `ollama` (local)
- `openrouter` (cloud)
- `openai` (cloud)
- `anthropic` (cloud)
- `gemini` (cloud)
- `mistral` (cloud)
- `groq` (cloud)
- `lmstudio` (local)

### Model Configuration
Each provider has separate models for "thinking" (planning/clarifying) and "task" (writing/reporting):

```bash
# Example for OpenAI
OPENAI_THINKING_MODEL=gpt-4o-mini
OPENAI_TASK_MODEL=gpt-4o-mini
```

### SearxNG Search (Optional)
Configure web search:

```bash
SEARXNG_BASE_URL=http://your-searxng-instance:port
SEARXNG_ENGINE=general
SEARXNG_LANGUAGE=en-US
SEARXNG_RESULTS=8
```

## API Endpoints

- `POST /api/research/start` - Start research task
- `GET /api/research/{task_id}` - Get research progress/results
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings at runtime

## Security Notes

- `.env` files are ignored by git (see `.gitignore`)
- API keys are loaded from environment variables only
- Never commit `.env` or any files containing real API keys
- The app includes fallback logic if `.env` is malformed

## Troubleshooting

- **"Failed to load .env settings"**: Check `.env` syntax, especially list-like values
- **Provider errors**: Verify API keys and model names in `.env`
- **Connection issues**: Check base URLs and network access
- **Port conflicts**: The batch file auto-selects free ports starting from 8081
