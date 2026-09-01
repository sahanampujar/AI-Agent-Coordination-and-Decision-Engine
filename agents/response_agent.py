from config import llm
from prompts.response_prompt import RESPONSE_PROMPT
from core.exceptions import llm_call


class ResponseAgent:

    def generate(self, analysis: str, history=None):

        prompt = ""

        if history:
            prompt += "Previous Conversation:\n"

            for item in history:
                prompt += f"{item['role']}: {item['message']}\n"

            prompt += "\n"

        prompt += RESPONSE_PROMPT.format(analysis=analysis)

        return llm_call(llm, prompt, "Response Agent")
