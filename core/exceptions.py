"""
Central exception types + a shared "call the LLM safely" helper.

WHY THIS FILE EXISTS
---------------------
Before this fix, each agent (planner/research/analysis/response) called
`llm.invoke(prompt)` directly and either:

  * returned the raw response with no validation, or
  * (research_agent only) caught errors and returned a *string* describing
    the error instead of raising.

Because a non-empty string is truthy, `workflow_executor.py`'s
`if not research_result: raise RuntimeError(...)` check never fired for
those swallowed errors, so the step was marked COMPLETED, the overall
workflow was marked COMPLETED, and the Streamlit UI showed
"Workflow Completed Successfully!" while the Research tab showed
"Research output was not generated." -- the exact bug described in the
project brief.

The fix: centralize LLM invocation behind `llm_call()`, which always
raises `AgentExecutionError` on empty output or provider failure. Every
agent now uses this helper, and workflow_executor.py's step loop
(unchanged behavior) marks the step FAILED and stops the workflow with a
truthful FAILED status whenever it's raised.
"""

from __future__ import annotations

import time


class AgentExecutionError(Exception):
    """Raised when an agent fails to produce usable output."""

    def __init__(self, agent_name: str, detail: str):
        self.agent_name = agent_name
        self.detail = detail
        super().__init__(f"{agent_name} failed: {detail}")


class ToolExecutionError(Exception):
    """Raised when a tool fails to execute safely."""

    def __init__(self, tool_name: str, detail: str):
        self.tool_name = tool_name
        self.detail = detail
        super().__init__(f"{tool_name} failed: {detail}")


class WorkflowValidationError(Exception):
    """Raised when a workflow definition is structurally invalid."""


class StepTimeoutError(Exception):
    """Raised when a workflow step exceeds its allotted execution time."""


def llm_call(llm, prompt: str, agent_name: str, retries: int = 1, retry_delay: float = 0.6):
    """
    Invoke the configured LLM and return normalized, validated text.

    - Retries transient provider errors up to `retries` times (simple
      linear backoff) before giving up.
    - Always raises AgentExecutionError (never returns a placeholder
      string) if the model errors out or returns empty content, so the
      failure is visible to the workflow executor and cannot silently
      masquerade as a successful step.
    """

    # Local import avoids a circular import at module load time
    # (config.py imports nothing from core, but agents import both).
    from config import normalize_content

    last_error = None

    for attempt in range(retries + 1):
        try:
            response = llm.invoke(prompt)
            content = getattr(response, "content", response)
            content = normalize_content(content)

            if not content or not content.strip():
                raise AgentExecutionError(
                    agent_name,
                    "The model returned an empty response.",
                )

            return content.strip()

        except AgentExecutionError:
            raise

        except Exception as error:  # provider/network/timeout errors
            last_error = error

            if attempt < retries:
                time.sleep(retry_delay)
                continue

            raise AgentExecutionError(agent_name, str(error)) from last_error
