import os

from reports.pdf_generator import generate_pdf
from reports.docx_generator import generate_docx
from reports.xlsx_generator import generate_xlsx
from reports.json_generator import generate_json

from database.models import new_session
from database import repository as repo


REPORTS_DIR = os.getenv("REPORTS_OUTPUT_DIR", "reports_output")

_GENERATORS = {"pdf", "docx", "xlsx", "json"}


def generate_report(execution: dict, query: str, report_type: str) -> str:
    """
    Generate a report of the given type for a completed workflow
    execution, save it under REPORTS_DIR, and register it in the
    database so it shows up under GET /api/runs/{id} and the
    dashboard. Returns the file path.
    """

    report_type = (report_type or "").lower().strip()

    if report_type not in _GENERATORS:
        raise ValueError(
            f"Unsupported report type '{report_type}'. "
            f"Choose one of: {sorted(_GENERATORS)}"
        )

    os.makedirs(REPORTS_DIR, exist_ok=True)

    run_id = execution.get("run_id", "unknown")
    filename = os.path.join(REPORTS_DIR, f"{run_id}.{report_type}")

    final_response = execution.get("results", {}).get("response", "")

    if report_type == "pdf":
        generate_pdf(final_response or "No response generated.", filename=filename)
    elif report_type == "docx":
        generate_docx(final_response or "No response generated.", filename=filename)
    elif report_type == "xlsx":
        generate_xlsx(execution, query, filename=filename)
    elif report_type == "json":
        generate_json(execution, query, filename=filename)

    session = new_session()
    try:
        repo.register_report(session, run_id, report_type, filename)
    finally:
        session.close()

    return filename
