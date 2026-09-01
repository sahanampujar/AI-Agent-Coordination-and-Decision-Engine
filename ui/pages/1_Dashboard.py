import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import streamlit as st

from database.models import init_db, new_session
from database import repository as repo


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Workflow Dashboard",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# PREMIUM BLACK + GOLD DASHBOARD THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    html,
    body,
    [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 8% 15%,
                rgba(255, 215, 0, 0.10),
                transparent 24%
            ),
            radial-gradient(
                circle at 92% 20%,
                rgba(212, 175, 55, 0.08),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 85%,
                rgba(255, 193, 7, 0.06),
                transparent 28%
            ),
            #050505 !important;

        color: #FFFFFF !important;
        background-attachment: fixed !important;
    }


    /* ========================================================
       MAIN CONTAINER
       ======================================================== */

    .main .block-container {
        max-width: 1450px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    h1,
    h2,
    h3,
    h4 {
        font-family:
            "Times New Roman",
            Times,
            serif !important;
    }

    h1 {
        color: #D4AF37 !important;
        font-size: 46px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-align: center !important;

        text-shadow:
            0 0 10px rgba(212, 175, 55, 0.18),
            0 0 24px rgba(212, 175, 55, 0.08) !important;
    }

    h2 {
        color: #D4AF37 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
    }

    h3 {
        color: #D4AF37 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    p,
    label,
    span,
    div {
        font-family:
            "Times New Roman",
            Times,
            serif !important;
    }


    /* ========================================================
       SUBTITLE
       ======================================================== */

    .dashboard-subtitle {
        text-align: center;
        color: #B8B8B8;
        font-size: 18px;
        letter-spacing: 1px;
        margin-top: -12px;
        margin-bottom: 35px;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(25, 25, 25, 0.95),
                rgba(10, 10, 10, 0.95)
            ) !important;

        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        border-radius: 15px !important;

        padding: 20px !important;

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.40),
            inset 0 1px 0 rgba(255, 215, 0, 0.04) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #BDBDBD !important;
        font-family:
            "Times New Roman",
            Times,
            serif !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-family:
            "Times New Roman",
            Times,
            serif !important;
        font-size: 34px !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       SECTION DIVIDER
       ======================================================== */

    hr {
        border-color: rgba(212, 175, 55, 0.25) !important;
        margin: 30px 0 !important;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(212, 175, 55, 0.30) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }


    /* ========================================================
       ALERT BOXES
       ======================================================== */

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        font-family:
            "Times New Roman",
            Times,
            serif !important;
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

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# LOAD DASHBOARD DATA
# ============================================================

session = new_session()

try:
    metrics = repo.dashboard_metrics(session)
    recent_runs = repo.list_runs(
        session,
        limit=25,
    )
finally:
    session.close()


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    "# ✦ ENTERPRISE WORKFLOW DASHBOARD ✦"
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        LIVE MONITORING • WORKFLOW ANALYTICS • DECISION INTELLIGENCE
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# TOP-LINE METRICS
# ============================================================

st.markdown(
    "## ✦ WORKFLOW OVERVIEW"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "TOTAL WORKFLOWS",
        metrics["total_workflows"],
    )

with col2:
    st.metric(
        "SUCCESSFUL RUNS",
        metrics["successful_runs"],
    )

with col3:
    st.metric(
        "FAILED RUNS",
        metrics["failed_runs"],
    )

with col4:
    st.metric(
        "PENDING REVIEW",
        metrics["pending_review_runs"],
    )


col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "AVG EXECUTION TIME",
        f"{metrics['average_execution_time_seconds']} s",
    )

with col6:
    st.metric(
        "APPROVAL RATE",
        f"{metrics['approval_rate_percent']}%",
    )

with col7:
    st.metric(
        "REJECTION RATE",
        f"{metrics['rejection_rate_percent']}%",
    )

with col8:
    st.metric(
        "REVIEW RATE",
        f"{metrics['review_rate_percent']}%",
    )


st.divider()


# ============================================================
# STEP FAILURE BREAKDOWN
# ============================================================

st.markdown(
    "## ⚠ STEP FAILURE ANALYTICS"
)

step_failures = metrics.get(
    "step_failure_counts",
    {}
)

if step_failures:

    st.bar_chart(
        step_failures
    )

else:

    st.success(
        "✓ No step failures recorded — system is operating cleanly."
    )


st.divider()


# ============================================================
# RECENT WORKFLOW HISTORY
# ============================================================

st.markdown(
    "## ◷ RECENT WORKFLOW RUNS"
)

if recent_runs:

    rows = []

    for run in recent_runs:

        rows.append(
            {
                "RUN ID": run.id,
                "BUSINESS QUERY": run.query,
                "STATUS": run.status,
                "STARTED": run.started_at,
                "DURATION (s)": run.duration_seconds,
                "USER": run.user,
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No workflow runs yet. "
        "Return to the main page and run a workflow."
    )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

st.divider()

st.markdown(
    "## ✦ SYSTEM SUMMARY"
)

summary_col1, summary_col2, summary_col3 = (
    st.columns(3)
)

with summary_col1:

    st.markdown(
        f"### {metrics['total_workflows']}"
    )

    st.caption(
        "Total workflow executions"
    )

with summary_col2:

    st.markdown(
        f"### {metrics['successful_runs']}"
    )

    st.caption(
        "Successfully completed workflows"
    )

with summary_col3:

    st.markdown(
        f"### {metrics['total_steps_logged']}"
    )

    st.caption(
        "Workflow steps logged"
    )