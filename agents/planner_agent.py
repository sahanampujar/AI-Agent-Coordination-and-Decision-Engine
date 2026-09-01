from config import llm
from prompts.planner_prompt import PLANNER_PROMPT
from core.exceptions import llm_call


class PlannerAgent:

    def plan(self, query: str, history=None):

        prompt = ""

        if history:
            prompt += "Previous Conversation:\n"

            for item in history:
                prompt += f"{item['role']}: {item['message']}\n"

            prompt += "\n"

        prompt += PLANNER_PROMPT.format(query=query)

        # llm_call() raises AgentExecutionError on empty output or
        # provider failure instead of silently returning something
        # falsy/placeholder-like. This lets workflow_executor.py mark
        # the step as FAILED (and stop the workflow / not report a
        # false success) instead of continuing silently.
        return llm_call(llm, prompt, "Planner Agent")
