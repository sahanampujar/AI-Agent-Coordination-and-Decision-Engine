import time

import pytest

import config
from workflows.workflow_executor import WorkflowExecutor
from core.exceptions import AgentExecutionError


class _NoOpMemory:
    def save(self, *a, **k):
        pass


class FakeCoordinator:
    """
    Stand-in for AgentCoordinator: lets each test control exactly what
    each pipeline stage returns/raises, without touching a real LLM.
    """

    def __init__(self, **overrides):
        self.shared_memory = _NoOpMemory()
        self._overrides = overrides

    def _resolve(self, name, default_value):
        value = self._overrides.get(name, default_value)
        if isinstance(value, Exception):
            raise value
        return value

    def run_planner(self, query):
        return self._resolve("planner", "planned steps")

    def run_tool(self, query):
        return self._resolve("tool", "tool output")

    def run_research(self, plan):
        return self._resolve("research", "research findings")

    def run_analysis(self, research):
        return self._resolve("analysis", "analysis summary")

    def run_decision(self, analysis, query=None):
        return self._resolve("decision", "DECISION: APPROVE\nLooks good.")

    def run_response(self, analysis):
        return self._resolve("response", "final response text")


def _workflow(*step_types):
    """Build a minimal workflow dict with one step per given type."""
    steps = []
    for i, step_type in enumerate(step_types, start=1):
        steps.append({
            "step": i,
            "name": step_type.capitalize(),
            "type": step_type,
            "component": f"{step_type.capitalize()} Agent",
        })
    return {"workflow_name": "Test Workflow", "objective": "test", "steps": steps}


def test_full_pipeline_success():
    coordinator = FakeCoordinator()
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("planner", "research", "analysis", "decision", "response")
    execution = executor.execute("Automate employee leave approval", workflow)

    assert execution["status"] == "COMPLETED"
    results = execution["results"]
    assert results["planner"] == "planned steps"
    assert results["research"] == "research findings"
    assert results["analysis"] == "analysis summary"
    assert results["response"] == "final response text"
    assert results["decision_branch"]["decision"] == "APPROVE"


def test_research_failure_stops_workflow_and_reports_failed_truthfully():
    """
    Regression test for the exact bug in the brief: a failed Research
    step must never result in an overall COMPLETED status, and the
    Research step itself must be marked FAILED (not silently skipped).
    """
    coordinator = FakeCoordinator(
        research=AgentExecutionError("Research Agent", "The model returned an empty response.")
    )
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("planner", "research", "analysis", "decision", "response")
    execution = executor.execute("Automate employee leave approval", workflow)

    assert execution["status"] == "FAILED"
    assert "Research" in execution["message"]
    assert "Step failed" in execution["results"]["Research"]
    # Steps after the failure never ran.
    assert "analysis" not in execution["results"]
    assert "response" not in execution["results"]


def test_empty_workflow_fails_validation():
    coordinator = FakeCoordinator()
    executor = WorkflowExecutor(coordinator)

    execution = executor.execute("query", {"steps": []})
    assert execution["status"] == "FAILED"
    assert "no execution steps" in execution["message"].lower()


def test_invalid_workflow_type_fails_validation():
    coordinator = FakeCoordinator()
    executor = WorkflowExecutor(coordinator)

    execution = executor.execute("query", "not-a-dict")
    assert execution["status"] == "FAILED"


def test_unsupported_step_type_fails():
    coordinator = FakeCoordinator()
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("something_unsupported")
    execution = executor.execute("query", workflow)

    assert execution["status"] == "FAILED"


def test_decision_review_pauses_and_resume_approve_completes(monkeypatch):
    coordinator = FakeCoordinator(decision="DECISION: REVIEW\nNeeds a human look.")
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("planner", "research", "analysis", "decision", "response")
    execution = executor.execute("Automate employee leave approval", workflow)

    assert execution["status"] == "PENDING_REVIEW"
    assert "response" not in execution["results"]
    run_id = execution["run_id"]

    resumed = executor.resume(run_id, approved=True, resolved_by="alice")
    assert resumed["status"] == "COMPLETED"
    assert resumed["results"]["response"] == "final response text"


def test_decision_review_pauses_and_resume_reject_marks_rejected():
    coordinator = FakeCoordinator(decision="DECISION: REVIEW\nNeeds a human look.")
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("planner", "research", "analysis", "decision", "response")
    execution = executor.execute("Automate employee leave approval", workflow)
    run_id = execution["run_id"]

    resumed = executor.resume(run_id, approved=False, resolved_by="bob", comment="Too risky")
    assert resumed["status"] == "REJECTED"
    assert "response" not in resumed["results"]


def test_resume_twice_raises_value_error():
    coordinator = FakeCoordinator(decision="DECISION: REVIEW\nNeeds a look.")
    executor = WorkflowExecutor(coordinator)

    workflow = _workflow("planner", "research", "analysis", "decision", "response")
    execution = executor.execute("q", workflow)
    run_id = execution["run_id"]

    executor.resume(run_id, approved=True)

    with pytest.raises(ValueError):
        executor.resume(run_id, approved=True)


def test_step_timeout_marks_step_failed(monkeypatch):
    monkeypatch.setattr(config, "STEP_TIMEOUT_SECONDS", 0.2)
    monkeypatch.setattr(config, "STEP_MAX_RETRIES", 0)

    class SlowCoordinator(FakeCoordinator):
        def run_planner(self, query):
            time.sleep(1)
            return "too slow"

    executor = WorkflowExecutor(SlowCoordinator())
    workflow = _workflow("planner")
    execution = executor.execute("q", workflow)

    assert execution["status"] == "FAILED"
    error_text = execution["results"]["Planner"].lower()
    assert "timeout" in error_text or "exceeded" in error_text
