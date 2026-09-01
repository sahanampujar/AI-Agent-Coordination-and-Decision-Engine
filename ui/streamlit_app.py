import json
import os
import sys
#from tkinter import font
#from textwrap import dedent
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
# PREMIUM BLACK + GOLD THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    /* ========================================================
    BLACK + GOLDEN SMOKE BACKGROUND
    ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 20%,
                rgba(255, 215, 0, 0.16),
                transparent 22%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(212, 175, 55, 0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(255, 193, 7, 0.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 20% 85%,
                rgba(218, 165, 32, 0.08),
                transparent 24%
            ),
            linear-gradient(
                135deg,
                #020202 0%,
                #080808 45%,
                #030303 100%
            ) !important;

        background-attachment: fixed !important;
        color: #FFFFFF !important;
    }

    /* ========================================================
    GOLDEN FOG / SMOKE EFFECT
    ======================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: -20%;
        pointer-events: none;
        z-index: 0;

        background:
            radial-gradient(
                ellipse at 25% 30%,
                rgba(255, 215, 0, 0.07),
                transparent 30%
            ),
            radial-gradient(
                ellipse at 75% 20%,
                rgba(212, 175, 55, 0.06),
                transparent 32%
            ),
            radial-gradient(
                ellipse at 65% 80%,
                rgba(255, 193, 7, 0.05),
                transparent 30%
            );

        filter: blur(55px);
        opacity: 0.9;
    }

    .stApp > * {
        position: relative;
        z-index: 1;
    }

    /* Main page title */
    .stApp [data-testid="stMarkdownContainer"] > h1:first-child {
        text-align: center !important;
        color: #D4AF37 !important;
        text-shadow: 0 0 18px rgba(212, 175, 55, 0.25);
    }

    /* Subtitle */
    .stApp [data-testid="stMarkdownContainer"] > h2 {
        text-align: center !important;
        color: #FFFFFF !important;
        letter-spacing: 2px !important;
    }

    /* Feature line */
    .stApp [data-testid="stMarkdownContainer"] > p {
        text-align: center !important;
        color: #B8B8B8 !important;
    }

    /* ========================================================
       MAIN CONTENT
       ======================================================== */

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ========================================================
       HEADINGS
       ======================================================== */

    h1 {
        font-family: "Times New Roman", Times, serif !important;
        color: #D4AF37 !important;
        font-size: 48px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-align: center !important;

        text-shadow:
            0 0 8px rgba(212, 175, 55, 0.20),
            0 0 22px rgba(212, 175, 55, 0.10) !important;
    }

    h2 {
        font-family: "Times New Roman", Times, serif !important;
        color: #F5F5F5 !important;
        font-size: 25px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-align: center !important;
    }

    h3 {
        font-family: "Times New Roman", Times, serif !important;
        color: #D4AF37 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    p {
        font-family: "Times New Roman", Times, serif !important;
        color: #E5E5E5 !important;
    }

    .stApp [data-testid="stMarkdownContainer"] p {
        font-family: "Times New Roman", Times, serif !important;
    }
    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #080808 !important;
        border-right: 1px solid #3A2F10 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #D4AF37 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #E8E8E8 !important;
    }

    /* ========================================================
    SIDEBAR BRANDING
    ======================================================== */

    section[data-testid="stSidebar"] h1 {
        font-size: 30px !important;
        line-height: 1.1 !important;
        letter-spacing: 1px !important;
        text-transform: none !important;
        color: #D4AF37 !important;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 20px !important;
        color: #D4AF37 !important;
    }

    /* ========================================================
       TEXT INPUTS
       ======================================================== */

    textarea {
        background: rgba(10, 10, 10, 0.90) !important;
        color: #FFFFFF !important;

        border: 1px solid rgba(212, 175, 55, 0.55) !important;
        border-radius: 14px !important;

        font-family: "Times New Roman", Times, serif !important;
        font-size: 18px !important;

        box-shadow:
            inset 0 0 20px rgba(212, 175, 55, 0.03) !important;
    }

    textarea:focus {
        border: 1px solid #FFD700 !important;

        box-shadow:
            0 0 15px rgba(212, 175, 55, 0.20) !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        background: linear-gradient(
            135deg,
            #B8860B,
            #D4AF37 45%,
            #FFD700
        ) !important;

        color: #000000 !important;

        border: 1px solid #FFD700 !important;
        border-radius: 12px !important;

        font-family: "Times New Roman", Times, serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;

        min-height: 52px !important;

        box-shadow:
            0 0 20px rgba(212, 175, 55, 0.20) !important;
    }

    .stButton > button p,
    .stButton > button span {
        color: #000000 !important;
        font-family: "Times New Roman", Times, serif !important;
        font-weight: 700 !important;
    }

    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        font-family: "Times New Roman", Times, serif !important;
        color: #C0C0C0 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFD700 !important;
    }

    div[data-baseweb="tab-highlight"] {
        background-color: #D4AF37 !important;
        height: 3px !important;
    }
    /* ========================================================
       METRIC CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background: #111111 !important;
        border: 1px solid #3A2F10 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow:
            0 4px 18px rgba(0, 0, 0, 0.35) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #AFAFAF !important;
    }

    div[data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-family: "Times New Roman", Times, serif !important;
        font-weight: 700 !important;
    }

    /* ========================================================
    PREMIUM GLASS CARDS
    ======================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(17, 17, 17, 0.78) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        border-radius: 16px !important;

        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.45),
            inset 0 1px 0 rgba(255, 215, 0, 0.05) !important;

        backdrop-filter: blur(12px) !important;
    }
    /* ========================================================
       INFO / SUCCESS / WARNING / ERROR
       ======================================================== */

    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        font-family: "Times New Roman", Times, serif !important;
    }

    /* ========================================================
       DATAFRAME
       ======================================================== */

    div[data-testid="stDataFrame"] {
        border: 1px solid #3A2F10 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ========================================================
       CODE / JSON
       ======================================================== */

    pre,
    code {
        background: #0D0D0D !important;
        color: #F5E6A8 !important;
        border: 1px solid #33290E !important;
    }

    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #3A2F10 !important;
    }

    /* ========================================================
       DOWNLOAD BUTTONS
       ======================================================== */

    div[data-testid="stDownloadButton"] > button {
        background: #111111 !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 10px !important;
        font-family: "Times New Roman", Times, serif !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        background: #D4AF37 !important;
        color: #050505 !important;
        box-shadow:
            0 0 14px rgba(212, 175, 55, 0.30) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
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

    execution = st.session_state.get("execution")
    query = st.session_state.get("query", "")
    workflow = st.session_state.get("workflow")

    # --------------------------------------------------------
    # CASE 1: Current session already has a workflow
    # --------------------------------------------------------

    if workflow is not None and execution is not None:
        return execution, query, workflow

    # --------------------------------------------------------
    # CASE 2: There is no active session workflow
    # --------------------------------------------------------

    if execution is None:

        execution = {
            "status": "IDLE",
            "message": "No workflow has been executed yet.",
            "results": {},
            "metrics": {},
            "run_id": None,
        }

    # --------------------------------------------------------
    # CASE 3: No workflow definition exists
    # --------------------------------------------------------

    if workflow is None:

        workflow = {
            "workflow_name": "Enterprise Workflow",
            "objective": query,
            "steps": [],
            "decision_points": [],
            "expected_output": "",
        }

    return execution, query, workflow
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
# PREMIUM BLACK + GOLD HEADER
# ============================================================

st.markdown(
    "# ✦ ENTERPRISE WORKFLOW PLATFORM "
)

st.markdown(
    "## AI-POWERED BUSINESS AUTOMATION"
)

st.markdown(
    "Multi-Agent AI  •  Intelligent Tools  •  "
    "Decision Intelligence  •  Human-in-the-Loop"
)

st.divider()
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

    st.markdown("# 🧠 PLANNER AGENT")

    st.markdown("---")

    if plan:

        st.markdown(
            "### ✦ Execution Plan"
        )

        st.markdown(plan)

    else:

        st.info(
            "Planner output will appear here after "
            "you run a workflow."
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

    st.markdown("# 🔍 RESEARCH AGENT")

    st.markdown("---")

    if research:

        st.markdown(
            "### ✦ Research Findings"
        )

        st.markdown(research)

    else:

        st.info(
            "Research output will appear here after "
            "you run a workflow."
        )


# ============================================================
# ANALYSIS
# ============================================================

with analysis_tab:

    st.markdown("# 📊 ANALYSIS AGENT")

    st.markdown("---")

    if analysis:

        st.markdown(
            "### ✦ Business Analysis"
        )

        st.markdown(analysis)

    else:

        st.info(
            "Analysis output will appear here after "
            "you run a workflow."
        )

# ============================================================
# DECISION ENGINE
# ============================================================

with decision_tab:

    st.markdown("# ⚖ DECISION ENGINE")

    if decision:

        st.markdown("### ✦ AI DECISION OUTPUT")

        st.markdown("---")

        # Display the decision text normally.
        # This avoids raw HTML being interpreted as code.
        st.markdown(decision)

    else:

        st.info(
            "No decision has been generated yet."
        )

    # ========================================================
    # DECISION BRANCH
    # ========================================================

    branch = results.get("decision_branch")

    if branch:

        decision_value = str(
            branch.get(
                "decision",
                "UNKNOWN"
            )
        ).upper()

        st.markdown("---")

        st.markdown(
            "### ✦ FINAL DECISION"
        )

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
                "⚠️ HUMAN REVIEW REQUIRED"
            )

        else:

            st.info(
                "💡 RECOMMEND"
            )

        # ====================================================
        # DECISION DETAILS
        # ====================================================

        st.markdown(
            "### ✦ Decision Details"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**ACTION**")

            st.write(
                branch.get(
                    "action",
                    ""
                )
            )

        with col2:

            st.markdown("**STATUS**")

            st.write(
                branch.get(
                    "status",
                    ""
                )
            )

        st.markdown("**NEXT STEP**")

        st.write(
            branch.get(
                "next_step",
                ""
            )
        )

# ============================================================
# WORKFLOW
# ============================================================

with workflow_tab:

    st.markdown("# 🔄 WORKFLOW")

    workflow_name = workflow.get(
        "workflow_name",
        ""
    )

    workflow_steps = workflow.get(
        "steps",
        []
    )

    if workflow_steps:

        st.markdown(
            f"### ✦ {workflow_name}"
        )

        st.markdown("---")

        st.markdown(
            "### Workflow Objective"
        )

        st.write(
            workflow.get(
                "objective",
                saved_query
            )
        )

        st.markdown(
            "### ✦ EXECUTION PIPELINE"
        )

        for index, step in enumerate(
            workflow_steps
        ):

            step_number = step.get(
                "step",
                index + 1
            )

            step_name = step.get(
                "name",
                "Unknown Step"
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

            st.markdown(
                f"**{step_number}. {step_name}**"
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

            if index < len(workflow_steps) - 1:
                st.markdown("↓")

        st.markdown("---")

        st.markdown(
            "### ⚖ Decision Points"
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

    else:

        st.info(
            "No workflow has been created yet. "
            "Enter a business problem and click "
            "'Run Enterprise Workflow'."
        )

# ============================================================
# EXECUTION
# ============================================================

with execution_tab:

    st.markdown("# ⚙ WORKFLOW EXECUTION")

    st.markdown("---")

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if execution_status == "COMPLETED":

        st.success(
            "✅ WORKFLOW COMPLETED SUCCESSFULLY"
        )

    elif execution_status == "PENDING_REVIEW":

        st.warning(
            "⏸ WORKFLOW PAUSED — HUMAN REVIEW REQUIRED"
        )

    elif execution_status == "REJECTED":

        st.warning(
            "🚫 WORKFLOW REJECTED BY REVIEWER"
        )

    elif execution_status == "FAILED":

        st.error(
            "❌ WORKFLOW EXECUTION FAILED"
        )

    else:

        st.info(
            "No workflow has been executed yet."
        )

    if execution_message:

        st.write(execution_message)

    # --------------------------------------------------------
    # Workflow metrics
    # --------------------------------------------------------

    if metrics:

        st.markdown(
            "### ✦ EXECUTION METRICS"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "TOTAL STEPS",
                metrics.get("total_steps", 0)
            )

        with col2:
            st.metric(
                "COMPLETED",
                metrics.get("completed_steps", 0)
            )

        with col3:
            st.metric(
                "FAILED",
                metrics.get("failed_steps", 0)
            )

        with col4:
            st.metric(
                "SUCCESS RATE",
                f"{metrics.get('success_rate', 0)}%"
            )

        st.markdown(
            "### ✦ TOTAL EXECUTION TIME"
        )

        st.metric(
            "Duration",
            f"{metrics.get('total_duration_seconds', 0)} seconds"
        )

        # ----------------------------------------------------
        # Step execution pipeline
        # ----------------------------------------------------

        st.markdown(
            "### ✦ STEP EXECUTION PIPELINE"
        )

        step_logs = metrics.get(
            "step_logs",
            []
        )

        if step_logs:

            for index, log in enumerate(step_logs):

                step_name = log.get(
                    "step",
                    "Unknown"
                )

                step_type = log.get(
                    "type",
                    ""
                )

                status = log.get(
                    "status",
                    "UNKNOWN"
                )

                duration = log.get(
                    "duration_seconds",
                    0
                )

                error = log.get(
                    "error"
                )

                if status == "COMPLETED":

                    st.success(
                        f"✅ {step_name}  •  "
                        f"{duration} sec"
                    )

                elif status == "FAILED":

                    st.error(
                        f"❌ {step_name}  •  "
                        f"{error or 'Unknown error'}"
                    )

                else:

                    st.warning(
                        f"⚠️ {step_name}  •  "
                        f"{status}"
                    )

                if index < len(step_logs) - 1:
                    st.markdown("↓")

        else:

            st.info(
                "No execution steps are available yet."
            )

    # --------------------------------------------------------
    # Execution results
    # --------------------------------------------------------

    st.markdown(
        "### ✦ EXECUTION RESULTS"
    )

    if results:

        for name, result in results.items():

            if name == "decision_branch":
                continue

            display_name = (
                str(name)
                .replace("_", " ")
                .title()
            )

            st.markdown(
                f"#### {display_name}"
            )

            if isinstance(
                result,
                (dict, list)
            ):

                st.json(result)

            else:

                st.markdown(str(result))

            st.markdown("---")

    else:

        st.info(
            "Execution results will appear here after "
            "a workflow has been run."
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

    st.markdown(
        "# 📜 AUDIT & TRACEABILITY"
    )

    st.markdown(
        "### ✦ WORKFLOW ACTIVITY HISTORY"
    )

    st.caption(
        "Every workflow start, execution step, decision, "
        "and human review action is recorded for "
        "compliance and traceability."
    )

    st.divider()

    if run_id:

        session = None

        try:

            session = new_session()

            logs = repo.list_audit_logs(
                session,
                run_id=run_id,
            )

        except Exception as error:

            logs = []

            st.error(
                f"Unable to load audit logs: {error}"
            )

        finally:

            if session is not None:
                session.close()

        # ====================================================
        # RUN INFORMATION
        # ====================================================

        st.markdown(
            "### ✦ RUN INFORMATION"
        )

        info_col1, info_col2 = st.columns(2)

        with info_col1:

            st.markdown(
                "**RUN ID**"
            )

            st.code(
                str(run_id)
            )

        with info_col2:

            st.markdown(
                "**CURRENT STATUS**"
            )

            if execution_status == "COMPLETED":

                st.success(
                    "✓ COMPLETED"
                )

            elif execution_status == "REJECTED":

                st.error(
                    "✕ REJECTED"
                )

            elif execution_status == "PENDING_REVIEW":

                st.warning(
                    "⚠ PENDING REVIEW"
                )

            elif execution_status == "FAILED":

                st.error(
                    "✕ FAILED"
                )

            else:

                st.info(
                    str(execution_status)
                )

        st.divider()

        # ====================================================
        # AUDIT ENTRIES
        # ====================================================

        st.markdown(
            "### ✦ AUDIT EVENTS"
        )

        if logs:

            rows = []

            for log in logs:

                rows.append(
                    {
                        "TIMESTAMP": log.timestamp,
                        "STEP": log.step or "—",
                        "STATUS": log.status or "—",
                        "DECISION": log.decision or "—",
                        "USER": log.user or "—",
                        "ERROR": log.error or "—",
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                f"{len(rows)} audit event(s) recorded for this workflow."
            )

        else:

            st.info(
                "No audit events have been recorded for this run yet."
            )

    else:

        st.info(
            "No workflow run is currently available. "
            "Run a workflow to generate audit events."
        )