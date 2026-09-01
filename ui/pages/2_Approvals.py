import os
import sys
import json

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
from workflows.coordinator import AgentCoordinator


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pending Approvals",
    page_icon="👤",
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

    html,
    body,
    [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 15%,
                rgba(255, 215, 0, 0.10),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(212, 175, 55, 0.08),
                transparent 26%
            ),
            radial-gradient(
                circle at 70% 80%,
                rgba(255, 193, 7, 0.06),
                transparent 28%
            ),
            #050505 !important;

        background-attachment: fixed !important;
        color: #FFFFFF !important;
    }


    /* ========================================================
       MAIN CONTAINER
       ======================================================== */

    .main .block-container {
        max-width: 1400px !important;
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
            0 0 12px rgba(212, 175, 55, 0.18);
    }

    h2,
    h3,
    h4 {
        color: #D4AF37 !important;
    }

    p,
    span,
    label,
    div {
        font-family:
            "Times New Roman",
            Times,
            serif !important;
    }


    /* ========================================================
       DESCRIPTION
       ======================================================== */

    .approval-subtitle {
        text-align: center;
        color: #B8B8B8;
        font-size: 18px;
        line-height: 1.6;
        max-width: 1000px;
        margin: 0 auto 30px auto;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    div[data-testid="stExpander"] {
        background: rgba(14, 14, 14, 0.88) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        border-radius: 16px !important;

        box-shadow:
            0 8px 28px rgba(0, 0, 0, 0.40) !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    input,
    textarea {
        background: #0D0D0D !important;
        color: #FFFFFF !important;

        border: 1px solid rgba(212, 175, 55, 0.45) !important;

        border-radius: 10px !important;

        font-family:
            "Times New Roman",
            Times,
            serif !important;

        font-size: 17px !important;
    }

    input:focus,
    textarea:focus {
        border: 1px solid #FFD700 !important;

        box-shadow:
            0 0 14px rgba(212, 175, 55, 0.18) !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 12px !important;

        font-family:
            "Times New Roman",
            Times,
            serif !important;

        font-size: 17px !important;
        font-weight: 700 !important;

        min-height: 48px !important;

        transition: all 0.2s ease !important;
    }


    /* APPROVE */

    button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #8A6A00,
                #D4AF37,
                #FFD700
            ) !important;

        color: #000000 !important;

        border: 1px solid #FFD700 !important;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        font-family:
            "Times New Roman",
            Times,
            serif !important;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: rgba(212, 175, 55, 0.25) !important;
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

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# COORDINATOR
# ============================================================

if "coordinator" not in st.session_state:
    st.session_state.coordinator = AgentCoordinator()

coordinator = st.session_state.coordinator


# ============================================================
# LOAD PENDING APPROVALS
# ============================================================

session = new_session()

try:

    pending = repo.list_pending_approvals(
        session
    )

    runs_by_id = {
        approval.run_id:
            repo.get_run(
                session,
                approval.run_id
            )
        for approval in pending
    }

finally:

    session.close()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    "# ✦ HUMAN AUTHORIZATION CENTER ✦"
)

st.markdown(
    "Review workflows routed by the Decision Engine for "
    "mandatory human authorization."
)

st.markdown(
    "Approve or reject each request while maintaining "
    "complete workflow traceability."
)

st.divider()


# ============================================================
# EMPTY STATE
# ============================================================

if not pending:

    st.success(
        "✓ No workflows are currently pending review."
    )

    st.markdown(
        "## ✓ ALL CLEAR"
    )

    st.markdown(
        "There are no workflow requests waiting for human authorization."
    )

    st.divider()

# ============================================================
# PENDING APPROVALS
# ============================================================

else:

    st.markdown(
        f"### ✦ {len(pending)} REQUEST(S) AWAITING REVIEW"
    )

    for approval in pending:

        run = runs_by_id.get(
            approval.run_id
        )

        if not run:
            continue

        with st.expander(
            f"⚠ Run {run.id}  •  {run.query}",
            expanded=True,
        ):

            # ------------------------------------------------
            # REQUEST INFORMATION
            # ------------------------------------------------

            info_col1, info_col2 = st.columns(2)

            with info_col1:

                st.markdown(
                    "**WORKFLOW STATUS**"
                )

                st.warning(
                    str(run.status)
                )

            with info_col2:

                st.markdown(
                    "**REQUESTED AT**"
                )

                st.write(
                    approval.requested_at
                )

            st.markdown("---")


            # ------------------------------------------------
            # RESULTS
            # ------------------------------------------------

            results = {}

            if run.results_json:

                try:
                    results = json.loads(
                        run.results_json
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    results = {}


            if results.get("analysis"):

                st.markdown(
                    "### ✦ BUSINESS ANALYSIS"
                )

                st.markdown(
                    results["analysis"]
                )

                st.markdown("---")


            if results.get("decision"):

                st.markdown(
                    "### ✦ DECISION REASONING"
                )

                st.markdown(
                    results["decision"]
                )

                st.markdown("---")


            # ------------------------------------------------
            # REVIEWER INFORMATION
            # ------------------------------------------------

            st.markdown(
                "### ✦ REVIEWER AUTHORIZATION"
            )

            reviewer_name = st.text_input(
                "Reviewer Name",
                value="reviewer",
                key=f"name_{run.id}",
            )

            comment = st.text_area(
                "Review Comment",
                placeholder=(
                    "Enter an optional review comment..."
                ),
                key=f"comment_{run.id}",
            )

            st.markdown("")


            # ------------------------------------------------
            # ACTIONS
            # ------------------------------------------------

            col_a, col_b = st.columns(2)

            with col_a:

                approve = st.button(
                    "✅  APPROVE WORKFLOW",
                    key=f"approve_{run.id}",
                    use_container_width=True,
                    type="primary",
                )

            with col_b:

                reject = st.button(
                    "❌  REJECT WORKFLOW",
                    key=f"reject_{run.id}",
                    use_container_width=True,
                )


            # ------------------------------------------------
            # APPROVE
            # ------------------------------------------------

            if approve:

                try:

                    result = coordinator.resume_workflow(
                        run.id,
                        approved=True,
                        resolved_by=(
                            reviewer_name.strip()
                            or "reviewer"
                        ),
                        comment=comment,
                    )

                    st.success(
                        result.get(
                            "message",
                            "Workflow approved."
                        )
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Approval failed: {error}"
                    )


            # ------------------------------------------------
            # REJECT
            # ------------------------------------------------

            if reject:

                try:

                    result = coordinator.resume_workflow(
                        run.id,
                        approved=False,
                        resolved_by=(
                            reviewer_name.strip()
                            or "reviewer"
                        ),
                        comment=comment,
                    )

                    st.warning(
                        result.get(
                            "message",
                            "Workflow rejected."
                        )
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Rejection failed: {error}"
                    )