import re


class WorkflowBuilder:

    def __init__(self):
        pass

    def build(self, query):

        query = str(query or "").strip()
        query_lower = query.lower()

        steps = []

        # =========================================================
        # STEP 1: PLANNER
        # =========================================================

        steps.append({
            "step": 1,
            "name": "Planner",
            "type": "Planner",
            "component": "Planner Agent",
            "description":
                "Analyze the business request and create an execution plan.",
        })

        # =========================================================
        # STEP 2: TOOL / RESEARCH
        # =========================================================

        # ---------------------------------------------------------
        # Calculator detection
        # ---------------------------------------------------------
        #
        # Recognize:
        #   22+1
        #   100 / 5
        #   calculate 22+1
        #   calculate total cost
        #   25 * (4+2)
        #
        # The expression check is important because "22+1" does not
        # contain the word "calculate".
        # ---------------------------------------------------------

        calculator_expression = query_lower.replace(
            "calculate",
            ""
        ).strip()

        is_calculation = bool(
            re.fullmatch(
                r"[0-9+\-*/(). %]+",
                calculator_expression
            )
        )

        has_calculation_keyword = any(
            word in query_lower
            for word in [
                "calculate",
                "calculation",
                "cost",
                "price",
                "total",
            ]
        )

        # ---------------------------------------------------------
        # Weather
        # ---------------------------------------------------------

        is_weather = (
            "weather" in query_lower
        )

        # ---------------------------------------------------------
        # File / document
        # ---------------------------------------------------------

        is_file_request = any(
            word in query_lower
            for word in [
                "file",
                "document",
                "pdf",
            ]
        )

        # ---------------------------------------------------------
        # Select tool
        # ---------------------------------------------------------

        if (
            is_calculation
            or has_calculation_keyword
        ):

            steps.append({
                "step": 2,
                "name": "Calculation",
                "type": "Calculator",
                "component": "Calculator Tool",
                "description":
                    "Perform the required calculation.",
            })

        elif is_weather:

            steps.append({
                "step": 2,
                "name": "Weather Check",
                "type": "Weather",
                "component": "Weather Tool",
                "description":
                    "Retrieve relevant weather information.",
            })

        elif is_file_request:

            steps.append({
                "step": 2,
                "name": "Document Processing",
                "type": "File",
                "component": "File Tool",
                "description":
                    "Read and process the requested document.",
            })

        else:

            steps.append({
                "step": 2,
                "name": "Research",
                "type": "Research",
                "component": "Research Agent",
                "description":
                    "Gather relevant information for the business request.",
            })

        # =========================================================
        # STEP 3: ANALYSIS
        # =========================================================

        steps.append({
            "step": 3,
            "name": "Analysis",
            "type": "Analysis",
            "component": "Analysis Agent",
            "description":
                "Analyze the collected information and identify insights.",
        })

        # =========================================================
        # STEP 4: DECISION
        # =========================================================

        steps.append({
            "step": 4,
            "name": "Decision",
            "type": "Decision",
            "component": "Decision Engine",
            "description":
                "Evaluate the analysis and determine the appropriate action.",
        })

        # =========================================================
        # STEP 5: RESPONSE
        # =========================================================

        steps.append({
            "step": 5,
            "name": "Response",
            "type": "Response",
            "component": "Response Agent",
            "description":
                "Generate the final business response.",
        })

        # =========================================================
        # RETURN WORKFLOW
        # =========================================================

        return {
            "workflow_name":
                "Enterprise Automated Workflow",

            "objective":
                query,

            "steps":
                steps,

            "decision_points": [
                "Evaluate business analysis",
                "Determine appropriate business action",
            ],

            "expected_output":
                "Final decision and business response.",
        }