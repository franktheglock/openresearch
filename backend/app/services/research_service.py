from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Dict

from ..models.research import (
	ResearchRequest,
	ResearchProgress,
	SearchPlan,
	SearchQuery,
	SearchStepResult,
	QueryConfirmation,
	ClarifyingQuestions,
	ClarifyingQuestion,
	ClarificationResponse,
)
from .ollama_service import ollama
from .openrouter_service import openrouter
from .openai_service import openai_client
from .anthropic_service import anthropic
from .gemini_service import gemini
from .mistral_service import mistral
from .groq_service import groq
from .lmstudio_service import lmstudio_client
from .searxng_service import searx
from .duckduckgo_service import duckduckgo
from ..config import settings


def _get_llm_service():
	"""Get the appropriate LLM service based on configuration"""
	provider = (settings.llm_provider or "").lower()
	if provider == "openrouter":
		return openrouter
	if provider == "ollama":
		return ollama
	if provider == "openai":
		return openai_client
	if provider == "anthropic":
		return anthropic
	if provider == "gemini":
		return gemini
	if provider == "mistral":
		return mistral
	if provider == "groq":
		return groq
	if provider == "lmstudio":
		return lmstudio_client
	# default fallback
	return openrouter


def _get_search_service():
	"""Get the appropriate search service based on configuration"""
	provider = (settings.search_provider or "").lower()
	if provider == "duckduckgo":
		return duckduckgo
	# default fallback to searxng
	return searx


def _make_clarifying_prompt(topic: str, depth: str) -> str:
	return (
		f"You are a research assistant helping to clarify a research topic before conducting web searches.\n\n"
		f"Research Topic: {topic}\n"
		f"Research Depth: {depth}\n\n"
		"Your task is to ask 1-3 clarifying questions that are RELEVANT to this specific topic. "
		"Think critically about what dimensions of this topic actually matter:\n"
		"- Ask about time frame/scope ONLY if it's actually relevant to understanding this topic\n"
		"- Ask about geography ONLY if location matters for this topic\n"
		"- Ask about audience/use case ONLY if different stakeholders would have different needs\n"
		"- Ask about specific aspects/angles that would help narrow the focus\n"
		"- Ask about technical depth ONLY for technical topics\n\n"
		"Do NOT ask irrelevant questions. If a question wouldn't actually help clarify this specific topic, skip it.\n"
		"If the topic is already very specific and clear, you can provide an empty questions array.\n\n"
		"You can create two types of questions:\n"
		"1. TEXT QUESTIONS: For open-ended responses where users can type their answer\n"
		"2. MULTIPLE CHOICE: For questions with predefined options users can select from\n\n"
		"Return ONLY valid JSON in this exact format:\n"
		'{\n'
		'  "questions": [\n'
		'    {"question": "Your question here?", "type": "text or multiple_choice", "options": ["option1", "option2"] if multiple_choice else null, "context": "Brief explanation of why this matters"}\n'
		'  ],\n'
		'  "topic": "research topic"\n'
		'}\n\n'
		"No additional text, explanations, or formatting outside the JSON."
	)


_TASKS: Dict[str, ResearchProgress] = {}
_LOCK = threading.Lock()


def _make_report_prompt(topic: str, steps: list[SearchStepResult], depth: str) -> str:
	bullets = []
	for s in steps:
		bullets.append(f"**Query**: {s.query}\n**Top Results**:\n" + "\n".join([f"  • {h.title}\n    Source: {h.url}\n    Summary: {h.snippet or 'No summary available'}" for h in s.hits[:5]]))
	sources_block = "\n\n".join(bullets)
	
	depth_instructions = {
		"surface": "Write a concise overview (2-3 sections) focusing on key concepts and basic understanding.",
		"standard": "Create a comprehensive report (4-6 sections) covering main aspects, recent developments, and practical implications.",
		"deep": "Produce an in-depth analysis (6+ sections) including technical details, multiple perspectives, trends, and expert insights."
	}
	
	instruction = depth_instructions.get(depth, depth_instructions["standard"])
	
	return (
		f"You are an expert research analyst. Create a professional, well-structured research report in Markdown format.\n\n"
		f"**Research Topic**: {topic}\n"
		f"**Depth Level**: {depth} - {instruction}\n\n"
		f"**Source Material**:\n{sources_block}\n\n"
		"**Report Requirements**:\n"
		"- Use proper Markdown formatting with clear headers (# ## ###)\n"
		"- Create tables for comparative data or statistics when appropriate\n"
		"- Include bullet points for key findings and recommendations\n"
		"- Write objectively and cite sources with [text](URL) links\n"
		"- Organize logically: Introduction → Main Sections → Key Findings → Conclusion\n"
		"- End with a '## Sources' section listing all referenced materials\n"
		"- Use **bold** for emphasis and `code formatting` for technical terms\n"
		"- Include relevant quotes from sources when they add value\n\n"
		"Focus on accuracy, clarity, and actionable insights. Synthesize information rather than just summarizing each source."
	)


