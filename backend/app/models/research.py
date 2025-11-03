from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
	topic: str
	depth: str = Field(default="standard", description="standard|deep|brief")


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
    started_at: datetime
    status: str
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


class QueryConfirmation(BaseModel):
    approved_queries: List[SearchQuery]


class ClarificationResponse(BaseModel):
    answers: List[str]