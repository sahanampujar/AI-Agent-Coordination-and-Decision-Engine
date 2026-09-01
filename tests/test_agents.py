import pytest

from core.exceptions import AgentExecutionError


def test_planner_agent_success(monkeypatch, fake_llm_factory):
    from agents.planner_agent import PlannerAgent

    fake = fake_llm_factory(["Plan: do the thing."])
    monkeypatch.setattr("agents.planner_agent.llm", fake)

    result = PlannerAgent().plan("Automate employee leave approval")
    assert result == "Plan: do the thing."


def test_planner_agent_raises_on_empty_output(monkeypatch, fake_llm_factory):
    from agents.planner_agent import PlannerAgent

    fake = fake_llm_factory(["   "])  # whitespace-only -> treated as empty
    monkeypatch.setattr("agents.planner_agent.llm", fake)

    with pytest.raises(AgentExecutionError):
        PlannerAgent().plan("Automate employee leave approval")


def test_research_agent_raises_instead_of_returning_placeholder_string(monkeypatch, fake_llm_factory):
    """
    This is the regression test for the exact bug described in the
    project brief: the Research Agent used to catch its own errors
    and return a *string* ("Research output was not generated.")
    instead of raising, which the workflow executor's truthiness
    check couldn't detect. Now it must raise.
    """
    from agents.research_agent import ResearchAgent

    fake = fake_llm_factory([RuntimeError("simulated provider outage")])
    monkeypatch.setattr("agents.research_agent.llm", fake)

    with pytest.raises(AgentExecutionError):
        ResearchAgent().research("Some plan")


def test_research_agent_success(monkeypatch, fake_llm_factory):
    from agents.research_agent import ResearchAgent

    fake = fake_llm_factory(["Research findings here."])
    monkeypatch.setattr("agents.research_agent.llm", fake)

    result = ResearchAgent().research("Some plan")
    assert result == "Research findings here."


def test_analysis_agent_raises_on_provider_error(monkeypatch, fake_llm_factory):
    from agents.analysis_agent import AnalysisAgent

    fake = fake_llm_factory([RuntimeError("timeout")])
    monkeypatch.setattr("agents.analysis_agent.llm", fake)

    with pytest.raises(AgentExecutionError):
        AnalysisAgent().analyze("Some research")


def test_response_agent_success(monkeypatch, fake_llm_factory):
    from agents.response_agent import ResponseAgent

    fake = fake_llm_factory(["Final response text."])
    monkeypatch.setattr("agents.response_agent.llm", fake)

    result = ResponseAgent().generate("Some analysis")
    assert result == "Final response text."


def test_llm_call_retries_then_succeeds(monkeypatch, fake_llm_factory):
    from core.exceptions import llm_call

    fake = fake_llm_factory([RuntimeError("flaky"), "recovered output"])
    monkeypatch.setattr("time.sleep", lambda *_: None)  # skip real backoff delay

    result = llm_call(fake, "prompt", "Test Agent", retries=1, retry_delay=0)
    assert result == "recovered output"
    assert len(fake.calls) == 2
