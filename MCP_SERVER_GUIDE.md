# OpenResearch MCP Server Configuration

This guide explains how to use OpenResearch as an MCP (Model Context Protocol) server, allowing Claude Desktop and other MCP-compatible clients to perform deep research.

## What is MCP?

MCP (Model Context Protocol) is a standard that allows AI assistants like Claude to connect to external tools and data sources. By running OpenResearch as an MCP server, you can give Claude the ability to conduct comprehensive web research with citations.

## Installation

1. **Install MCP Dependencies**
   ```bash
   cd backend
   pip install httpx mcp
   ```

2. **Ensure Backend is Running**
   ```bash
   # Start the FastAPI backend (if not already running)
   uvicorn app.main:app --host 0.0.0.0 --port 8081
   ```

## Configuration for Claude Desktop

### Option 1: Default Setup (Backend on localhost:8081)

Add this to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\Desktop\\deep reaserch\\backend\\mcp_server.py"
      ]
    }
  }
}
```

### Option 2: Custom Backend URL

If your backend runs on a different host/port, set the environment variable:

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\Desktop\\deep reaserch\\backend\\mcp_server.py"
      ],
      "env": {
        "OPENRESEARCH_API_URL": "http://192.168.1.100:8081"
      }
    }
  }
}
```

## Available Tools

Once configured, Claude Desktop will have access to these tools:

### 1. `research`
Conduct comprehensive AI-powered research on any topic.

**Parameters:**
- `topic` (required): The research topic or question
- `depth` (optional): Research depth - "surface", "standard", or "deep"

**Example:**
```
Can you research the latest developments in quantum computing?
```

**Interactive Workflow:**
When you start a research task, the system may ask clarifying questions to better understand your requirements. For example:
- What time period should the research cover?
- What types of sources are preferred (academic, news, industry)?
- What specific aspects to focus on?

Claude will present these questions to you, and you can provide answers. The research will then continue with your input.

### 2. `get_research_status`
Check the status of an ongoing research task.

**Parameters:**
- `task_id` (required): Task ID from a research request

**Usage:**
This tool is useful for checking on long-running research tasks, or if you need to retrieve results later.

### 3. `answer_clarifying_questions`
Provide answers to clarifying questions for an ongoing research task.

**Parameters:**
- `task_id` (required): The task ID of the research needing clarification
- `answers` (required): Array of answers in the same order as the questions

**Example:**
When research asks clarifying questions, Claude will show them to you and collect your answers. You don't need to call this tool directly - Claude will handle it automatically after you provide your responses.

## How It Works

1. Claude Desktop connects to the MCP server via stdio
2. When you ask Claude to research something, it calls the `research` tool
3. The MCP server communicates with your OpenResearch FastAPI backend
4. If the system needs clarification, Claude will ask you questions and wait for your answers
5. After clarification (if needed), the backend performs web searches and analyzes results
6. The MCP server polls for progress and handles query confirmations automatically
7. Claude receives the complete research report with citations

**Interactive Flow:**
```
You: "Research quantum computing advances"
   ↓
Claude calls research tool
   ↓
System asks: "What time period? What types of sources?"
   ↓
Claude presents questions to you
   ↓
You: "Last 2 years, focus on academic papers"
   ↓
Claude submits answers via answer_clarifying_questions
   ↓
Research continues automatically
   ↓
Complete report delivered
```

## Testing the MCP Server

You can test the MCP server directly:

```bash
cd backend
python mcp_server.py
```

The server will wait for JSON-RPC messages on stdin. For proper testing, use Claude Desktop or an MCP client.

## Troubleshooting

### "Connection refused"
- Ensure your FastAPI backend is running on the configured port
- Check the `OPENRESEARCH_API_URL` environment variable

### "Module not found: mcp"
```bash
pip install mcp httpx
```

### Claude Desktop doesn't show the tools
- Restart Claude Desktop after updating the config
- Check Claude Desktop logs for MCP server errors
- Verify the Python path in your configuration is correct

### Research times out
- Increase the timeout in `mcp_server.py` (default: 10 minutes)
- Check your search provider (SearxNG/DuckDuckGo) is accessible
- Verify your LLM provider credentials are configured

## Advanced Usage

### Using with Other MCP Clients

The MCP server works with any MCP-compatible client. Just ensure:
1. The FastAPI backend is running
2. The client can execute the Python script
3. The `OPENRESEARCH_API_URL` points to your backend

### Customizing Auto-Responses

The MCP server automatically answers clarifying questions and approves search queries. To customize this behavior, edit the `handle_research()` function in `mcp_server.py`:

```python
# Around line 155 - modify how clarifications are answered
if status == "awaiting_clarification":
    # Your custom logic here
    answers = []
    for q in questions:
        # Custom answer logic
        answers.append("Your custom answer")
```

## Security Notes

- The MCP server connects to your local FastAPI backend
- All API keys and credentials are stored in the backend's `.env` file
- The MCP server does not expose your API keys to Claude Desktop
- Research is performed server-side with full access control

## Example Prompts for Claude

Once configured, try these with Claude:

- "Research the top 10 fastest growing startups in 2025"
- "Do a deep research on recent breakthroughs in AI safety"
- "Give me a comprehensive overview of the current state of renewable energy technology"
- "Research recent academic papers on neural network architectures"

Claude will use the OpenResearch MCP tool to perform comprehensive research and provide detailed reports with citations!
