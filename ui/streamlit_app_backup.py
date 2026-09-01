import json
import os
import sys

import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Enterprise Workflow Platform",
    page_icon="🤖",
    layout="wide",
)

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ============================================================
# PROJECT IMPORTS
# ============================================================

from workflows.coordinator import AgentCoordinator
from reports.report_manager import generate_report

from database.models import (
    init_db,
    new_session,
)

from database import repository as repo


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def initialize_session_state():
    defaults = {
        "execution": None,
        "query": "",
        "workflow": None,
        "report_files": {},
        "report_run_id": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# ============================================================
# COORDINATOR
# ============================================================

@st.cache_resource
def get_coordinator():
    return AgentCoordinator()


coordinator = get_coordinator()


# ============================================================
# DATABASE RESTORE
# ============================================================

def restore_latest_execution():
    """
    Restore the latest workflow run from SQLite.

    This is used when Streamlit reruns because the user navigated
    between pages or refreshed the browser.
    """

    session = None

    try:

        session = new_session()

        # ----------------------------------------------------
        # Find latest run
        # ----------------------------------------------------

        if hasattr(repo, "get_latest_run"):

            latest_run = repo.get_latest_run(
                session
            )

        else:

            from database.models import WorkflowRun

            latest_run = (
                session.query(
                    WorkflowRun
                )
                .order_by(
                    WorkflowRun.started_at.desc()
                )
                .first()
            )

        if latest_run is None:

            return None, "", None


        # ----------------------------------------------------
        # Restore results JSON
        # ----------------------------------------------------

        results = {}

        if latest_run.results_json:

            try:

                results = json.loads(
                    latest_run.results_json
                )

            except (
                TypeError,
                ValueError
            ):

                results = {}


        # ----------------------------------------------------
        # Restore workflow definition
        # ----------------------------------------------------

        workflow = None

        if latest_run.workflow:

            try:

                workflow = json.loads(
                    latest_run.workflow.definition_json
                )

            except (
                TypeError,
                ValueError
            ):

                workflow = {
                    "workflow_name":
                        latest_run.workflow.name,

                    "objective":
                        (
                            latest_run.workflow.objective
                            or latest_run.query
                            or ""
                        ),

                    "steps": [],

                    "decision_points": [],

                    "expected_output": "",
                }


        # ----------------------------------------------------
        # Restore step metrics from database
        # ----------------------------------------------------

        metrics = {}

        try:

            steps = repo.list_steps(
                session,
                latest_run.id
            )

        except Exception:

            steps = []


        if steps:

            step_logs = []

            completed_steps = 0
            failed_steps = 0

            total_duration = 0.0

            for step in steps:

                duration = float(
                    step.duration_seconds or 0
                )

                total_duration += duration

                if step.status == "COMPLETED":

                    completed_steps += 1

                elif step.status == "FAILED":

                    failed_steps += 1

                step_logs.append(
                    {
                        "step": step.step_name,
                        "type": step.step_type or "",
                        "status": step.status,
                        "duration_seconds": duration,
                        "error": step.error,
                    }
                )

            total_steps = len(
                step_logs
            )

            success_rate = (
                round(
                    completed_steps
                    / total_steps
                    * 100,
                    2
                )
                if total_steps
                else 0
            )

            metrics = {
                "status":
                    latest_run.status,

                "total_duration_seconds":
                    round(
                        total_duration,
                        3
                    ),

                "total_steps":
                    total_steps,

                "completed_steps":
                    completed_steps,

                "failed_steps":
                    failed_steps,

                "success_rate":
                    success_rate,

                "step_logs":
                    step_logs,
            }


        # ----------------------------------------------------
        # Build execution object
        # ----------------------------------------------------

        execution = {
            "status":
                latest_run.status,

            "message":
                latest_run.message or "",

            "results":
                results,

            "metrics":
                metrics,

            "run_id":
                latest_run.id,
        }

        query = (
            latest_run.query
            or ""
        )

        return (
            execution,
            query,
            workflow
        )

    except Exception as error:

        print(
            "RESTORE ERROR:",
            error
        )

        return (
            None,
            "",
            None
        )

    finally:

        if session is not None:

            session.close()


# ============================================================
# LOAD CURRENT EXECUTION
# ============================================================

def load_current_execution():

    execution = st.session_state.get(
        "execution"
    )

    query = st.session_state.get(
        "query",
        ""
    )

    workflow = st.session_state.get(
        "workflow"
    )

    # --------------------------------------------------------
    # Restore from database if session state is empty.
    # --------------------------------------------------------

    def load_current_execution():

        execution = st.session_state.get(
            "execution"
        )

        query = st.session_state.get(
            "query",
            ""
        )

        workflow = st.session_state.get(
            "workflow"
        )

        if execution is None:

            execution = {
                "status": "IDLE",
                "message": "No workflow has been executed yet.",
                "results": {},
                "metrics": {},
                "run_id": None,
            }

        if workflow is None:

            workflow = {
                "workflow_name": "Enterprise Workflow",
                "objective": query,
                "steps": [],
                "decision_points": [],
                "expected_output": "",
            }

        return (
            execution,
            query,
            workflow,
        )
    # --------------------------------------------------------
    # Empty state
    # --------------------------------------------------------

    if execution is None:

        execution = {
            "status":
                "IDLE",

            "message":
                "No workflow has been executed yet.",

            "results":
                {},

            "metrics":
                {},

            "run_id":
                None,
        }

    if workflow is None:

        workflow = {
            "workflow_name":
                "Enterprise Workflow",

            "objective":
                query,

            "steps":
                [],

            "decision_points":
                [],

            "expected_output":
                "",
        }

    return (
        execution,
        query,
        workflow
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🤖 Enterprise AI"
    )

    st.caption(
        "Workflow Platform v1.0"
    )

    st.markdown(
        "---"
    )

    st.subheader(
        "Project"
    )

    st.write(
        "Enterprise Workflow Platform "
        "with Decision Automation System"
    )

    st.markdown(
        "---"
    )

    st.subheader(
        "AI Model"
    )

    st.success(
        "llama3.2 (Local)"
    )

    st.subheader(
        "System Status"
    )

    st.success(
        "🟢 Online"
    )

    st.markdown(
        "---"
    )

    st.info(
        "Multi-Agent AI + Workflow Automation + "
        "Decision Intelligence"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🤖 Enterprise Workflow Platform"
)

st.markdown(
    """
**Enterprise Workflow Platform with Decision Automation**

Automate business processes using:

- Multi-Agent AI
- Intelligent Tools
- Workflow Automation
- Decision Intelligence
- Memory Management
"""
)


# ============================================================
# LOAD CURRENT STATE
# ============================================================

(
    execution,
    saved_query,
    workflow
) = load_current_execution()


execution_status = execution.get(
    "status",
    "IDLE"
)

execution_message = execution.get(
    "message",
    ""
)

results = execution.get(
    "results",
    {}
)

metrics = execution.get(
    "metrics",
    {}
)

run_id = execution.get(
    "run_id"
)

plan = results.get(
    "planner",
    ""
)

tool_output = results.get(
    "tool",
    ""
)

research = results.get(
    "research",
    ""
)

analysis = results.get(
    "analysis",
    ""
)

decision = results.get(
    "decision",
    ""
)

final_report = results.get(
    "response",
    ""
)

#execution_message = execution.get(
  #  "message",
   # ""
#)

results = execution.get(
    "results",
    {}
)

#metrics = execution.get(
 #   "metrics",
  #  {}
#)

#run_id = execution.get(
 #   "run_id"
#)

#plan = results.get(
 #   "planner",
  #  ""
#)

#tool_output = results.get(
 #   "tool",
  #  ""
#)

research = results.get(
    "research",
    ""
)

analysis = results.get(
    "analysis",
    ""
)

decision = results.get(
    "decision",
    ""
)

final_report = results.get(
    "response",
    ""
)


# ============================================================
# USER INPUT
# ============================================================

query = st.text_area(
    "Enter your business problem",

    value=saved_query,

    height=150,

    placeholder=(
        "Example: Automate employee leave approval workflow"
    ),
)


# ============================================================
# RUN BUTTON
# ============================================================

run_button = st.button(
    "▶ Run Enterprise Workflow",
    use_container_width=True,
)


# ============================================================
# WORKFLOW EXECUTION
# ============================================================
#
# IMPORTANT:
#
# The workflow is executed ONLY when run_button is True.
#
# Dashboard navigation, Approvals navigation, report
# downloads, browser refreshes, etc. must NEVER execute
# the workflow again.
# ============================================================

if run_button:

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    clean_query = query.strip()

    if not clean_query:

        st.warning(
            "Please enter a business problem first."
        )

        st.stop()


    # --------------------------------------------------------
    # Progress UI
    # --------------------------------------------------------

    progress_bar = st.progress(
        0
    )

    status_box = st.empty()


    # --------------------------------------------------------
    # Build workflow
    # --------------------------------------------------------

    status_box.info(
        "🔄 Building Enterprise Workflow..."
    )

    try:

        workflow = (
            coordinator
            .run_workflow_builder(
                clean_query
            )
        )

    except Exception as error:

        progress_bar.progress(
            0
        )

        status_box.error(
            "❌ Workflow generation failed: "
            f"{error}"
        )

        st.exception(
            error
        )

        st.stop()


    # --------------------------------------------------------
    # Validate workflow
    # --------------------------------------------------------

    if not isinstance(
        workflow,
        dict
    ):

        st.error(
            "❌ Invalid workflow returned."
        )

        st.stop()


    steps = workflow.get(
        "steps",
        []
    )

    if not steps:

        st.error(
            "❌ Workflow contains no executable steps."
        )

        st.json(
            workflow
        )

        st.stop()


    progress_bar.progress(
        10
    )


    # --------------------------------------------------------
    # Execute workflow exactly once
    # --------------------------------------------------------

    status_box.info(
        "⚙️ Executing Enterprise Workflow..."
    )

    try:

        execution = (
            coordinator
            .run_workflow(
                clean_query,
                workflow
            )
        )

    except Exception as error:

        progress_bar.progress(
            0
        )

        st.error(
            "❌ Workflow execution failed: "
            f"{error}"
        )

        st.exception(
            error
        )

        st.stop()


    # --------------------------------------------------------
    # Persist current UI state
    # --------------------------------------------------------

    st.session_state.execution = (
        execution
    )

    st.session_state.query = (
        clean_query
    )

    st.session_state.workflow = (
        workflow
    )


    # --------------------------------------------------------
    # Reset report cache for new run
    # --------------------------------------------------------

    new_run_id = execution.get(
        "run_id"
    )

    if (
        st.session_state.report_run_id
        != new_run_id
    ):

        st.session_state.report_files = {}

        st.session_state.report_run_id = (
            None
        )


    progress_bar.progress(
        100
    )

    st.success(
        "Workflow execution finished."
    )


    # --------------------------------------------------------
    # Reload current execution
    # --------------------------------------------------------

    (
        execution,
        saved_query,
        workflow
    ) = load_current_execution()


    execution_status = execution.get(
        "status",
        "IDLE"
    )

    execution_message = execution.get(
        "message",
        ""
    )

    results = execution.get(
        "results",
        {}
    )

    metrics = execution.get(
        "metrics",
        {}
    )

    run_id = execution.get(
        "run_id"
    )

    plan = results.get(
        "planner",
        ""
    )

    tool_output = results.get(
        "tool",
        ""
    )

    research = results.get(
        "research",
        ""
    )

    analysis = results.get(
        "analysis",
        ""
    )

    decision = results.get(
        "decision",
        ""
    )

    final_report = results.get(
        "response",
        ""
    )


# ============================================================
# STATUS BANNER
# ============================================================

if execution_status == "COMPLETED":

    st.success(
        "✅ Workflow Completed Successfully!"
    )

elif execution_status == "PENDING_REVIEW":

    st.warning(
        "⏸️ Workflow Paused — Awaiting Human Review"
    )

    if execution_message:

        st.info(
            execution_message
        )

elif execution_status == "REJECTED":

    st.warning(
        "🚫 Workflow Rejected by Reviewer"
    )

    if execution_message:

        st.info(
            execution_message
        )

elif execution_status == "FAILED":

    st.error(
        "❌ Workflow Execution Failed"
    )

    if execution_message:

        st.error(
            execution_message
        )


# ============================================================
# HUMAN REVIEW
# ============================================================

if (
    execution_status == "PENDING_REVIEW"
    and run_id
):

    st.markdown(
        "### 🧑‍⚖️ Human Review Required"
    )

    st.write(
        "The Decision Engine routed this request "
        "to **REVIEW**. The Response step will not "
        "run until a reviewer approves or rejects it."
    )

    reviewer_name = st.text_input(
        "Reviewer name",
        value="reviewer",
        key=f"reviewer_{run_id}",
    )

    comment = st.text_area(
        "Comment (optional)",
        key=f"comment_{run_id}",
    )

    col_approve, col_reject = st.columns(
        2
    )


    # --------------------------------------------------------
    # APPROVE
    # --------------------------------------------------------

    if col_approve.button(
        "✅ Approve",
        key=f"approve_{run_id}",
    ):

        try:

            resumed = (
                coordinator
                .resume_workflow(
                    run_id,
                    approved=True,
                    resolved_by=(
                        reviewer_name.strip()
                        or "reviewer"
                    ),
                    comment=comment,
                )
            )

            st.session_state.execution = (
                resumed
            )

            st.session_state.query = (
                saved_query
            )

            st.session_state.workflow = (
                workflow
            )

            st.session_state[
                f"resumed_{run_id}"
            ] = resumed

            st.rerun()

        except Exception as error:

            st.error(
                f"Approval failed: {error}"
            )


    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    if col_reject.button(
        "❌ Reject",
        key=f"reject_{run_id}",
    ):

        try:

            resumed = (
                coordinator
                .resume_workflow(
                    run_id,
                    approved=False,
                    resolved_by=(
                        reviewer_name.strip()
                        or "reviewer"
                    ),
                    comment=comment,
                )
            )

            st.session_state.execution = (
                resumed
            )

            st.session_state.query = (
                saved_query
            )

            st.session_state.workflow = (
                workflow
            )

            st.session_state[
                f"resumed_{run_id}"
            ] = resumed

            st.rerun()

        except Exception as error:

            st.error(
                f"Rejection failed: {error}"
            )


# ============================================================
# TABS
# ============================================================

(
    planner_tab,
    tool_tab,
    research_tab,
    analysis_tab,
    decision_tab,
    workflow_tab,
    execution_tab,
    memory_tab,
    shared_tab,
    report_tab,
    audit_tab,
) = st.tabs(
    [
        "🧠 Planner",
        "🛠 Tool",
        "🔍 Research",
        "📊 Analysis",
        "⚖️ Decision",
        "🔄 Workflow",
        "⚙️ Execution",
        "🧠 Memory",
        "🤝 Shared Memory",
        "📄 Final Report",
        "📜 Audit Log",
    ]
)


# ============================================================
# PLANNER
# ============================================================

with planner_tab:

    st.subheader(
        "🧠 Planner Agent"
    )

    if plan:

        st.markdown(
            plan
        )

    else:

        st.info(
            "Planner output was not generated."
        )


# ============================================================
# TOOL
# ============================================================

with tool_tab:

    st.subheader(
        "🛠 Intelligent Tool Execution"
    )

    if tool_output:

        st.write(
            tool_output
        )

    else:

        st.info(
            "No external tool was required "
            "for this workflow."
        )


# ============================================================
# RESEARCH
# ============================================================

with research_tab:

    st.subheader(
        "🔍 Research Agent"
    )

    if research:

        st.markdown(
            research
        )

    else:

        st.info(
            "Research was not required for this workflow."
        )


# ============================================================
# ANALYSIS
# ============================================================

with analysis_tab:

    st.subheader(
        "📊 Analysis Agent"
    )

    if analysis:

        st.markdown(
            analysis
        )

    else:

        st.info(
            "Analysis output was not generated."
        )


# ============================================================
# DECISION
# ============================================================

with decision_tab:

    st.subheader(
        "⚖️ Decision Engine"
    )

    if decision:

        st.markdown(
            decision
        )

    else:

        st.info(
            "Decision was not generated."
        )


    # --------------------------------------------------------
    # Decision branch
    # --------------------------------------------------------

    branch = results.get(
        "decision_branch"
    )

    if branch:

        st.markdown(
            "### 🔀 Decision Branch"
        )

        decision_value = str(
            branch.get(
                "decision",
                "UNKNOWN"
            )
        ).upper()


        if decision_value == "APPROVE":

            st.success(
                "✅ APPROVE"
            )

        elif decision_value == "REJECT":

            st.error(
                "❌ REJECT"
            )

        elif decision_value == "REVIEW":

            st.warning(
                "⚠️ REVIEW REQUIRED"
            )

        else:

            st.info(
                "💡 RECOMMEND"
            )


        st.write(
            "**Action:** "
            + str(
                branch.get(
                    "action",
                    ""
                )
            )
        )

        st.write(
            "**Status:** "
            + str(
                branch.get(
                    "status",
                    ""
                )
            )
        )

        st.write(
            "**Next Step:** "
            + str(
                branch.get(
                    "next_step",
                    ""
                )
            )
        )


# ============================================================
# WORKFLOW
# ============================================================

with workflow_tab:

    st.subheader(
        "🔄 Enterprise Workflow"
    )

    workflow_name = workflow.get(
        "workflow_name",
        "Enterprise Workflow"
    )

    st.markdown(
        f"### {workflow_name}"
    )

    st.write(
        workflow.get(
            "objective",
            saved_query
        )
    )

    st.markdown(
        "### Execution Steps"
    )

    for step in workflow.get(
        "steps",
        []
    ):

        step_number = step.get(
            "step",
            ""
        )

        step_name = step.get(
            "name",
            ""
        )

        step_type = step.get(
            "type",
            ""
        )

        component = step.get(
            "component",
            ""
        )

        description = step.get(
            "description",
            ""
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"**Step {step_number} — {step_name}**"
            )

            st.write(
                f"Type: `{step_type}`"
            )

            st.write(
                f"Component: `{component}`"
            )

            if description:

                st.caption(
                    description
                )


    st.markdown(
        "### ⚖️ Decision Points"
    )

    decision_points = workflow.get(
        "decision_points",
        []
    )

    if decision_points:

        for point in decision_points:

            st.write(
                f"• {point}"
            )

    else:

        st.info(
            "No explicit decision points."
        )


    st.markdown(
        "### 🎯 Expected Output"
    )

    st.write(
        workflow.get(
            "expected_output",
            ""
        )
    )


# ============================================================
# EXECUTION
# ============================================================

with execution_tab:

    st.subheader(
        "⚙️ Workflow Execution"
    )


    if execution_status == "COMPLETED":

        st.success(
            "✅ Workflow executed successfully!"
        )

    elif execution_status == "PENDING_REVIEW":

        st.warning(
            "⏸️ Workflow is waiting for human review."
        )

    elif execution_status == "REJECTED":

        st.warning(
            "🚫 Workflow was rejected."
        )

    elif execution_status == "FAILED":

        st.error(
            "❌ Workflow execution failed."
        )

    else:

        st.info(
            "No workflow has been executed yet."
        )


    if execution_message:

        st.write(
            execution_message
        )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    if metrics:

        st.markdown(
            "### 📈 Workflow Metrics"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Total Steps",
            metrics.get(
                "total_steps",
                0
            )
        )

        col2.metric(
            "Completed",
            metrics.get(
                "completed_steps",
                0
            )
        )

        col3.metric(
            "Failed",
            metrics.get(
                "failed_steps",
                0
            )
        )

        col4.metric(
            "Success Rate",
            f"{metrics.get('success_rate', 0)}%"
        )

        st.metric(
            "Execution Time",
            f"{metrics.get('total_duration_seconds', 0)} seconds"
        )


        # ----------------------------------------------------
        # Step logs
        # ----------------------------------------------------

        st.markdown(
            "### 📝 Step Execution Log"
        )

        for log in metrics.get(
            "step_logs",
            []
        ):

            log_step = log.get(
                "step",
                "Unknown"
            )

            log_type = log.get(
                "type",
                ""
            )

            log_status = log.get(
                "status",
                ""
            )

            duration = log.get(
                "duration_seconds",
                0
            )

            error = log.get(
                "error"
            )

            if log_status == "COMPLETED":

                st.success(
                    f"✅ {log_step} "
                    f"({log_type}) — "
                    f"{duration} sec"
                )

            elif log_status == "FAILED":

                st.error(
                    f"❌ {log_step} "
                    f"({log_type}) — "
                    f"{error or 'Unknown error'}"
                )

            else:

                st.warning(
                    f"⚠️ {log_step} "
                    f"({log_type}) — "
                    f"{log_status}"
                )


    # --------------------------------------------------------
    # Execution results
    # --------------------------------------------------------

    st.markdown(
        "### 📋 Execution Results"
    )

    if results:

        for name, result in (
            results.items()
        ):

            if name == "decision_branch":

                continue

            display_name = (
                str(name)
                .replace(
                    "_",
                    " "
                )
                .title()
            )

            st.markdown(
                f"#### {display_name}"
            )

            if isinstance(
                result,
                (dict, list)
            ):

                st.json(
                    result
                )

            else:

                st.write(
                    result
                )

            st.markdown(
                "---"
            )

    else:

        st.info(
            "No execution results available."
        )


# ============================================================
# MEMORY
# ============================================================

with memory_tab:

    st.subheader(
        "🧠 Conversation Memory"
    )

    try:

        history = (
            coordinator
            .long_term_memory
            .load()
        )

    except Exception:

        history = []


    if history:

        for item in history:

            role = item.get(
                "role",
                "Unknown"
            )

            message = item.get(
                "message",
                ""
            )

            st.markdown(
                f"**{role}**"
            )

            st.write(
                message
            )

            st.markdown(
                "---"
            )

    else:

        st.info(
            "No conversation history available."
        )


# ============================================================
# SHARED MEMORY
# ============================================================

with shared_tab:

    st.subheader(
        "🤝 Shared Memory"
    )

    try:

        shared_data = (
            coordinator
            .shared_memory
            .get_all()
        )

    except Exception:

        shared_data = {}


    if shared_data:

        for key, value in (
            shared_data.items()
        ):

            display_key = (
                str(key)
                .replace(
                    "_",
                    " "
                )
                .title()
            )

            st.markdown(
                f"### {display_key}"
            )

            if isinstance(
                value,
                (dict, list)
            ):

                st.json(
                    value
                )

            else:

                st.write(
                    value
                )

            st.markdown(
                "---"
            )

    else:

        st.info(
            "Shared memory is empty."
        )


# ============================================================
# FINAL REPORT
# ============================================================

with report_tab:

    st.subheader(
        "📄 Final Business Report"
    )

    if final_report:

        st.markdown(
            final_report
        )

        st.markdown(
            "#### 📥 Download Report"
        )

        format_labels = {
            "pdf": (
                "📄 PDF",
                "application/pdf",
            ),

            "docx": (
                "📝 Word (.docx)",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),

            "xlsx": (
                "📊 Excel (.xlsx)",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),

            "json": (
                "🗂️ JSON",
                "application/json",
            ),
        }


        # ----------------------------------------------------
        # Generate reports only once per run
        # ----------------------------------------------------

        if run_id:

            stored_run_id = (
                st.session_state.report_run_id
            )

            if stored_run_id != run_id:

                st.session_state.report_files = {}

                for report_type in (
                    format_labels
                ):

                    try:

                        file_path = (
                            generate_report(
                                execution,
                                saved_query,
                                report_type
                            )
                        )

                        st.session_state.report_files[
                            report_type
                        ] = file_path

                    except Exception as error:

                        st.session_state.report_files[
                            report_type
                        ] = None

                        st.warning(
                            f"{report_type.upper()} "
                            f"generation failed: "
                            f"{error}"
                        )

                st.session_state.report_run_id = (
                    run_id
                )


        # ----------------------------------------------------
        # Download buttons
        # ----------------------------------------------------

        download_cols = st.columns(
            4
        )

        for col, item in zip(
            download_cols,
            format_labels.items()
        ):

            report_type = item[0]

            label = item[1][0]

            mime = item[1][1]

            file_path = (
                st.session_state
                .get(
                    "report_files",
                    {}
                )
                .get(
                    report_type
                )
            )

            with col:

                if (
                    file_path
                    and os.path.exists(
                        file_path
                    )
                ):

                    try:

                        with open(
                            file_path,
                            "rb"
                        ) as file:

                            file_data = file.read()


                        st.download_button(
                            label=label,

                            data=file_data,

                            file_name=os.path.basename(
                                file_path
                            ),

                            mime=mime,

                            key=(
                                "download_"
                                f"{report_type}_"
                                f"{run_id}"
                            ),

                            use_container_width=True,

                            # Do NOT rerun workflow
                            on_click="ignore",
                        )

                    except Exception as error:

                        st.warning(
                            f"{report_type.upper()} "
                            f"download unavailable: "
                            f"{error}"
                        )

                else:

                    st.info(
                        f"{label} not available"
                    )

    else:

        st.info(
            "Final response was not generated."
        )


# ============================================================
# AUDIT LOG
# ============================================================

with audit_tab:

    st.subheader(
        "📜 Audit Log"
    )

    st.caption(
        "Every workflow start, step, decision, "
        "and human review action is recorded "
        "here with a timestamp and user for "
        "compliance/traceability."
    )

    if run_id:

        session = None

        try:

            session = new_session()

            logs = repo.list_audit_logs(
                session,
                run_id=run_id
            )

        except Exception as error:

            logs = []

            st.warning(
                f"Could not load audit log: {error}"
            )

        finally:

            if session is not None:

                session.close()


        if logs:

            st.dataframe(
                [
                    {
                        "Timestamp":
                            log.timestamp,

                        "Step":
                            log.step,

                        "Status":
                            log.status,

                        "Decision":
                            log.decision,

                        "User":
                            log.user,

                        "Error":
                            log.error,
                    }

                    for log in logs
                ],

                use_container_width=True,
            )

        else:

            st.info(
                "No audit log entries for "
                "this run yet."
            )

    else:

        st.info(
            "No workflow run available."
        )