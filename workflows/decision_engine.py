import re

from config import llm
from core.exceptions import llm_call


VALID_DECISIONS = (
    "APPROVE",
    "REJECT",
    "REVIEW",
    "RECOMMEND",
)


class DecisionEngine:

    def __init__(self):
        self.llm = llm

    def evaluate(self, analysis, query=None):

        # ============================================================
        # FORCE HUMAN REVIEW WHEN EXPLICITLY REQUIRED
        # ============================================================

        query_text = str(
            query or ""
        ).lower()

        analysis_text = str(
            analysis or ""
        ).lower()

        human_review_keywords = [
            "human authorization",
            "human approval",
            "human review",
            "mandatory human",
            "manager approval required",
            "manual approval required",
            "requires human",
        ]

        requires_human_review = any(
            keyword in query_text
            or keyword in analysis_text
            for keyword in human_review_keywords
        )

        if requires_human_review:

            return (
                "DECISION: REVIEW\n"
                "Decision Reason: Human authorization "
                "is explicitly required.\n"
                "Recommended Action: Pause the workflow "
                "for human review.\n"
                "Confidence Level: High"
            )

        # ============================================================
        # NORMAL LLM DECISION
        # ============================================================

        prompt = f"""
You are an Enterprise Decision Automation Agent.

Evaluate the business analysis and select exactly one decision.

User Business Request:
{query if query else "Not provided"}

Business Analysis:
{analysis}

Valid decisions:

- APPROVE
- REJECT
- REVIEW
- RECOMMEND

Rules:

APPROVE:
The proposed action is feasible and benefits clearly
outweigh the risks.

REJECT:
The risks or problems make the action unsuitable.

REVIEW:
Important uncertainty exists or human approval is required.

RECOMMEND:
Provide a recommendation when a final approval/rejection
decision is not appropriate.

Start your response with EXACTLY:

DECISION: <APPROVE|REJECT|REVIEW|RECOMMEND>

Then provide:

Decision Reason:
Key Factors:
Risks:
Recommended Action:
Confidence Level:

Keep the response concise and actionable.
"""

        return llm_call(
            self.llm,
            prompt,
            "Decision Engine"
        )

    @staticmethod
    def parse_decision(
        decision_text: str
    ) -> str:
        """
        Extract APPROVE / REJECT / REVIEW / RECOMMEND
        from the decision response.
        """

        if not decision_text:
            return "RECOMMEND"

        text = str(
            decision_text
        )

        # First look for the structured DECISION line.
        match = re.search(
            r"DECISION\s*:\s*"
            r"(APPROVE|REJECT|REVIEW|RECOMMEND)",
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

        # Fallback for older/non-compliant responses.
        upper_text = text.upper()

        for label in VALID_DECISIONS:

            if label in upper_text:
                return label

        return "RECOMMEND"