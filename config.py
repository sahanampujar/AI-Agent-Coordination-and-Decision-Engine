import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PROVIDER
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
).lower().strip()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash-lite",
)


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest",
)


# ============================================================
# CEREBRAS CONFIGURATION
# ============================================================

CEREBRAS_API_KEY = os.getenv(
    "CEREBRAS_API_KEY"
)

CEREBRAS_MODEL = os.getenv(
    "CEREBRAS_MODEL",
    "gpt-oss-120b",
)


# ============================================================
# WORKFLOW / PLATFORM CONFIGURATION
# ============================================================

STEP_TIMEOUT_SECONDS = float(
    os.getenv(
        "STEP_TIMEOUT_SECONDS",
        "180",
    )
)

STEP_MAX_RETRIES = int(
    os.getenv(
        "STEP_MAX_RETRIES",
        "1",
    )
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./enterprise_workflow.db",
)

API_AUTH_TOKEN = os.getenv(
    "API_AUTH_TOKEN",
    "",
)


# ============================================================
# RESPONSE NORMALIZATION
# ============================================================

def normalize_content(content):
    """
    Convert provider-specific content into plain text.
    """

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if isinstance(text, str):
                    text_parts.append(text)

        return "\n".join(
            part.strip()
            for part in text_parts
            if part and part.strip()
        ).strip()

    if isinstance(content, dict):

        text = content.get("text")

        if isinstance(text, str):
            return text.strip()

        nested = content.get("content")

        if nested is not None:
            return normalize_content(nested)

    return str(content).strip()


# ============================================================
# NORMALIZED RESPONSE
# ============================================================

class SimpleResponse:

    def __init__(self, content):
        self.content = normalize_content(content)


# ============================================================
# NORMALIZED LLM WRAPPER
# ============================================================

class NormalizedLLM:

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, prompt, *args, **kwargs):

        response = self.llm.invoke(
            prompt,
            *args,
            **kwargs,
        )

        if hasattr(response, "content"):

            response.content = normalize_content(
                response.content
            )

        else:

            response = SimpleResponse(
                response
            )

        return response

    def __getattr__(self, name):
        return getattr(
            self.llm,
            name,
        )


# ============================================================
# CEREBRAS ADAPTER
# ============================================================

class CerebrasLLM:

    def __init__(
        self,
        api_key,
        model,
    ):

        from cerebras.cloud.sdk import Cerebras

        self.client = Cerebras(
            api_key=api_key
        )

        self.model = model

    def invoke(
        self,
        prompt,
        *args,
        **kwargs,
    ):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": str(prompt),
                }
            ],
            temperature=0,
        )

        content = ""

        if response.choices:

            content = (
                response
                .choices[0]
                .message
                .content
                or ""
            )

        return SimpleResponse(
            content
        )


# ============================================================
# CREATE LLM
# ============================================================

if LLM_PROVIDER == "gemini":

    if not GEMINI_API_KEY:

        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    base_llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        max_output_tokens=512,
    )

    llm = NormalizedLLM(
        base_llm
    )


elif LLM_PROVIDER == "cerebras":

    if not CEREBRAS_API_KEY:

        raise ValueError(
            "CEREBRAS_API_KEY is missing from .env"
        )

    base_llm = CerebrasLLM(
        api_key=CEREBRAS_API_KEY,
        model=CEREBRAS_MODEL,
    )

    llm = NormalizedLLM(
        base_llm
    )


elif LLM_PROVIDER == "ollama":

    base_llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
    )

    llm = NormalizedLLM(
        base_llm
    )


else:

    raise ValueError(
        "Unsupported LLM_PROVIDER: "
        f"{LLM_PROVIDER}. "
        "Choose ollama, gemini, or cerebras."
    )