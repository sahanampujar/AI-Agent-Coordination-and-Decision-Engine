"""
Shared pytest fixtures.

IMPORTANT: DATABASE_URL is set at *module import time* (before any
test file imports `database.models`), because that module creates its
SQLAlchemy engine at import time from the DATABASE_URL environment
variable. This guarantees tests never touch enterprise_workflow.db.
"""

import os
import sys
import tempfile

os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:latest")

_TMP_DB = os.path.join(tempfile.gettempdir(), "test_enterprise_workflow.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    """
    Drop-in stand-in for config.llm / config.NormalizedLLM.

    Usage:
        fake = FakeLLM(["planner output", "research output", ...])
        fake.invoke("any prompt")  -> FakeResponse("planner output")

    Or raise on a given call:
        fake = FakeLLM([Exception("boom")])
    """

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def invoke(self, prompt, *args, **kwargs):
        self.calls.append(prompt)

        if not self._responses:
            raise RuntimeError("FakeLLM has no more queued responses.")

        next_item = self._responses.pop(0)

        if isinstance(next_item, Exception):
            raise next_item

        return FakeResponse(next_item)


@pytest.fixture
def fake_llm_factory():
    """Returns a constructor so each test can build its own FakeLLM."""
    return FakeLLM


@pytest.fixture(autouse=True)
def _reset_db_between_tests():
    """
    Ensure a clean schema for every test module. Cheap for SQLite;
    keeps tests independent of execution order.
    """
    from database.models import init_db
    init_db()
    yield
