"""
Repository helpers: small, focused functions wrapping the SQLAlchemy
models in database/models.py. Callers (workflow_executor, the FastAPI
app, and the Streamlit dashboard) use these instead of writing raw
queries, so persistence logic lives in one place.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from database.models import (
    Approval,
    AuditLog,
    Decision,
    Report,
    Workflow,
    WorkflowRun,
    WorkflowStep,
)


# ============================================================
# WORKFLOWS
# ============================================================

def create_workflow(session, name: str, objective: str, definition: dict) -> Workflow:
    workflow = Workflow(
        name=name,
        objective=objective,
        definition_json=json.dumps(definition, default=str),
    )
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


def get_workflow(session, workflow_id: str) -> Optional[Workflow]:
    return session.get(Workflow, workflow_id)


def list_workflows(session, limit: int = 100):
    return (
        session.query(Workflow)
        .order_by(Workflow.created_at.desc())
        .limit(limit)
        .all()
    )


# ============================================================
# WORKFLOW RUNS
# ============================================================

def create_run(session, workflow_id: str, query: str, user: str = "anonymous") -> WorkflowRun:
    run = WorkflowRun(
        workflow_id=workflow_id,
        query=query,
        user=user,
        status="RUNNING",
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def update_run(
    session,
    run_id: str,
    status: Optional[str] = None,
    message: Optional[str] = None,
    results: Optional[dict] = None,
    context: Optional[dict] = None,
    finished: bool = False,
) -> Optional[WorkflowRun]:
    run = session.get(WorkflowRun, run_id)
    if not run:
        return None

    if status is not None:
        run.status = status
    if message is not None:
        run.message = message
    if results is not None:
        run.results_json = json.dumps(results, default=str)
    if context is not None:
        run.context_json = json.dumps(context, default=str)

    if finished:
        run.completed_at = datetime.utcnow()
        if run.started_at:
            run.duration_seconds = (run.completed_at - run.started_at).total_seconds()

    session.commit()
    session.refresh(run)
    return run


def get_run(session, run_id: str) -> Optional[WorkflowRun]:
    return session.get(WorkflowRun, run_id)


def list_runs(session, limit: int = 100):
    return (
        session.query(WorkflowRun)
        .order_by(WorkflowRun.started_at.desc())
        .limit(limit)
        .all()
    )


# ============================================================
# WORKFLOW STEPS
# ============================================================

def log_step(
    session,
    run_id: str,
    step_name: str,
    step_type: str,
    status: str,
    duration_seconds: float = 0,
    error: Optional[str] = None,
    agent: Optional[str] = None,
    tool: Optional[str] = None,
) -> WorkflowStep:
    step = WorkflowStep(
        run_id=run_id,
        step_name=step_name,
        step_type=step_type,
        status=status,
        duration_seconds=duration_seconds,
        error=error,
        agent=agent,
        tool=tool,
    )
    session.add(step)
    session.commit()
    return step


def list_steps(session, run_id: str):
    return (
        session.query(WorkflowStep)
        .filter(WorkflowStep.run_id == run_id)
        .order_by(WorkflowStep.created_at.asc())
        .all()
    )


# ============================================================
# DECISIONS
# ============================================================

def record_decision(session, run_id: str, decision_label: str, reasoning_text: str) -> Decision:
    decision = Decision(
        run_id=run_id,
        decision=decision_label,
        reasoning_text=reasoning_text,
    )
    session.add(decision)
    session.commit()
    session.refresh(decision)
    return decision


def get_decision(session, decision_id: str) -> Optional[Decision]:
    return session.get(Decision, decision_id)


def list_decisions(session, limit: int = 100):
    return (
        session.query(Decision)
        .order_by(Decision.created_at.desc())
        .limit(limit)
        .all()
    )


# ============================================================
# APPROVALS (human-in-the-loop)
# ============================================================

def create_approval(session, run_id: str) -> Approval:
    approval = Approval(run_id=run_id, status="PENDING")
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval


def resolve_approval(
    session, approval_id: str, approved: bool, resolved_by: str = "reviewer", comment: str = ""
) -> Optional[Approval]:
    approval = session.get(Approval, approval_id)
    if not approval:
        return None

    approval.status = "APPROVED" if approved else "REJECTED"
    approval.resolved_at = datetime.utcnow()
    approval.resolved_by = resolved_by
    approval.comment = comment

    session.commit()
    session.refresh(approval)
    return approval


def get_pending_approval_for_run(session, run_id: str) -> Optional[Approval]:
    return (
        session.query(Approval)
        .filter(Approval.run_id == run_id, Approval.status == "PENDING")
        .order_by(Approval.requested_at.desc())
        .first()
    )


def list_pending_approvals(session, limit: int = 100):
    return (
        session.query(Approval)
        .filter(Approval.status == "PENDING")
        .order_by(Approval.requested_at.asc())
        .limit(limit)
        .all()
    )


# ============================================================
# AUDIT LOG
# ============================================================

def write_audit_log(
    session,
    run_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    user: str = "anonymous",
    step: Optional[str] = None,
    agent: Optional[str] = None,
    tool: Optional[str] = None,
    decision: Optional[str] = None,
    status: Optional[str] = None,
    error: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        run_id=run_id,
        workflow_id=workflow_id,
        user=user,
        step=step,
        agent=agent,
        tool=tool,
        decision=decision,
        status=status,
        error=error,
    )
    session.add(entry)
    session.commit()
    return entry


def list_audit_logs(session, run_id: Optional[str] = None, limit: int = 200):
    query = session.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if run_id:
        query = query.filter(AuditLog.run_id == run_id)
    return query.limit(limit).all()


# ============================================================
# REPORTS
# ============================================================

def register_report(session, run_id: str, report_type: str, file_path: str) -> Report:
    report = Report(run_id=run_id, report_type=report_type, file_path=file_path)
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def list_reports(session, run_id: Optional[str] = None, limit: int = 100):
    query = session.query(Report).order_by(Report.created_at.desc())
    if run_id:
        query = query.filter(Report.run_id == run_id)
    return query.limit(limit).all()


# ============================================================
# DASHBOARD / ANALYTICS
# ============================================================

def dashboard_metrics(session) -> dict:
    runs = session.query(WorkflowRun).all()

    total = len(runs)
    completed = sum(1 for r in runs if r.status == "COMPLETED")
    failed = sum(1 for r in runs if r.status == "FAILED")
    pending_review = sum(1 for r in runs if r.status == "PENDING_REVIEW")
    rejected = sum(1 for r in runs if r.status == "REJECTED")

    durations = [r.duration_seconds for r in runs if r.duration_seconds]
    avg_duration = round(sum(durations) / len(durations), 3) if durations else 0

    decisions = session.query(Decision).all()
    decision_total = len(decisions) or 1
    approve_rate = round(
        100 * sum(1 for d in decisions if d.decision == "APPROVE") / decision_total, 2
    )
    reject_rate = round(
        100 * sum(1 for d in decisions if d.decision == "REJECT") / decision_total, 2
    )
    review_rate = round(
        100 * sum(1 for d in decisions if d.decision == "REVIEW") / decision_total, 2
    )

    steps = session.query(WorkflowStep).all()
    step_failures: dict[str, int] = {}
    for s in steps:
        if s.status == "FAILED":
            step_failures[s.step_name] = step_failures.get(s.step_name, 0) + 1

    return {
        "total_workflows": total,
        "successful_runs": completed,
        "failed_runs": failed,
        "pending_review_runs": pending_review,
        "rejected_runs": rejected,
        "average_execution_time_seconds": avg_duration,
        "approval_rate_percent": approve_rate,
        "rejection_rate_percent": reject_rate,
        "review_rate_percent": review_rate,
        "step_failure_counts": step_failures,
        "total_steps_logged": len(steps),
    }
