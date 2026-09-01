from config import llm
from prompts.research_prompt import RESEARCH_PROMPT
from core.exceptions import llm_call


class ResearchAgent:

    def research(self, plan: str, history=None):

        # -------------------------------------------------
        # Build conversation context
        # -------------------------------------------------

        history_text = ""

        if history:

            history_text = "Previous Conversation:\n"

            # Use only recent history to avoid unnecessarily
            # large prompts and improve response speed.
            recent_history = history[-6:]

            for item in recent_history:

                role = item.get("role", "Unknown")
                message = item.get("message", "")

                history_text += f"{role}: {message}\n"

            history_text += "\n"

        # -------------------------------------------------
        # Build research prompt
        # -------------------------------------------------

        prompt = f"""
{history_text}

You are the Research Agent in an Enterprise Workflow Platform.

Business Plan:
{plan}

Your task is to research and summarize the information
required to support the business workflow.

Focus on:
1. Important facts and requirements
2. Relevant business considerations
3. Risks or constraints
4. Useful recommendations

Keep the response concise and structured.

{RESEARCH_PROMPT.format(query=plan)}
"""

        # -------------------------------------------------
        # Call the LLM safely. NOTE: this used to catch its own
        # exceptions and return a descriptive *string* instead of
        # raising. Because that string was non-empty, the workflow
        # executor's truthiness check ("if not research_result")
        # never caught it, so a failed Research step could still be
        # reported as a COMPLETED workflow. llm_call() now always
        # raises AgentExecutionError instead, so the failure is
        # visible and honestly reported end-to-end.
        # -------------------------------------------------

        return llm_call(llm, prompt, "Research Agent")
