# Deployment Guide

## 1. Local Development

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env: set LLM_PROVIDER, and either GEMINI_API_KEY or OLLAMA_MODEL
```

Initialize the database (auto-created on first run too, but you can do it explicitly):

```bash
python -c "from database.models import init_db; init_db()"
```

### Start the Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

Opens at http://localhost:8501. The Dashboard and Approvals pages are available
from the left-hand page navigator (Streamlit multipage app).

### Start the REST API

```bash
uvicorn api.main:app --reload --port 8000
```

Docs at http://localhost:8000/docs (FastAPI auto-generated Swagger UI).

Both processes share the same SQLite database file
(`enterprise_workflow.db` by default), so a workflow started through
one is visible in the other.

---

## 2. Environment Variables (.env)

| Variable | Required | Description |
|---|---|---|
| `LLM_PROVIDER` | Yes | `gemini` or `ollama` |
| `GEMINI_API_KEY` | If provider=gemini | Your Gemini API key |
| `GEMINI_MODEL` | No | Defaults to `gemini-2.5-flash-lite` |
| `OLLAMA_MODEL` | If provider=ollama | e.g. `llama3.2:latest` (must be pulled locally: `ollama pull llama3.2`) |
| `STEP_TIMEOUT_SECONDS` | No | Per-step execution timeout (default 60) |
| `STEP_MAX_RETRIES` | No | Retries for transient agent/tool failures (default 1) |
| `DATABASE_URL` | No | SQLAlchemy URL, default `sqlite:///./enterprise_workflow.db` |
| `API_AUTH_TOKEN` | No | If set, REST API write endpoints require `Authorization: Bearer <token>` |
| `REPORTS_OUTPUT_DIR` | No | Where generated reports are saved (default `reports_output/`) |

Never commit `.env` — it's already in `.gitignore`. Use `.env.example` as
the template for new environments.

---

## 3. Database Setup

Default: SQLite file, zero setup. For production, point `DATABASE_URL`
at Postgres (or any SQLAlchemy-supported DB) — no code changes needed:

```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/workflow_db
```

Tables (`users`, `workflows`, `workflow_runs`, `workflow_steps`,
`decisions`, `approvals`, `audit_logs`, `reports`) are created
automatically on startup via `init_db()`.

---

## 4. Docker

```bash
docker compose up --build
```

- Streamlit UI: http://localhost:8501
- REST API: http://localhost:8000
- SQLite DB persists in the `workflow_data` named volume.
- Generated reports persist in `./reports_output` on the host.

Set your `.env` file before building (it's loaded via `env_file` in
`docker-compose.yml`).

---

## 5. Health Check

```bash
curl http://localhost:8000/api/health
```

```json
{"status": "ok", "llm_provider": "ollama", "database": "sqlite:///./enterprise_workflow.db"}
```

Use this endpoint for container/orchestrator liveness checks.

---

## 6. Logging

- Workflow execution events, decisions, and human-review actions are
  written to the `audit_logs` table (queryable via
  `GET /api/audit-logs` or the "Audit Log" tab in Streamlit) — this is
  the primary structured log for compliance/traceability.
- Application-level errors surface in the process stdout/stderr as
  usual; when running under Docker/Compose, view them with
  `docker compose logs -f`.
- For centralized logging in production, forward container stdout to
  your log aggregator of choice (e.g. CloudWatch, Loki, ELK) — no code
  changes required since nothing writes to a local log file today.

---

## 7. Scaling & Performance Notes

- Each agent call goes through `core.exceptions.llm_call()`, which
  retries transient provider errors once by default
  (`STEP_MAX_RETRIES`) before failing the step — tune this and
  `STEP_TIMEOUT_SECONDS` for your provider's latency profile.
- The workflow executor reuses intermediate results (planner output,
  tool output, research, analysis) across subsequent steps rather
  than recomputing them, and research prompts trim conversation
  history to the last 6 turns to keep prompts concise.
- For higher throughput, run multiple `uvicorn` workers:
  `uvicorn api.main:app --workers 4`, and switch `DATABASE_URL` to
  Postgres (SQLite is fine for demos/single-instance use but is not
  ideal for concurrent multi-worker writes).
- Streamlit itself is single-user-per-session by design; the REST API
  is the right integration point for multi-user/automated access.

---

## 8. Security Checklist

- [x] API keys loaded from `.env`, never hardcoded, never logged.
- [x] Calculator tool uses a safe AST-based evaluator (no `eval()`).
- [x] Optional bearer-token auth on all REST API write endpoints
      (`API_AUTH_TOKEN`).
- [x] Input validated at the tool/agent boundary (empty queries,
      malformed workflows rejected with a clear error).
- [ ] Role-based authorization (only a single shared token today —
      add per-user roles if you need reviewer-only approval endpoints
      restricted from general API callers).
- [ ] TLS termination — put this behind a reverse proxy (nginx,
      Caddy, or your cloud load balancer) in production; the app
      itself serves plain HTTP.
