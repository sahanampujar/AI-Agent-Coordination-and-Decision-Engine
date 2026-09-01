from config import llm
from prompts.analysis_prompt import ANALYSIS_PROMPT
from core.exceptions import llm_call


class AnalysisAgent:

    def analyze(self, research: str, history=None):

        prompt = ""

        if history:
            prompt += "Previous Conversation:\n"

            for item in history:
                prompt += f"{item['role']}: {item['message']}\n"

            prompt += "\n"

        prompt += ANALYSIS_PROMPT.format(research=research)

        return llm_call(llm, prompt, "Analysis Agent")
