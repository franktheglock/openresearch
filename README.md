# OpenResearch

A comprehensive AI-powered research assistant that combines multiple LLM providers with web search capabilities. Generate detailed research reports with intelligent question clarification, search planning, and multi-format export.

![OpenResearch](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🤖 Multiple LLM Providers
- **Ollama** (Local models)
- **OpenRouter** (Unified API access)
- **OpenAI** (GPT models)
- **Anthropic** (Claude models)
- **Google Gemini** (Gemini models)
- **Mistral** (Mistral models)
- **Groq** (Fast inference)
- **LMStudio** (Local OpenAI-compatible)

### 🔍 Web Search Integration
- **SearxNG** (Privacy-focused search)
- **DuckDuckGo** (No API key required)

### 🧠 Intelligent Research Flow
- **Clarifying Questions**: Context-aware questions based on research topic
- **Search Planning**: AI-generated search queries with rationale
- **Query Confirmation**: Review and edit search queries before execution
- **Report Generation**: Comprehensive Markdown reports with sources

### 📊 Export Options
- **Markdown** (.md)
- **HTML** (.html)
- **PDF** (.pdf)

### 🎨 Modern UI
- Clean, responsive interface
- Dark theme with modern styling
- Real-time progress updates
- Debug panel for development

### 🔌 MCP Server Support
- **Claude Desktop Integration**: Use as a research tool in Claude
- **Tool Calling**: Expose research capabilities to other LLMs
- **Automated Workflow**: Auto-handles clarifications and confirmations
- **Async Operations**: Non-blocking research with status polling

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### One-Click Setup (Windows)
```bash
# Clone the repository
git clone https://github.com/franktheglock/openresearch.git
cd openresearch

# Run the complete setup script
backend\start.bat
```

This will:
- Create a virtual environment
- Install all dependencies
- Start the backend server
- Open your browser to the application

### Manual Setup

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys (see Configuration section below)
```

#### 3. Start the Backend
```bash
# Windows
start_backend.bat

# Linux/Mac
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

#### 4. Open Frontend
Simply open `frontend/index.html` in your web browser.

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the `backend/` directory:

```bash
# LLM Provider Selection
LLM_PROVIDER=openrouter

# OpenRouter (https://openrouter.ai/)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_THINKING_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_TASK_MODEL=anthropic/claude-3.5-sonnet

# OpenAI (https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_THINKING_MODEL=gpt-4o-mini
OPENAI_TASK_MODEL=gpt-4o-mini

# Anthropic (https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_THINKING_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_TASK_MODEL=claude-3-5-sonnet-latest

# Google Gemini (https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_THINKING_MODEL=gemini-1.5-pro-latest
GEMINI_TASK_MODEL=gemini-1.5-pro-latest

# Mistral (https://console.mistral.ai/)
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_THINKING_MODEL=mistral-large-latest
MISTRAL_TASK_MODEL=mistral-large-latest

# Groq (https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
GROQ_THINKING_MODEL=llama-3.1-70b-versatile
GROQ_TASK_MODEL=llama-3.1-70b-versatile

# LMStudio (local server at http://localhost:1234/v1)
LMSTUDIO_THINKING_MODEL=deepseek-r1:1.5b
LMSTUDIO_TASK_MODEL=llama3.1:8b

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_THINKING_MODEL=deepseek-r1:1.5b
OLLAMA_TASK_MODEL=llama3.1:8b

# Search Provider
SEARCH_PROVIDER=searxng

# SearxNG
SEARXNG_BASE_URL=http://192.168.1.142:55001
SEARXNG_LANGUAGE=en-US
SEARXNG_RESULTS=8

# DuckDuckGo (no API key needed)
DUCKDUCKGO_REGION=us-en
DUCKDUCKGO_RESULTS=8

# CORS
ALLOWED_ORIGINS=http://localhost:8081,http://127.0.0.1:8081
```

### Local LLM Setup

#### Ollama
```bash
# Install Ollama from https://ollama.ai/
ollama pull deepseek-r1:1.5b
ollama pull llama3.1:8b
```

#### LMStudio
1. Download from https://lmstudio.ai/
2. Start local server on port 1234
3. Load your preferred models

### Search Setup

#### SearxNG
```bash
# Install SearxNG (Docker recommended)
docker run -d -p 8080:8080 searxng/searxng
```

#### DuckDuckGo
No setup required - works out of the box!

## 📖 Usage

### Web Interface

1. **Enter Research Topic**: Type your research question or topic
2. **Select Depth**: Choose research depth (brief/standard/deep)
3. **Answer Clarifying Questions**: The AI may ask context-specific questions
4. **Review Search Plan**: Edit or confirm the generated search queries
5. **View Results**: Read the comprehensive research report
6. **Export**: Download in Markdown, HTML, or PDF format

### MCP Server (Claude Desktop Integration)

OpenResearch can be used as an MCP (Model Context Protocol) server, allowing Claude Desktop and other MCP clients to perform deep research through tool calls.

**Quick Setup:**

1. Install MCP dependencies:
   ```bash
   pip install httpx mcp
   ```

2. Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "openresearch": {
         "command": "python",
         "args": ["C:\\path\\to\\openresearch\\backend\\mcp_server.py"]
       }
     }
   }
   ```

3. Restart Claude Desktop and ask it to research topics!

See [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md) for detailed MCP server documentation.

## 🔌 API / MCP Integration

Every feature is also exposed over HTTP so other apps or MCP tools can orchestrate deep research workflows:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/research/start` | `POST` | Launches a new async task. Returns `task_id` plus current progress payload (including clarifying prompts if already available). |
| `/api/research/run` | `POST` | Same payload as `/start`, but optionally blocks until the task finishes (set `wait_for_completion`, `poll_interval_seconds`, and `timeout_seconds`). |
| `/api/research/{task_id}` | `GET` | Poll current status. Response includes flags like `awaiting_clarification`, `awaiting_confirmation`, intermediate steps, and final markdown when done. |
| `/api/research/{task_id}/clarify` | `POST` | Submit answers to outstanding clarifying questions. |
| `/api/research/{task_id}/confirm` | `POST` | Approve or edit the generated search plan. |
| `/api/research/{task_id}` | `DELETE` | Cancel a pending task (threads will wind down gracefully). |

