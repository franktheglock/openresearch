# OpenResearch MCP Server - Troubleshooting & Quick Start

## Problem You Encountered

**Error:** "Research failed: Unknown error"

**Root Cause:** The LLM provider was set to `openrouter` but no API key was configured.

## Solution

### Option 1: Use Ollama (Local, No API Key Needed)

1. **Make sure backend is running:**
   ```bash
   cd backend
   start.bat
   ```

2. **Configure to use Ollama:**
   ```bash
   python fix_config.py
   ```

   Or use Claude Desktop with the MCP tool:
   ```
   Use configure_research_settings with llm_provider="ollama"
   ```

### Option 2: Add OpenRouter API Key

1. Get an API key from https://openrouter.ai/
2. Edit `backend/.env`:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   ```
3. Restart the backend

## Updated MCP Server Features

The MCP server now has better error handling and debugging:

### New Tool: `get_research_settings`
Check current configuration to diagnose issues:
```
Ask Claude: "What are my current research settings?"
```

This will show:
- Active LLM provider
- Whether API keys are configured
- Search provider settings
- Connection URLs

### Improved Error Messages
The MCP server now shows detailed error information including:
- Actual error message (not just "Unknown error")
- Debug prompts and responses when available
- Connection troubleshooting hints

### Better Logging
The MCP server prints progress to console:
```
[MCP] Started research task abc-123 for topic: quantum computing
[MCP] Attempt 1: Status=clarifying, Message=Asking clarifying questions
[MCP] Handling 2 clarifying questions
[MCP] Submitting answers: ['Not specified', 'Not specified']
[MCP] Attempt 6: Status=searching, Message=Executing web searches
[MCP] Auto-approving 4 search queries
[MCP]   1. quantum computing 2025 breakthroughs
[MCP]   2. quantum computing practical applications
...
```

## Complete Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install httpx mcp
```

### 2. Configure Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "python",
      "args": [
        "C:\\Users\\claym\\Desktop\\deep reaserch\\backend\\mcp_server.py"
      ],
      "env": {
        "OPENRESEARCH_API_URL": "http://localhost:8081"
      }
    }
  }
}
```

**Important:** Update the path to match your actual installation directory!

### 3. Start Backend
```bash
cd backend
start.bat
```

### 4. Configure Provider (Choose One)

**Option A: Ollama (Recommended - No API Key)**
```bash
python fix_config.py
```

**Option B: Via Claude Desktop**
```
Ask Claude: "Configure research to use ollama as the LLM provider"
```

**Option C: Web UI**
- Open http://localhost:8081 (use the frontend)
- Click Settings
- Change LLM Provider to "ollama"
- Click Save

### 5. Restart Claude Desktop

### 6. Test!
```
Ask Claude: "Research the latest developments in quantum computing"
```

## Available MCP Tools

1. **research**
   - Conduct comprehensive research
   - Parameters: `topic`, `depth` (surface/standard/deep)

2. **get_research_status**
   - Check status of ongoing research
   - Parameters: `task_id`

3. **configure_research_settings**
   - Change LLM or search provider
   - Parameters: `llm_provider`, `search_provider`, URLs

4. **get_research_settings** ⭐ NEW
   - View current configuration
   - No parameters needed
   - Great for troubleshooting

## Common Issues

### "OpenRouter API key is required"
**Fix:** Switch to Ollama (free, local) or add OpenRouter API key

```bash
python fix_config.py
```

### "Connection refused"
**Fix:** Make sure backend is running

```bash
cd backend
start.bat
```

### "Research timed out"
**Fix:** Check that:
- Ollama is running (if using Ollama)
- SearxNG/DuckDuckGo is accessible
- LLM models are downloaded

### MCP server not appearing in Claude
**Fix:** 
1. Check Claude config path matches your installation
2. Restart Claude Desktop completely
3. Check Claude logs: `%APPDATA%\Claude\logs`

## Testing Without Claude Desktop

You can test the backend API directly:

```python
import requests

# Start research
r = requests.post("http://localhost:8081/api/research/start", json={
    "topic": "quantum computing",
    "depth": "standard"
})
task_id = r.json()["task_id"]

# Check status
r = requests.get(f"http://localhost:8081/api/research/{task_id}")
print(r.json())
```

## Next Steps

1. Ensure backend is running
2. Run `fix_config.py` to set Ollama
3. Restart Claude Desktop
4. Ask Claude: "What are my current research settings?"
5. If it shows Ollama, try: "Research quantum computing breakthroughs in 2025"

---

**Made with ❤️ for researchers using Claude Desktop**