def _fixed_make_plan_prompt(topic: str, depth: str, clarifying_answers: list[str] = None) -> str:
	depth_guidance = {
		"surface": "Focus on basic overview and fundamental concepts. 3-4 queries covering general information.",
		"standard": "Cover key aspects, recent developments, and practical applications. 4-5 queries for comprehensive coverage.",
		"deep": "Include detailed analysis, expert opinions, technical details, and multiple perspectives. 5-6 queries for thorough investigation."
	}
	
	guidance = depth_guidance.get(depth, depth_guidance["standard"])
	
	clarification_context = ""
	if clarifying_answers:
		clarification_context = f"\n\nUser provided these clarifications:\n" + "\n".join(f"- {answer}" for answer in clarifying_answers) + "\n"
	
	return (
		f"You are a research planning expert. Create a strategic web search plan for comprehensive research on the given topic.\n\n"
		f"Topic: {topic}\n"
		f"Research Depth: {depth} - {guidance}{clarification_context}\n\n"
		"Requirements:\n"
		"- Generate diverse, specific search queries that will uncover different angles and aspects\n"
		"- Each query should target different information sources (news, academic, industry, technical, etc.)\n"
		"- Include both current/recent information and foundational knowledge\n"
		"- Avoid redundant or overly similar queries\n"
		"- Focus on authoritative and reliable sources\n"
		"- Incorporate the user's clarifications to make searches more targeted\n\n"
		"Return ONLY valid JSON in this exact format:\n"
		'{"topic": "research topic", "queries": [{"query": "specific search terms", "rationale": "why this search is important"}]}\n\n'
		"No additional text, explanations, or formatting."
	)