### Request payloads

```jsonc
// POST /api/research/start
{
	"topic": "Spotify fastest songs to 1B streams",
	"depth": "deep",             // surface | standard | deep
	"metadata": { "request_id": "abc123" }
}

// POST /api/research/run
{
	"topic": "Frontier AI regulation",
	"depth": "standard",
	"wait_for_completion": true,
	"timeout_seconds": 420
}

// POST /api/research/{task_id}/clarify
{
	"answers": ["Focus on global legislation", "Timeframe 2023-2025"]
}

// POST /api/research/{task_id}/confirm
{
	"approved_queries": [
		{"query": "frontier ai regulation overview 2025", "rationale": "baseline"},
		{"query": "us eu ai act comparison 2024", "rationale": "regional delta"}
	]
}
```

### Sample MCP tool definition

```json
{
	"name": "openresearch",
	"description": "Multi-step deep research assistant",
	"input_schema": {
		"type": "object",
		"properties": {
			"topic": {"type": "string"},
			"depth": {"type": "string", "enum": ["surface", "standard", "deep"]},
			"wait_for_completion": {"type": "boolean", "default": true}
		},
		"required": ["topic"]
	},
	"http": {
		"endpoint": "http://localhost:8081/api/research/run",
		"method": "POST"
	}
}
```

Responses always echo the full `progress` object, so MCP callers can inspect `status`, pending questions, and final `report_markdown` without reaching into internal state.

## 🏗️ Architecture

```
openresearch/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── config.py       # Settings management
│   │   ├── main.py         # FastAPI app
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   └── services/       # LLM & search services
│   ├── requirements.txt    # Python dependencies
│   └── start.bat          # Windows startup script
├── frontend/               # Static HTML/CSS/JS
│   └── index.html         # Single-page application
└── README.md              # This file
```

### API Endpoints

- `POST /api/research/start` - Start research task
- `GET /api/research/{task_id}` - Get progress/results
- `POST /api/research/{task_id}/clarify` - Submit clarification answers
- `POST /api/research/{task_id}/confirm` - Confirm search queries
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

## 🔧 Development

### Backend Development
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

### Frontend Development
The frontend is a single HTML file. Edit `frontend/index.html` and refresh your browser.

### Adding New Providers

1. **Create Service**: Add new service in `backend/app/services/`
2. **Update Config**: Add settings in `config.py`
3. **Update Router**: Add settings endpoints in `routers/settings.py`
4. **Update Frontend**: Add UI controls in `frontend/index.html`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Security Notes

- Never commit `.env` files containing real API keys
- The app includes fallback logic for malformed environment files
- API keys are only loaded from environment variables
- Frontend uses password fields for sensitive inputs

## 🐛 Troubleshooting

### Common Issues

**"Failed to load .env settings"**
- Check `.env` file syntax, especially list values
- The app will fall back to defaults if parsing fails

**"Connection refused"**
- Ensure Ollama/LMStudio/SearxNG services are running
- Check base URLs in settings

**"No search results"**
- Verify search provider configuration
- Check network connectivity

**Port conflicts**
- The startup script auto-selects free ports
- Default: 8081, falls back to 8082-8181

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Ollama](https://ollama.ai/) - Local LLM runner
- [SearxNG](https://searxng.org/) - Privacy-respecting search engine
- [Marked.js](https://marked.js.org/) - Markdown parser
- [html2pdf.js](https://ekoopmans.github.io/html2pdf.js/) - PDF generation

---

**Made with ❤️ for researchers, students, and knowledge seekers**</content>
<parameter name="filePath">c:\Users\claym\Desktop\deep reaserch\README.md