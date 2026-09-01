import os

import pytest

from reports.report_manager import generate_report
from database.models import new_session
from database import repository as repo


def _sample_execution(run_id):
    return {
        "run_id": run_id,
        "status": "COMPLETED",
        "message": "ok",
        "results": {
            "response": "Approved: proceed with the leave request.\nNext steps: notify HR."
        },
        "metrics": {
            "total_steps": 5,
            "completed_steps": 5,
            "failed_steps": 0,
            "success_rate": 100,
            "total_duration_seconds": 1.23,
            "step_logs": [
                {"step": "Planner", "type": "planner", "status": "COMPLETED", "duration_seconds": 0.2, "error": None},
            ],
        },
    }


@pytest.mark.parametrize("report_type", ["pdf", "docx", "xlsx", "json"])
def test_generate_report_creates_file_and_registers_it(report_type):
    execution = _sample_execution("run-report-test-1")
    path = generate_report(execution, "Automate employee leave approval", report_type)

    assert os.path.exists(path)
    assert path.endswith(f".{report_type}")

    session = new_session()
    reports = repo.list_reports(session, run_id="run-report-test-1")
    session.close()

    assert any(r.report_type == report_type for r in reports)


def test_different_runs_do_not_overwrite_each_others_report():
    exec_a = _sample_execution("run-a")
    exec_b = _sample_execution("run-b")

    path_a = generate_report(exec_a, "query A", "pdf")
    path_b = generate_report(exec_b, "query B", "pdf")

    assert path_a != path_b
    assert os.path.exists(path_a)
    assert os.path.exists(path_b)


def test_unsupported_report_type_raises_value_error():
    execution = _sample_execution("run-bad-type")
    with pytest.raises(ValueError):
        generate_report(execution, "q", "csv")
