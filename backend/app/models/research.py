from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str
    depth: str = Field(default="standard", description="surface|standard|deep")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Opaque metadata echoed back in progress responses")


class SearchQuery(BaseModel):
	query: str
	rationale: Optional[str] = None


class ClarifyingQuestion(BaseModel):
	question: str
	context: Optional[str] = None
	type: str = Field(default="text", description="text|multiple_choice")
	options: Optional[List[str]] = Field(default=None, description="Options for multiple choice questions")


class ClarifyingQuestions(BaseModel):
	questions: List[ClarifyingQuestion]
	topic: str


class ClarifyingAnswers(BaseModel):
	answers: List[str]  # Answers corresponding to the questions


class SearchPlan(BaseModel):
	topic: str
	queries: List[SearchQuery]


class SearchHit(BaseModel):
	title: str
	url: str
	snippet: Optional[str] = None


class SearchStepResult(BaseModel):
	query: str
	hits: List[SearchHit]


class ResearchProgress(BaseModel):
    task_id: str
    topic: str
    depth: str
    metadata: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    cancelled: bool = Field(default=False)
    message: Optional[str] = None
    clarifying_questions: Optional[ClarifyingQuestions] = None
    awaiting_clarification: bool = Field(default=False)
    plan: Optional[SearchPlan] = None
    steps: List[SearchStepResult] = Field(default_factory=list)
    report_markdown: Optional[str] = None
    awaiting_confirmation: bool = Field(default=False)
    # Debug information
    debug_clarifying_prompt: Optional[str] = None
    debug_clarifying_response: Optional[str] = None
    debug_plan_prompt: Optional[str] = None
    debug_plan_response: Optional[str] = None
    debug_report_prompt: Optional[str] = None
    debug_report_response: Optional[str] = None


class ResearchResponse(BaseModel):
    task_id: str
    status: str
    progress: ResearchProgress


class ResearchRunRequest(ResearchRequest):
    wait_for_completion: bool = Field(default=True, description="If true, block until the task finishes or times out")
    poll_interval_seconds: float = Field(default=1.0, ge=0.2, le=10.0)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)


class ResearchRunResponse(BaseModel):
    task_id: str
    status: str
    completed: bool
    progress: ResearchProgress


class QueryConfirmation(BaseModel):
    approved_queries: List[SearchQuery]


class ClarificationResponse(BaseModel):
    answers: List[str]