def start_research(req: ResearchRequest) -> str:
	task_id = str(uuid.uuid4())
	progress = ResearchProgress(
		task_id=task_id,
		started_at=datetime.utcnow(),
		status="starting",
		message="Generating search plan",
	)
	with _LOCK:
		_TASKS[task_id] = progress
	
	# Terminal debug output
	print(f"\n{'='*80}")
	print(f"🚀 RESEARCH TASK STARTED - Task: {task_id}")
	print(f"{'='*80}")
	print(f"📋 Topic: {req.topic}")
	print(f"🎯 Depth: {req.depth}")
	print(f"🕒 Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
	print(f"{'='*80}\n")

	thread = threading.Thread(target=_run_research, args=(task_id, req), daemon=True)
	thread.start()
	return task_id


def get_progress(task_id: str) -> ResearchProgress | None:
	with _LOCK:
		return _TASKS.get(task_id)


def confirm_queries(task_id: str, confirmation: QueryConfirmation) -> bool:
	with _LOCK:
		task = _TASKS.get(task_id)
		if not task or not task.awaiting_confirmation:
			return False
		
		# Update the plan with confirmed queries
		if task.plan:
			task.plan.queries = confirmation.approved_queries
		task.awaiting_confirmation = False
		task.status = "searching"
		task.message = "Executing web searches"
	
	# Continue with the search phase in a new thread
	thread = threading.Thread(target=_continue_research, args=(task_id,), daemon=True)
	thread.start()
	return True


def submit_clarification(task_id: str, clarification: ClarificationResponse) -> bool:
	with _LOCK:
		task = _TASKS.get(task_id)
		if not task or not task.awaiting_clarification:
			return False
		
		task.awaiting_clarification = False
		task.status = "planning"
		task.message = "Creating enhanced search plan with your input"
	
	# Continue with planning phase using clarifications
	thread = threading.Thread(target=_continue_planning, args=(task_id, clarification.answers), daemon=True)
	thread.start()
	return True


def _continue_research(task_id: str):
	"""Continue research after query confirmation"""
	try:
		task = None
		with _LOCK:
			task = _TASKS.get(task_id)
		
		if not task or not task.plan:
			return
		
		# Search
		steps: list[SearchStepResult] = []
		print(f"\n{'='*80}")
		print(f"🔍 EXECUTING SEARCH QUERIES - Task: {task_id}")
		print(f"{'='*80}")
		
		for i, q in enumerate(task.plan.queries, 1):
			print(f"🔎 Query {i}/{len(task.plan.queries)}: {q.query}")
			if q.rationale:
				print(f"   💡 Rationale: {q.rationale}")
			
			search_service = _get_search_service()
			hits = search_service.search(q.query)
			print(f"   ✅ Found {len(hits)} results")
			
			steps.append(SearchStepResult(query=q.query, hits=hits))
			with _LOCK:
				_TASKS[task_id].steps = steps.copy()
		
		print(f"{'='*80}\n")

		# Report
		with _LOCK:
			_TASKS[task_id].status = "reporting"
			_TASKS[task_id].message = "Compiling report"

		# Get topic and depth from the original request (we need to store this in the task)
		topic = task.plan.topic
		report_prompt = _make_report_prompt(topic, steps, "standard")  # Default depth
		llm_service = _get_llm_service()
		report_md = llm_service.complete(report_prompt)

		with _LOCK:
			_TASKS[task_id].debug_report_prompt = report_prompt
			_TASKS[task_id].debug_report_response = report_md
			_TASKS[task_id].report_markdown = report_md
			_TASKS[task_id].status = "done"
			_TASKS[task_id].message = "Completed"
		
		# Terminal debug output
		print(f"\n{'='*80}")
		print(f"📝 REPORT GENERATION DEBUG - Task: {task_id}")
		print(f"{'='*80}")
		print(f"📝 PROMPT SENT TO LLM:")
		print(f"-" * 40)
		print(report_prompt)
		print(f"-" * 40)
		print(f"🤖 LLM RESPONSE:")
		print(f"-" * 40)
		print(report_md)
		print(f"{'='*80}\n")
	except Exception as e:
		with _LOCK:
			_TASKS[task_id].status = "error"
			_TASKS[task_id].message = f"Failed: {e}"


def _continue_planning(task_id: str, clarifying_answers: list[str]):
	"""Continue with planning after receiving clarification"""
	try:
		task = None
		with _LOCK:
			task = _TASKS.get(task_id)
		
		if not task or not task.clarifying_questions:
			return
		
		# Get the original topic and depth (we need to store these in the task)
		topic = task.clarifying_questions.topic
		
		# Generate plan with clarifications
		plan_prompt = _fixed_make_plan_prompt(topic, "standard", clarifying_answers)  # Default depth
		llm_service = _get_llm_service()
		plan_text = llm_service.think(plan_prompt)

		# Store debug information
		with _LOCK:
			_TASKS[task_id].debug_plan_prompt = plan_prompt
			_TASKS[task_id].debug_plan_response = plan_text

		# Parse plan JSON leniently
		plan = _parse_plan(plan_text, topic)

		with _LOCK:
			_TASKS[task_id].plan = plan
			_TASKS[task_id].status = "awaiting_confirmation"
			_TASKS[task_id].message = "Waiting for search query confirmation"
			_TASKS[task_id].awaiting_confirmation = True

	except Exception as e:
		with _LOCK:
			_TASKS[task_id].status = "error"
			_TASKS[task_id].message = f"Failed during planning: {e}"


def _run_research(task_id: str, req: ResearchRequest):
	try:
		# First step: Ask clarifying questions
		with _LOCK:
			_TASKS[task_id].status = "clarifying"
			_TASKS[task_id].message = "Asking clarifying questions"

		clarifying_prompt = _make_clarifying_prompt(req.topic, req.depth)
		llm_service = _get_llm_service()
		clarifying_text = llm_service.think(clarifying_prompt)

		# Store debug information
		with _LOCK:
			_TASKS[task_id].debug_clarifying_prompt = clarifying_prompt
			_TASKS[task_id].debug_clarifying_response = clarifying_text
		
		# Terminal debug output
		print(f"\n{'='*80}")
		print(f"🤔 CLARIFYING QUESTIONS DEBUG - Task: {task_id}")
		print(f"{'='*80}")
		print(f"📝 PROMPT SENT TO LLM:")
		print(f"-" * 40)
		print(clarifying_prompt)
		print(f"-" * 40)
		print(f"🤖 LLM RESPONSE:")
		print(f"-" * 40)
		print(clarifying_text)
		print(f"{'='*80}\n")

		# Parse clarifying questions
		clarifying_questions = _parse_clarifying_questions(clarifying_text, req.topic)
		
		# Debug: Show parsed questions
		print(f"\n🔍 PARSED CLARIFYING QUESTIONS:")
		for i, q in enumerate(clarifying_questions.questions, 1):
			print(f"   Question {i}: {q.question[:50]}...")
			print(f"   Type: {q.type}")
			print(f"   Options: {q.options}")
			print(f"   Context: {q.context}")
			print(f"   ---")

		with _LOCK:
			_TASKS[task_id].clarifying_questions = clarifying_questions
			
			# If there are questions, wait for user input
			if clarifying_questions.questions:
				_TASKS[task_id].status = "awaiting_clarification"
				_TASKS[task_id].message = "Waiting for your input on clarifying questions"
				_TASKS[task_id].awaiting_clarification = True
				return
			else:
				# No questions needed, proceed directly to planning
				_TASKS[task_id].status = "planning"
				_TASKS[task_id].message = "Creating search plan"

		# Continue with planning if no clarification needed
		plan_prompt = _fixed_make_plan_prompt(req.topic, req.depth)
		plan_text = llm_service.think(plan_prompt)

		# Store debug information
		with _LOCK:
			_TASKS[task_id].debug_plan_prompt = plan_prompt
			_TASKS[task_id].debug_plan_response = plan_text
		
		# Terminal debug output
		print(f"\n{'='*80}")
		print(f"📋 PLANNING DEBUG - Task: {task_id}")
		print(f"{'='*80}")
		print(f"📝 PROMPT SENT TO LLM:")
		print(f"-" * 40)
		print(plan_prompt)
		print(f"-" * 40)
		print(f"🤖 LLM RESPONSE:")
		print(f"-" * 40)
		print(plan_text)
		print(f"{'='*80}\n")

		# Parse plan JSON leniently
		plan = _parse_plan(plan_text, req.topic)

		with _LOCK:
			_TASKS[task_id].plan = plan
			_TASKS[task_id].status = "awaiting_confirmation"
			_TASKS[task_id].message = "Waiting for search query confirmation"
			_TASKS[task_id].awaiting_confirmation = True

		# Wait for confirmation (the function will exit here, continuation happens in confirm_queries)
		return
	except Exception as e:
		with _LOCK:
			_TASKS[task_id].status = "error"
			_TASKS[task_id].message = f"Failed: {e}"


def _parse_plan(plan_text: str, topic: str) -> SearchPlan:
	import json
	# try to locate JSON block
	extracted = plan_text
	start = plan_text.find("{")
	end = plan_text.rfind("}")
	if start != -1 and end != -1 and end > start:
		extracted = plan_text[start : end + 1]
	try:
		obj = json.loads(extracted)
		queries_raw = obj.get("queries", [])
		queries = []
		for q in queries_raw:
			if isinstance(q, dict) and q.get("query"):
				queries.append(SearchQuery(query=q["query"], rationale=q.get("rationale")))
			elif isinstance(q, str):
				queries.append(SearchQuery(query=q))
		if not queries:
			# fallback
			queries = [
				SearchQuery(query=f"{topic} overview"),
				SearchQuery(query=f"{topic} latest news"),
				SearchQuery(query=f"{topic} key sources"),
			]
		return SearchPlan(topic=obj.get("topic") or topic, queries=queries[:6])
	except Exception:
		return SearchPlan(
			topic=topic,
			queries=[
				SearchQuery(query=f"{topic} overview"),
				SearchQuery(query=f"{topic} latest developments"),
				SearchQuery(query=f"{topic} research papers"),
			],
		)


def _parse_clarifying_questions(text: str, topic: str) -> ClarifyingQuestions:
	import json
	# try to locate JSON block
	extracted = text
	start = text.find("{")
	end = text.rfind("}")
	if start != -1 and end != -1 and end > start:
		extracted = text[start : end + 1]
	try:
		obj = json.loads(extracted)
		questions_raw = obj.get("questions", [])
		questions = []
		for q in questions_raw:
			if isinstance(q, dict) and q.get("question"):
				questions.append(ClarifyingQuestion(
					question=q["question"], 
					context=q.get("context"),
					type=q.get("type", "text"),
					options=q.get("options")
				))
			elif isinstance(q, str):
				questions.append(ClarifyingQuestion(question=q))
		
		return ClarifyingQuestions(topic=obj.get("topic") or topic, questions=questions)
	except Exception:
		# If parsing fails, return empty questions (will proceed directly to planning)
		return ClarifyingQuestions(topic=topic, questions=[])

