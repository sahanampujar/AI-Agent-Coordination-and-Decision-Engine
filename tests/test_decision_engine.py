import pytest

from workflows.decision_engine import DecisionEngine
from core.exceptions import AgentExecutionError


def test_parse_decision_from_structured_line():
    text = "DECISION: APPROVE\n\nReasoning: looks good."
    assert DecisionEngine.parse_decision(text) == "APPROVE"


def test_parse_decision_case_insensitive():
    text = "decision: review\nNeeds a second look."
    assert DecisionEngine.parse_decision(text) == "REVIEW"


def test_parse_decision_falls_back_to_keyword_search():
    text = "Given the risk profile, this should be REJECTED. REJECT."
    assert DecisionEngine.parse_decision(text) == "REJECT"


def test_parse_decision_defaults_to_recommend_when_unclear():
    assert DecisionEngine.parse_decision("Not sure what to do here.") == "RECOMMEND"


def test_parse_decision_handles_empty_input():
    assert DecisionEngine.parse_decision("") == "RECOMMEND"


def test_decision_engine_evaluate_raises_on_llm_failure(monkeypatch, fake_llm_factory):
    engine = DecisionEngine()
    fake = fake_llm_factory([RuntimeError("provider down")])
    monkeypatch.setattr(engine, "llm", fake)

    with pytest.raises(AgentExecutionError):
        engine.evaluate("some analysis", "some query")
