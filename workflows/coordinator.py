from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.response_agent import ResponseAgent

from tools.tool_selector import ToolSelector

from memory.conversation_memory import ConversationMemory
from memory.shared_memory import SharedMemory
from memory.long_term_memory import LongTermMemory

from workflows.decision_engine import DecisionEngine
from workflows.workflow_builder import WorkflowBuilder
from workflows.workflow_executor import WorkflowExecutor


class AgentCoordinator:

    def __init__(self):

        # =====================================================
        # AGENTS
        # =====================================================

        self.planner = PlannerAgent()
        self.research = ResearchAgent()
        self.analysis = AnalysisAgent()
        self.response = ResponseAgent()

        # =====================================================
        # TOOLS
        # =====================================================

        self.tool_selector = ToolSelector()

        # =====================================================
        # MEMORY
        # =====================================================

        self.memory = ConversationMemory()
        self.shared_memory = SharedMemory()
        self.long_term_memory = LongTermMemory()

        # =====================================================
        # DECISION + WORKFLOW
        # =====================================================

        self.decision_engine = DecisionEngine()
        self.workflow_builder = WorkflowBuilder()

    # =========================================================
    # PLANNER
    # =========================================================

    def run_planner(self, query):

        self.memory.add_message(
            "User",
            query
        )

        self.long_term_memory.save(
            "User",
            query
        )

        history = self.memory.get_history()

        plan = self.planner.plan(
            query,
            history
        )

        if plan is None:
            plan = ""

        plan = str(plan)

        self.memory.add_message(
            "Planner",
            plan
        )

        self.long_term_memory.save(
            "Planner",
            plan
        )

        self.shared_memory.save(
            "plan",
            plan
        )

        return plan

    # =========================================================
    # TOOL
    # =========================================================

    def run_tool(self, query):

        tool_output = self.tool_selector.execute(
            query
        )

        if tool_output is None:
            tool_output = ""

        tool_output = str(
            tool_output
        )

        self.memory.add_message(
            "Tool",
            tool_output
        )

        self.long_term_memory.save(
            "Tool",
            tool_output
        )

        self.shared_memory.save(
            "tool",
            tool_output
        )

        return tool_output

    # =========================================================
    # RESEARCH
    # =========================================================

    def run_research(self, plan):

        history = self.memory.get_history()

        research = self.research.research(
            plan,
            history
        )

        if research is None:
            research = ""

        research = str(
            research
        )

        self.memory.add_message(
            "Research",
            research
        )

        self.long_term_memory.save(
            "Research",
            research
        )

        self.shared_memory.save(
            "research",
            research
        )

        return research

    # =========================================================
    # ANALYSIS
    # =========================================================

    def run_analysis(self, research):

        history = self.memory.get_history()

        analysis = self.analysis.analyze(
            research,
            history
        )

        if analysis is None:
            analysis = ""

        analysis = str(
            analysis
        )

        self.memory.add_message(
            "Analysis",
            analysis
        )

        self.long_term_memory.save(
            "Analysis",
            analysis
        )

        self.shared_memory.save(
            "analysis",
            analysis
        )

        return analysis

    # =========================================================
    # DECISION
    # =========================================================

    def run_decision(
        self,
        analysis,
        query=None
    ):

        decision = self.decision_engine.evaluate(
            analysis,
            query
        )

        if decision is None:
            decision = ""

        decision = str(
            decision
        )

        self.memory.add_message(
            "Decision",
            decision
        )

        self.long_term_memory.save(
            "Decision",
            decision
        )

        self.shared_memory.save(
            "decision",
            decision
        )

        return decision

    # =========================================================
    # RESPONSE
    # =========================================================

    def run_response(self, analysis):

        history = self.memory.get_history()

        response = self.response.generate(
            analysis,
            history
        )

        if response is None:
            response = ""

        response = str(
            response
        )

        self.memory.add_message(
            "Response",
            response
        )

        self.long_term_memory.save(
            "Response",
            response
        )

        self.shared_memory.save(
            "response",
            response
        )

        return response

    # =========================================================
    # WORKFLOW BUILDER
    # =========================================================

    def run_workflow_builder(self, query):

        workflow = self.workflow_builder.build(
            query
        )

        if workflow is None:
            workflow = {}

        self.memory.add_message(
            "Workflow Builder",
            str(workflow)
        )

        self.long_term_memory.save(
            "Workflow Builder",
            str(workflow)
        )

        self.shared_memory.save(
            "workflow",
            workflow
        )

        return workflow

    # =========================================================
    # WORKFLOW EXECUTION
    # =========================================================

    def run_workflow(
        self,
        query,
        workflow,
        user="anonymous"
    ):

        executor = WorkflowExecutor(
            self
        )

        # Keep a reference so a paused (PENDING_REVIEW) run can later
        # be resumed via self.resume_workflow() without rebuilding a
        # new executor instance.
        self._last_executor = executor

        execution = executor.execute(
            query,
            workflow,
            user=user
        )

        if execution is None:
            execution = {
                "status": "FAILED",
                "message": "Workflow returned no result.",
                "results": {},
                "metrics": {}
            }

        # -----------------------------------------------------
        # Save complete execution
        # -----------------------------------------------------

        self.shared_memory.save(
            "workflow_execution",
            execution
        )

        self.long_term_memory.save(
            "Workflow Execution",
            str(execution)
        )

        self.memory.add_message(
            "Workflow Execution",
            str(execution)
        )

        return execution

    # =========================================================
    # RESUME AFTER HUMAN REVIEW
    # =========================================================

    def resume_workflow(self, run_id, approved, resolved_by="reviewer", comment=""):
        """
        Resume a workflow that is paused in PENDING_REVIEW after a
        human approves or rejects it. Human-in-the-loop support
        (Module I). Safe to call even if run_workflow() was executed
        by a different coordinator/process instance (e.g. from the
        REST API or a fresh Streamlit session), since PENDING_REVIEW
        state and context are persisted in the database, not held in
        memory.
        """

        executor = WorkflowExecutor(self)
        return executor.resume(
            run_id,
            approved,
            resolved_by=resolved_by,
            comment=comment
        )