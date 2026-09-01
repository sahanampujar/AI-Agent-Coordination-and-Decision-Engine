import json


def generate_json(execution: dict, query: str, filename="Business_Report.json"):
    """
    Generate a machine-readable JSON export of a workflow execution,
    for downstream integrations that need structured data rather than
    a document (e.g. feeding another enterprise system, or archiving).
    """

    payload = {
        "query": query,
        "status": execution.get("status"),
        "message": execution.get("message"),
        "run_id": execution.get("run_id"),
        "results": execution.get("results", {}),
        "metrics": execution.get("metrics", {}),
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    return filename
