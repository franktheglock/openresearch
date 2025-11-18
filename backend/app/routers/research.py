import time

from fastapi import APIRouter, HTTPException

from ..models.research import (
	ResearchRequest,
	ResearchResponse,
	ResearchRunRequest,
	ResearchRunResponse,
	QueryConfirmation,
	ClarificationResponse,
)
from ..services.research_service import (
	start_research,
	get_progress,
	confirm_queries,
	submit_clarification,
	cancel_task,
)


router = APIRouter(prefix="/research", tags=["research"])


@router.post("/start", response_model=ResearchResponse)
def start(req: ResearchRequest):
	task_id = start_research(req)
	progress = get_progress(task_id)
	assert progress is not None
	return ResearchResponse(task_id=task_id, status=progress.status, progress=progress)


@router.post("/run", response_model=ResearchRunResponse)
def run(req: ResearchRunRequest):
	task_id = start_research(req)
	progress = get_progress(task_id)
	assert progress is not None
	if not req.wait_for_completion:
		return ResearchRunResponse(task_id=task_id, status=progress.status, completed=False, progress=progress)

	deadline = time.time() + req.timeout_seconds
	while time.time() < deadline:
		progress = get_progress(task_id)
		if not progress:
			raise HTTPException(status_code=404, detail="Task not found")
		if progress.status in {"done", "error", "cancelled"}:
			return ResearchRunResponse(task_id=task_id, status=progress.status, completed=True, progress=progress)
		time.sleep(req.poll_interval_seconds)

	raise HTTPException(status_code=408, detail="Timed out waiting for task to complete")


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


@router.delete("/{task_id}")
def cancel(task_id: str):
	success = cancel_task(task_id)
	if not success:
		raise HTTPException(status_code=404, detail="Task not found")
	return {"message": "Task cancelled"}

