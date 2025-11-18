#!/usr/bin/env python3
"""
OpenResearch MCP Server

This MCP server exposes the OpenResearch API as tools that can be called by
Claude Desktop and other MCP-compatible clients for deep research capabilities.
"""

import asyncio
import json
import sys
from typing import Any, Sequence
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Default API base URL (can be configured via environment)
import os
API_BASE_URL = os.getenv("OPENRESEARCH_API_URL", "http://localhost:8081")

# Initialize MCP server
app = Server("openresearch")

# HTTP client for making requests to the FastAPI backend
http_client = httpx.AsyncClient(timeout=3000)  # 5 minute timeout for long research tasks


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available research tools.
    """
    return [
        Tool(
            name="research",
            description=(
                "Conduct comprehensive AI-powered research on any topic. "
                "This tool performs web searches, analyzes results, and generates "
                "detailed research reports with citations. Supports multiple search "
                "engines (SearxNG, DuckDuckGo) and can adjust research depth. "
                "Perfect for gathering information, fact-checking, exploring topics, "
                "and generating comprehensive reports with sources."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The research topic or question to investigate"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["surface", "standard", "deep"],
                        "description": (
                            "Research depth level:\n"
                            "- surface: Quick overview (2-3 sections, 3-4 queries)\n"
                            "- standard: Comprehensive coverage (4-6 sections, 4-5 queries)\n"
                            "- deep: In-depth analysis (6+ sections, 5-6 queries)"
                        ),
                        "default": "standard"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_research_status",
            description=(
                "Check the status of an ongoing research task. "
                "Returns current progress, status, and results when complete."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID returned from the research tool"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="answer_clarifying_questions",
            description=(
                "Provide answers to clarifying questions for an ongoing research task. "
                "Use this when the research tool returns clarifying questions that need user input."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID of the research needing clarification"
                    },
                    "answers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of answers corresponding to the clarifying questions in order"
                    }
                },
                "required": ["task_id", "answers"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    
    if name == "research":
        return await handle_research(arguments)
    elif name == "get_research_status":
        return await handle_get_status(arguments)
    elif name == "answer_clarifying_questions":
        return await handle_answer_clarifications(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_research(arguments: dict) -> Sequence[TextContent]:
    """
    Start a research task and wait for completion with clarifications.
    """
    topic = arguments.get("topic")
    depth = arguments.get("depth", "standard")
    
    if not topic:
        return [TextContent(type="text", text="Error: topic is required")]
    
    try:
        # Start research
        response = await http_client.post(
            f"{API_BASE_URL}/api/research/start",
            json={"topic": topic, "depth": depth}
        )
        response.raise_for_status()
        data = response.json()
        task_id = data.get("task_id")
        
        if not task_id:
            return [TextContent(type="text", text="Error: No task_id received")]
        
        # Poll for completion and handle clarifications
        max_attempts = 120  # 10 minutes max
        attempt = 0
        
        print(f"[MCP] Started research task {task_id} for topic: {topic}")
        
        while attempt < max_attempts:
            await asyncio.sleep(5)  # Poll every 5 seconds
            attempt += 1
            
            status_response = await http_client.get(f"{API_BASE_URL}/api/research/{task_id}")
            status_response.raise_for_status()
            response_data = status_response.json()
            
            # The API returns {task_id, status, progress: {...}}
            # The actual progress object is nested
            progress = response_data.get("progress", response_data)
            
            status = progress.get("status")
            message = progress.get("message", "")
            
            # Debug logging
            if attempt == 1 or attempt % 6 == 0:
                print(f"[MCP] Attempt {attempt}: Status={status}, Message={message}")
            
            # Handle awaiting clarification
            if status == "awaiting_clarification":
                clarifying_questions = progress.get("clarifying_questions", {})
                questions = clarifying_questions.get("questions", [])
                
                print(f"[MCP] Research needs clarification - returning questions to user")
                
                # Format questions for the user
                questions_text = "# Clarifying Questions Needed\n\n"
                questions_text += "The research system needs more information to proceed:\n\n"
                
                for i, q in enumerate(questions, 1):
                    question = q.get("question", "")
                    context = q.get("context", "")
                    q_type = q.get("type", "text")
                    options = q.get("options", [])
                    
                    questions_text += f"**Question {i}:** {question}\n"
                    if context:
                        questions_text += f"*Context: {context}*\n"
                    
                    if q_type == "multiple_choice" and options:
                        questions_text += f"Options: {', '.join(options)}\n"
                    
                    questions_text += "\n"
                
                questions_text += "\n---\n\n"
                questions_text += f"**Task ID:** `{task_id}`\n\n"
                questions_text += "To continue this research, please use the `answer_clarifying_questions` tool with:\n"
                questions_text += f"- task_id: `{task_id}`\n"
                questions_text += f"- answers: [your answers in order]\n\n"
                questions_text += "*Example:* If asked about timeframe and scope, provide answers like:\n"
                questions_text += '`["Last 5 years", "Academic and industry sources"]`'
                
                return [TextContent(
                    type="text",
                    text=questions_text
                )]
            
            # Handle awaiting confirmation
            if status == "awaiting_confirmation":
                plan = progress.get("plan", {})
                queries = plan.get("queries", [])
                
                print(f"[MCP] Auto-approving {len(queries)} search queries")
                for i, q in enumerate(queries, 1):
                    print(f"[MCP]   {i}. {q.get('query', 'Unknown query')}")
                
                # Auto-approve queries
                await http_client.post(
                    f"{API_BASE_URL}/api/research/{task_id}/confirm",
                    json={"approved_queries": queries}
                )
                continue
            
            # Check if done
            if status == "done":
                report = progress.get("report_markdown", "")
                if report:
                    return [TextContent(
                        type="text",
                        text=f"# Research Complete\n\n{report}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="Research completed but no report generated."
                    )]
            
            # Check for error
            if status == "error":
                message = progress.get("message", "Unknown error")
                debug_info = []
                
                # Gather debug information
                if progress.get("debug_plan_prompt"):
                    debug_info.append("\n### Planning Prompt\n" + progress["debug_plan_prompt"][:500])
                if progress.get("debug_plan_response"):
                    debug_info.append("\n### Planning Response\n" + progress["debug_plan_response"][:500])
                if progress.get("debug_clarifying_prompt"):
                    debug_info.append("\n### Clarifying Prompt\n" + progress["debug_clarifying_prompt"][:500])
                if progress.get("debug_clarifying_response"):
                    debug_info.append("\n### Clarifying Response\n" + progress["debug_clarifying_response"][:500])
                
                full_message = f"# Research Failed\n\n**Error:** {message}\n\n"
                if debug_info:
                    full_message += "## Debug Information\n" + "\n".join(debug_info)
                
                return [TextContent(
                    type="text",
                    text=full_message
                )]
            
            # Show progress for long-running tasks
            if attempt % 6 == 0:  # Every 30 seconds
                print(f"[MCP] Research status: {status} - {progress.get('message', '')}")
        
        return [TextContent(
            type="text",
            text=f"Research timed out after 10 minutes. Last status: {status}"
        )]
        
    except httpx.HTTPError as e:
        return [TextContent(
            type="text",
            text=f"HTTP Error connecting to OpenResearch backend at {API_BASE_URL}: {str(e)}\n\nMake sure the backend is running on the correct port."
        )]
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        )]


async def handle_get_status(arguments: dict) -> Sequence[TextContent]:
    """
    Get the status of a research task.
    """
    task_id = arguments.get("task_id")
    
    if not task_id:
        return [TextContent(type="text", text="Error: task_id is required")]
    
    try:
        response = await http_client.get(f"{API_BASE_URL}/api/research/{task_id}")
        response.raise_for_status()
        progress = response.json()
        
        status = progress.get("status")
        message = progress.get("message", "")
        
        if status == "done":
            report = progress.get("report_markdown", "")
            return [TextContent(
                type="text",
                text=f"Status: {status}\n\n{report}" if report else f"Status: {status}\n{message}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Status: {status}\nMessage: {message}"
            )]
            
    except httpx.HTTPError as e:
        return [TextContent(
            type="text",
            text=f"HTTP Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def handle_answer_clarifications(arguments: dict) -> Sequence[TextContent]:
    """
    Submit answers to clarifying questions for a research task.
    """
    task_id = arguments.get("task_id")
    answers = arguments.get("answers", [])
    
    if not task_id:
        return [TextContent(type="text", text="Error: task_id is required")]
    
    if not answers:
        return [TextContent(type="text", text="Error: answers array is required")]
    
    try:
        print(f"[MCP] Submitting {len(answers)} answers for task {task_id}")
        
        # Submit clarifications
        response = await http_client.post(
            f"{API_BASE_URL}/api/research/{task_id}/clarify",
            json={"answers": answers}
        )
        response.raise_for_status()
        
        print(f"[MCP] Answers submitted successfully, continuing research...")
        
        return [TextContent(
            type="text",
            text=f"✓ Answers submitted successfully. Research is continuing with your input.\n\nUse `get_research_status` with task_id `{task_id}` to check progress."
        )]
        
    except httpx.HTTPError as e:
        error_detail = ""
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except:
            error_detail = str(e)
        
        return [TextContent(
            type="text",
            text=f"Error submitting answers: {error_detail}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def handle_configure_settings(arguments: dict) -> Sequence[TextContent]:
    """
    Configure research settings.
    """
    try:
        response = await http_client.post(
            f"{API_BASE_URL}/api/settings",
            json=arguments
        )
        response.raise_for_status()
        result = response.json()
        
        return [TextContent(
            type="text",
            text=f"Settings updated successfully: {json.dumps(arguments, indent=2)}"
        )]
        
    except httpx.HTTPError as e:
        return [TextContent(
            type="text",
            text=f"HTTP Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def handle_get_settings() -> Sequence[TextContent]:
    """
    Get current research settings.
    """
    try:
        response = await http_client.get(f"{API_BASE_URL}/api/settings")
        response.raise_for_status()
        settings = response.json()
        
        # Format nicely
        llm_provider = settings.get("llm_provider", "unknown")
        search_provider = settings.get("search_provider", "unknown")
        
        output = f"""# Current OpenResearch Configuration

