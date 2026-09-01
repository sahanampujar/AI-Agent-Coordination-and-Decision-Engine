import pytest
from fastapi.testclient import TestClient

import config
import api.main as api_main
from workflows.workflow_executor import WorkflowExecutor
from tests.test_workflow_executor import FakeCoordinator, _workflow


class FakeAPICoordinator:
    """
    Mirrors AgentCoordinator's public surface used by api/main.py, but
    drives a FakeCoordinator + real WorkflowExecutor underneath so no
    real LLM call is ever made.
    """

    def __init__(self, **overrides):
        self.inner = FakeCoordinator(**overrides)

    def run_workflow_builder(self, query):
        return _workflow("planner", "research", "analysis", "decision", "response")

    def run_workflow(self, query, workflow, user="anonymous"):
        executor = WorkflowExecutor(self.inner)
        return executor.execute(query, workflow, user=user)

    def resume_workflow(self, run_id, approved, resolved_by="reviewer", comment=""):
        executor = WorkflowExecutor(self.inner)
        return executor.resume(run_id, approved, resolved_by=resolved_by, comment=comment)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api_main, "_coordinator", FakeAPICoordinator())
    monkeypatch.setattr(config, "API_AUTH_TOKEN", "")  # auth disabled by default
    return TestClient(api_main.app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_workflow_endpoint(client):
    response = client.post("/api/workflows", json={"query": "Automate employee leave approval"})
    assert response.status_code == 201
    body = response.json()
    assert body["workflow"]["steps"]


def test_build_and_execute_workflow_endpoint(client):
    response = client.post(
        "/api/workflows/execute",
        json={"query": "Automate employee leave approval"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["results"]["response"]


def test_list_and_get_run(client):
    exec_response = client.post(
        "/api/workflows/execute", json={"query": "Automate employee leave approval"}
    )
    run_id = exec_response.json()["run_id"]

    list_response = client.get("/api/runs")
    assert list_response.status_code == 200
    assert any(r["id"] == run_id for r in list_response.json())

    get_response = client.get(f"/api/runs/{run_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "COMPLETED"


def test_get_nonexistent_run_returns_404(client):
    response = client.get("/api/runs/does-not-exist")
    assert response.status_code == 404


def test_dashboard_metrics_endpoint(client):
    client.post("/api/workflows/execute", json={"query": "test query"})
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "total_workflows" in body
    assert "approval_rate_percent" in body


def test_human_review_approve_flow(monkeypatch):
    monkeypatch.setattr(
        api_main, "_coordinator",
        FakeAPICoordinator(decision="DECISION: REVIEW\nNeeds review."),
    )
    monkeypatch.setattr(config, "API_AUTH_TOKEN", "")
    client = TestClient(api_main.app)

    exec_response = client.post(
        "/api/workflows/execute", json={"query": "Automate employee leave approval"}
    )
    assert exec_response.json()["status"] == "PENDING_REVIEW"
    run_id = exec_response.json()["run_id"]

    decision_response = client.post(
        f"/api/runs/{run_id}/decision",
        json={"approved": True, "resolved_by": "alice"},
    )
    assert decision_response.status_code == 200
    assert decision_response.json()["status"] == "COMPLETED"


def test_auth_required_when_token_configured(monkeypatch):
    monkeypatch.setattr(api_main, "_coordinator", FakeAPICoordinator())
    monkeypatch.setattr(config, "API_AUTH_TOKEN", "secret-token")
    client = TestClient(api_main.app)

    no_auth = client.post("/api/workflows/execute", json={"query": "q"})
    assert no_auth.status_code == 401

    with_auth = client.post(
        "/api/workflows/execute",
        json={"query": "q"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert with_auth.status_code == 200
