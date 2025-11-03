from fastapi import APIRouter, HTTPException

from ..models.research import ResearchRequest, ResearchResponse, QueryConfirmation, ClarificationResponse
from ..services.research_service import start_research, get_progress, confirm_queries, submit_clarification


router = APIRouter(prefix="/research", tags=["research"])


@router.post("/start", response_model=ResearchResponse)
def start(req: ResearchRequest):
	task_id = start_research(req)
	progress = get_progress(task_id)
	assert progress is not None
	return ResearchResponse(task_id=task_id, status=progress.status, progress=progress)


@router.get("/{task_id}", response_model=ResearchResponse)
def progress(task_id: str):
	p = get_progress(task_id)
	if not p:
		raise HTTPException(status_code=404, detail="Task not found")
	return ResearchResponse(task_id=task_id, status=p.status, progress=p)


@router.post("/{task_id}/confirm")
def confirm_search_queries(task_id: str, confirmation: QueryConfirmation):
	success = confirm_queries(task_id, confirmation)
	if not success:
		raise HTTPException(status_code=404, detail="Task not found or not awaiting confirmation")
	return {"message": "Queries confirmed, continuing research"}


@router.post("/{task_id}/clarify")
def submit_clarifications(task_id: str, clarification: ClarificationResponse):
	success = submit_clarification(task_id, clarification)
	if not success:
		raise HTTPException(status_code=404, detail="Task not found or not awaiting clarification")
	return {"message": "Clarifications received, creating enhanced search plan"}

