"""
Enterprise REST API (Module F).

Run with:
    uvicorn api.main:app --reload --port 8000

This exposes the SAME AgentCoordinator / WorkflowExecutor used by the
Streamlit UI, so a workflow triggered through the API is executed,
persisted, audited, and (if routed to REVIEW) paused for human
approval exactly the same way it is when triggered through the UI.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Header, status
from pydantic import BaseModel, Field

import config
from database.models import init_db, get_session
from database import repository as repo
from workflows.coordinator import AgentCoordinator
from reports.report_manager import generate_report

from fastapi.responses import FileResponse


app = FastAPI(
    title="Enterprise Workflow Platform API",
    description=(
        "REST API for the AI Agent Coordination & Decision Engine: "
        "build and execute multi-agent business workflows, review "
        "decisions, approve/reject human-in-the-loop steps, and "
        "retrieve reports and audit logs."
    ),
    version="1.0.0",
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def _on_startup():
    init_db()


# One shared coordinator instance is fine here: agents are stateless
# w.r.t. the LLM call itself, and per-request session state (memory)
# is intentionally NOT relied upon by the API -- persistence for
# anything that matters (runs, steps, decisions) goes through the
# database, not in-process memory.
_coordinator = AgentCoordinator()


# ============================================================
# AUTH (simple bearer token, optional)
# ============================================================

def require_auth(authorization: Optional[str] = Header(None)):
    """
    If API_AUTH_TOKEN is set in .env, all write endpoints require
    `Authorization: Bearer <token>`. If unset, auth is skipped (local
    demo mode). Never logs or echoes the configured token.
    """

    if not config.API_AUTH_TOKEN:
        return True

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")

    token = authorization.removeprefix("Bearer ").strip()

    if token != config.API_AUTH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    return True


# ============================================================
# SCHEMAS
# ============================================================

class WorkflowCreateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Business problem to automate.")


class WorkflowExecuteRequest(BaseModel):
    user: str = Field(default="anonymous")


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    resolved_by: str = Field(default="reviewer")
    comment: str = Field(default="")


class ReportRequest(BaseModel):
    report_type: str = Field(..., description="pdf | docx | xlsx | json")


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_provider": config.LLM_PROVIDER,
        "database": config.DATABASE_URL,
    }


# ============================================================
# WORKFLOWS
# ============================================================

@app.post("/api/workflows", status_code=201)
def create_workflow(payload: WorkflowCreateRequest, _auth=Depends(require_auth)):
    """
    Build (but do not execute) a workflow definition for a business
    query, using the same WorkflowBuilder as the Streamlit UI.
    """

    workflow = _coordinator.run_workflow_builder(payload.query)

    if not isinstance(workflow, dict) or not workflow.get("steps"):
        raise HTTPException(status_code=422, detail="Could not build a valid workflow for this query.")

    return {"query": payload.query, "workflow": workflow}


@app.get("/api/workflows")
def list_workflows(limit: int = 50, session=Depends(get_session)):
    workflows = repo.list_workflows(session, limit=limit)
    return [
        {
            "id": w.id,
            "name": w.name,
            "objective": w.objective,
            "created_at": w.created_at,
        }
        for w in workflows
    ]


@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: str, session=Depends(get_session)):
    import json

    workflow = repo.get_workflow(session, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    return {
        "id": workflow.id,
        "name": workflow.name,
        "objective": workflow.objective,
        "definition": json.loads(workflow.definition_json),
        "created_at": workflow.created_at,
    }


@app.post("/api/workflows/{workflow_id}/execute")
def execute_workflow(
    workflow_id: str,
    payload: WorkflowExecuteRequest,
    session=Depends(get_session),
    _auth=Depends(require_auth),
):
    """
    Execute an already-built workflow by ID. Builds a *new* workflow
    definition scoped to the same objective (WorkflowBuilder is
    deterministic per-query) so the executor always has a fresh,
    validated step list, then runs it through the exact same
    WorkflowExecutor used by the UI -- including retries, timeouts,
    DB persistence, audit logging, and the human-review pause.
    """

    import json

    db_workflow = repo.get_workflow(session, workflow_id)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    workflow_definition = json.loads(db_workflow.definition_json)
    query = db_workflow.objective or ""

    execution = _coordinator.run_workflow(query, workflow_definition, user=payload.user)

    return execution


@app.post("/api/workflows/execute")
def build_and_execute_workflow(
    payload: WorkflowCreateRequest,
    user: str = "anonymous",
    _auth=Depends(require_auth),
):
    """
    Convenience endpoint: build AND execute a workflow for a business
    query in one call -- mirrors what the Streamlit "Run" button does.
    """

    workflow = _coordinator.run_workflow_builder(payload.query)

    if not isinstance(workflow, dict) or not workflow.get("steps"):
        raise HTTPException(status_code=422, detail="Could not build a valid workflow for this query.")

    execution = _coordinator.run_workflow(payload.query, workflow, user=user)
    return execution


# ============================================================
# RUNS
# ============================================================

@app.get("/api/runs")
def list_runs(limit: int = 50, session=Depends(get_session)):
    runs = repo.list_runs(session, limit=limit)
    return [
        {
            "id": r.id,
            "workflow_id": r.workflow_id,
            "query": r.query,
            "status": r.status,
            "message": r.message,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "duration_seconds": r.duration_seconds,
        }
        for r in runs
    ]


@app.get("/api/runs/{run_id}")
def get_run(run_id: str, session=Depends(get_session)):
    import json

    run = repo.get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    steps = repo.list_steps(session, run_id)
    reports = repo.list_reports(session, run_id)

    return {
        "id": run.id,
        "workflow_id": run.workflow_id,
        "query": run.query,
        "status": run.status,
        "message": run.message,
        "results": json.loads(run.results_json) if run.results_json else {},
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "duration_seconds": run.duration_seconds,
        "steps": [
            {
                "step_name": s.step_name,
                "step_type": s.step_type,
                "status": s.status,
                "duration_seconds": s.duration_seconds,
                "error": s.error,
            }
            for s in steps
        ],
        "reports": [
            {"report_type": r.report_type, "file_path": r.file_path}
            for r in reports
        ],
    }


# ============================================================
# DECISIONS
# ============================================================

@app.get("/api/decisions/{decision_id}")
def get_decision(decision_id: str, session=Depends(get_session)):
    decision = repo.get_decision(session, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found.")

    return {
        "id": decision.id,
        "run_id": decision.run_id,
        "decision": decision.decision,
        "reasoning_text": decision.reasoning_text,
        "created_at": decision.created_at,
    }


# ============================================================
# HUMAN-IN-THE-LOOP APPROVALS
# ============================================================

@app.get("/api/approvals/pending")
def pending_approvals(session=Depends(get_session)):
    approvals = repo.list_pending_approvals(session)
    return [
        {
            "id": a.id,
            "run_id": a.run_id,
            "status": a.status,
            "requested_at": a.requested_at,
        }
        for a in approvals
    ]


@app.post("/api/runs/{run_id}/decision")
def submit_human_decision(
    run_id: str,
    payload: ApprovalDecisionRequest,
    _auth=Depends(require_auth),
):
    """
    Approve or reject a workflow that is PENDING_REVIEW. Resumes and
    completes the workflow (running the Response step) on approval.
    """

    try:
        execution = _coordinator.resume_workflow(
            run_id,
            payload.approved,
            resolved_by=payload.resolved_by,
            comment=payload.comment,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return execution


# ============================================================
# REPORTS
# ============================================================

@app.post("/api/runs/{run_id}/reports")
def create_report(run_id: str, payload: ReportRequest, session=Depends(get_session)):
    import json

    run = repo.get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    execution = {
        "run_id": run.id,
        "status": run.status,
        "message": run.message,
        "results": json.loads(run.results_json) if run.results_json else {},
        "metrics": {},
    }

    try:
        file_path = generate_report(execution, run.query, payload.report_type)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    return {"run_id": run_id, "report_type": payload.report_type, "file_path": file_path}


@app.get("/api/runs/{run_id}/reports/{report_type}/download")
def download_report(run_id: str, report_type: str, session=Depends(get_session)):
    reports = repo.list_reports(session, run_id)
    match = next((r for r in reports if r.report_type == report_type), None)

    if not match or not os.path.exists(match.file_path):
        raise HTTPException(status_code=404, detail="Report not found. Generate it first via POST /api/runs/{run_id}/reports.")

    return FileResponse(match.file_path, filename=os.path.basename(match.file_path))


# ============================================================
# AUDIT LOG
# ============================================================

@app.get("/api/audit-logs")
def audit_logs(run_id: Optional[str] = None, limit: int = 200, session=Depends(get_session)):
    logs = repo.list_audit_logs(session, run_id=run_id, limit=limit)
    return [
        {
            "id": log.id,
            "run_id": log.run_id,
            "workflow_id": log.workflow_id,
            "user": log.user,
            "step": log.step,
            "agent": log.agent,
            "tool": log.tool,
            "decision": log.decision,
            "status": log.status,
            "error": log.error,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard/metrics")
def dashboard_metrics(session=Depends(get_session)):
    return repo.dashboard_metrics(session)