## LLM Provider
**Active Provider:** {llm_provider}

### Provider Details
"""
        
        if llm_provider == "ollama":
            output += f"""- **Base URL:** {settings.get('ollama_base_url', 'not set')}
- **Thinking Model:** {settings.get('ollama_thinking_model', 'not set')}
- **Task Model:** {settings.get('ollama_task_model', 'not set')}
"""
        elif llm_provider == "openrouter":
            has_key = bool(settings.get('openrouter_api_key'))
            output += f"""- **API Key:** {'✓ Configured' if has_key else '✗ NOT SET (required!)'}
- **Thinking Model:** {settings.get('openrouter_thinking_model', 'not set')}
- **Task Model:** {settings.get('openrouter_task_model', 'not set')}
"""
        elif llm_provider == "lmstudio":
            output += f"""- **Base URL:** {settings.get('lmstudio_base_url', 'not set')}
- **Thinking Model:** {settings.get('lmstudio_thinking_model', 'not set')}
- **Task Model:** {settings.get('lmstudio_task_model', 'not set')}
"""
        
        output += f"""
## Search Provider
**Active Provider:** {search_provider}

### Search Details
"""
        
        if search_provider == "searxng":
            output += f"""- **Base URL:** {settings.get('searxng_base_url', 'not set')}
- **Language:** {settings.get('searxng_language', 'not set')}
- **Results:** {settings.get('searxng_results', 'not set')}
"""
        elif search_provider == "duckduckgo":
            output += f"""- **Region:** {settings.get('duckduckgo_region', 'not set')}
- **Results:** {settings.get('duckduckgo_results', 'not set')}
"""
        
        output += "\n---\n\n*Use `configure_research_settings` to change these settings*"
        
        return [TextContent(type="text", text=output)]
        
    except httpx.HTTPError as e:
        return [TextContent(
            type="text",
            text=f"HTTP Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """
    Run the MCP server.
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openresearch",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
