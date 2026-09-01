from database.models import new_session
from database import repository as repo


def test_create_and_fetch_workflow_and_run():
    session = new_session()

    workflow = repo.create_workflow(
        session, name="Leave Approval", objective="Automate leave approval",
        definition={"steps": [{"name": "Planner", "type": "planner"}]},
    )
    assert workflow.id

    run = repo.create_run(session, workflow.id, "Automate leave approval", user="alice")
    assert run.status == "RUNNING"

    repo.update_run(session, run.id, status="COMPLETED", message="ok", results={"response": "done"}, finished=True)

    fetched = repo.get_run(session, run.id)
    assert fetched.status == "COMPLETED"
    assert fetched.completed_at is not None
    assert fetched.duration_seconds is not None

    session.close()


def test_log_step_and_list_steps():
    session = new_session()
    workflow = repo.create_workflow(session, "W", "obj", {"steps": []})
    run = repo.create_run(session, workflow.id, "q")

    repo.log_step(session, run.id, "Planner", "planner", "COMPLETED", duration_seconds=0.5)
    repo.log_step(session, run.id, "Research", "research", "FAILED", duration_seconds=1.2, error="boom")

    steps = repo.list_steps(session, run.id)
    assert len(steps) == 2
    assert steps[1].status == "FAILED"
    assert steps[1].error == "boom"

    session.close()


def test_approval_lifecycle():
    session = new_session()
    workflow = repo.create_workflow(session, "W", "obj", {"steps": []})
    run = repo.create_run(session, workflow.id, "q")

    approval = repo.create_approval(session, run.id)
    assert approval.status == "PENDING"

    pending = repo.get_pending_approval_for_run(session, run.id)
    assert pending.id == approval.id

    repo.resolve_approval(session, approval.id, approved=True, resolved_by="carol", comment="looks fine")

    assert repo.get_pending_approval_for_run(session, run.id) is None

    session.close()


def test_audit_log_written_and_filterable():
    session = new_session()
    workflow = repo.create_workflow(session, "W", "obj", {"steps": []})
    run = repo.create_run(session, workflow.id, "q")

    repo.write_audit_log(session, run_id=run.id, workflow_id=workflow.id, status="RUNNING")
    repo.write_audit_log(session, run_id=run.id, workflow_id=workflow.id, status="COMPLETED")

    logs = repo.list_audit_logs(session, run_id=run.id)
    assert len(logs) == 2

    session.close()


def test_dashboard_metrics_aggregates_runs():
    session = new_session()
    workflow = repo.create_workflow(session, "W", "obj", {"steps": []})

    run1 = repo.create_run(session, workflow.id, "q1")
    repo.update_run(session, run1.id, status="COMPLETED", finished=True)

    run2 = repo.create_run(session, workflow.id, "q2")
    repo.update_run(session, run2.id, status="FAILED", finished=True)

    metrics = repo.dashboard_metrics(session)
    assert metrics["total_workflows"] >= 2
    assert metrics["successful_runs"] >= 1
    assert metrics["failed_runs"] >= 1

    session.close()
