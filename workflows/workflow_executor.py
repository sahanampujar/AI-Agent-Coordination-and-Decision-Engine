import time
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from workflows.execution_monitor import ExecutionMonitor
from workflows.decision_engine import DecisionEngine
from core.exceptions import AgentExecutionError, ToolExecutionError, StepTimeoutError

import config

from database.models import new_session
from database import repository as repo


def _word_in(haystack: str, needle: str) -> bool:
    """
    Word-boundary substring check, used instead of plain `in` for
    matching a keyword against a step's free-text `component` field.

    Plain substring matching is unsafe here: "search" is a literal
    substring of "research" ("re" + "search"), so `"search" in
    "research agent"` is True. That collision used to silently
    misroute Research steps into the Search Tool branch -- see the
    detailed comment above the tool-routing block in _dispatch_step()
    for the full failure mode this caused.
    """
    return re.search(rf"\b{re.escape(needle)}\b", haystack or "") is not None



# Step types that represent transient, retry-worthy work (LLM/tool
# calls). Validation-type failures (bad workflow shape, unsupported
# step) are NOT retried since retrying them can't help.
_RETRYABLE_STEP_TYPES = {
    "planner", "calculator", "search", "weather", "file",
    "research", "analysis", "decision", "response",
}


class WorkflowExecutor:

    def __init__(self, coordinator):
        self.coordinator = coordinator

    # =============================================================
    # PUBLIC ENTRYPOINT
    # =============================================================

    def execute(self, query, workflow, user: str = "anonymous"):
        """
        Execute a workflow end-to-end.

        Behavior preserved from the original implementation:
          - returns a dict with status/message/workflow/results/metrics
          - stops on the first failed step and reports FAILED truthfully
          - never reports COMPLETED unless every step actually completed

        New behavior:
          - persists the run, each step, decisions, and audit log
            entries to the database (Module E)
          - retries transient agent/tool failures (Module B)
          - applies a per-step timeout (Module B)
          - pauses execution and returns PENDING_REVIEW (instead of
            forcing a decision) when the Decision Engine routes to
            REVIEW, creating an Approval record a human can act on
            (Module I). Call `resume(run_id, approved)` to continue.
        """

        session = new_session()
        results = {}

        monitor = ExecutionMonitor()
        monitor.start()

        # =====================================================
        # VALIDATE WORKFLOW
        # =====================================================

        if not isinstance(workflow, dict):
            monitor.finish()
            return self._fail_fast(
                session, workflow, results, monitor,
                "Invalid workflow format.",
            )

        steps = workflow.get("steps", [])

        if not isinstance(steps, list) or not steps:
            monitor.finish()
            return self._fail_fast(
                session, workflow, results, monitor,
                "Workflow contains no execution steps.",
            )

        # =====================================================
        # PERSIST WORKFLOW + RUN
        # =====================================================

        try:
            db_workflow = repo.create_workflow(
                session,
                name=workflow.get("workflow_name", "Enterprise Workflow"),
                objective=workflow.get("objective", query),
                definition=workflow,
            )
            db_run = repo.create_run(session, db_workflow.id, query, user=user)

            repo.write_audit_log(
                session, run_id=db_run.id, workflow_id=db_workflow.id, user=user,
                step="WORKFLOW_START", status="RUNNING",
            )
        except Exception as db_error:
            # If persistence itself is unavailable (e.g. DB down),
            # still report a truthful FAILED status instead of
            # crashing the whole request/UI.
            monitor.finish()
            return self._fail_fast(
                session, workflow, results, monitor,
                f"Could not initialize workflow persistence: {db_error}",
            )

        try:
            for step in steps:

                step_name = str(step.get("name", f"Step {step.get('step', '')}"))
                step_type = str(step.get("type", "")).strip().lower()
                component = str(step.get("component", "")).strip().lower()

                step_start = time.perf_counter()
                step_status = "COMPLETED"
                step_error = None
                pending_review = False

                try:
                    self._run_step_with_resilience(
                        step_type, component, query, results, step_name,
                    )

                except (AgentExecutionError, ToolExecutionError, StepTimeoutError) as error:
                    step_status = "FAILED"
                    step_error = str(error)
                    results[step_name] = f"Step failed: {error}"

                except Exception as error:
                    step_status = "FAILED"
                    step_error = str(error)
                    results[step_name] = f"Step failed: {error}"

                duration = time.perf_counter() - step_start

                monitor.log_step(
                    step_name=step_name, step_type=step_type,
                    status=step_status, duration=duration, error=step_error,
                )

                repo.log_step(
                    session, db_run.id, step_name, step_type, step_status,
                    duration_seconds=duration, error=step_error,
                )
                repo.write_audit_log(
                    session, run_id=db_run.id, workflow_id=db_workflow.id, user=user,
                    step=step_name, status=step_status, error=step_error,
                )

                # -----------------------------------------------
                # DECISION step: record decision + check for REVIEW
                # -----------------------------------------------
                if step_status == "COMPLETED" and (
                    step_type == "decision" or _word_in(component, "decision")
                ):
                    decision_label = results.get("decision_branch", {}).get("decision")
                    repo.record_decision(
                        session, db_run.id, decision_label or "RECOMMEND",
                        results.get("decision", ""),
                    )
                    repo.write_audit_log(
                        session, run_id=db_run.id, workflow_id=db_workflow.id,
                        user=user, step=step_name, decision=decision_label,
                        status="RECORDED",
                    )

                    if decision_label == "REVIEW":
                        pending_review = True

                if step_status == "FAILED":
                    monitor.finish()
                    execution = {
                        "status": "FAILED",
                        "message": f"Workflow stopped at step: {step_name}",
                        "workflow": workflow,
                        "results": results,
                        "metrics": monitor.get_metrics(),
                        "run_id": db_run.id,
                    }
                    repo.update_run(
                        session, db_run.id, status="FAILED", message=execution["message"],
                        results=results, finished=True,
                    )
                    repo.write_audit_log(
                        session, run_id=db_run.id, workflow_id=db_workflow.id,
                        user=user, status="FAILED", error=step_error,
                    )
                    session.close()
                    return execution

                if pending_review:
                    # Pause here: the Response step (and anything after
                    # Decision) is NOT executed until a human approves
                    # or rejects. This is the human-in-the-loop gate
                    # (Module I). Context is persisted so `resume()`
                    # can continue exactly where we left off.
                    monitor.finish()
                    approval = repo.create_approval(session, db_run.id)

                    execution = {
                        "status": "PENDING_REVIEW",
                        "message": (
                            "Workflow paused: the Decision Engine routed this "
                            "request to REVIEW and it now requires human "
                            "approval before the Response step can run."
                        ),
                        "workflow": workflow,
                        "results": results,
                        "metrics": monitor.get_metrics(),
                        "run_id": db_run.id,
                        "approval_id": approval.id,
                    }
                    repo.update_run(
                        session, db_run.id, status="PENDING_REVIEW",
                        message=execution["message"], results=results,
                        context={"query": query, "workflow": workflow, "results": results},
                    )
                    repo.write_audit_log(
                        session, run_id=db_run.id, workflow_id=db_workflow.id,
                        user=user, status="PENDING_REVIEW", decision="REVIEW",
                    )
                    session.close()
                    return execution

            # =====================================================
            # FINISH SUCCESS
            # =====================================================

            monitor.finish()

            execution = {
                "status": "COMPLETED",
                "message": "Workflow executed successfully.",
                "workflow": workflow,
                "results": results,
                "metrics": monitor.get_metrics(),
                "run_id": db_run.id,
            }

            try:
                self.coordinator.shared_memory.save("workflow_execution", execution)
            except Exception:
                pass

            repo.update_run(
                session, db_run.id, status="COMPLETED", message=execution["message"],
                results=results, finished=True,
            )
            repo.write_audit_log(
                session, run_id=db_run.id, workflow_id=db_workflow.id, user=user,
                status="COMPLETED",
            )

            session.close()
            return execution

        except Exception as error:
            monitor.finish()
            execution = {
                "status": "FAILED",
                "message": str(error),
                "workflow": workflow,
                "results": results,
                "metrics": monitor.get_metrics(),
                "run_id": db_run.id,
            }
            repo.update_run(
                session, db_run.id, status="FAILED", message=str(error),
                results=results, finished=True,
            )
            repo.write_audit_log(
                session, run_id=db_run.id, workflow_id=db_workflow.id, user=user,
                status="FAILED", error=str(error),
            )
            session.close()
            return execution

    # =============================================================
    # HUMAN-IN-THE-LOOP RESUME
    # =============================================================

    def resume(self, run_id: str, approved: bool, resolved_by: str = "reviewer", comment: str = ""):
        """
        Resume a workflow that is PENDING_REVIEW after a human decision.

        - approved=True  -> runs the Response step and completes the run.
        - approved=False -> marks the run REJECTED; Response is not run.
        """

        session = new_session()

        db_run = repo.get_run(session, run_id)
        if not db_run:
            session.close()
            raise ValueError(f"No workflow run found with id={run_id}")

        if db_run.status != "PENDING_REVIEW":
            session.close()
            raise ValueError(
                f"Run {run_id} is not awaiting review (status={db_run.status})."
            )

        approval = repo.get_pending_approval_for_run(session, run_id)
        if approval:
            repo.resolve_approval(session, approval.id, approved, resolved_by, comment)

        import json
        context = json.loads(db_run.context_json) if db_run.context_json else {}
        query = context.get("query", db_run.query)
        workflow = context.get("workflow", {})
        results = context.get("results", {})

        repo.write_audit_log(
            session, run_id=run_id, workflow_id=db_run.workflow_id,
            user=resolved_by, status="APPROVED" if approved else "REJECTED",
            decision="APPROVE" if approved else "REJECT",
        )

        if not approved:
            repo.update_run(
                session, run_id, status="REJECTED",
                message=f"Human reviewer rejected this workflow. {comment}".strip(),
                results=results, finished=True,
            )
            session.close()
            return {
                "status": "REJECTED",
                "message": "Human reviewer rejected this workflow.",
                "workflow": workflow,
                "results": results,
                "run_id": run_id,
            }

        # Approved: run the remaining Response step.
        monitor = ExecutionMonitor()
        monitor.start()
        step_start = time.perf_counter()

        try:
            analysis = results.get("analysis", "")
            decision = results.get("decision", "")
            branch = results.get("decision_branch", {})

            response_input = f"""
Generate the final enterprise business response.

Business Query:
{query}

Business Analysis:
{analysis}

Decision:
{decision}

Decision Branch:
{branch}

A human reviewer has approved this request after review.

Return a concise, professional final response.
"""
            results["response"] = self.coordinator.run_response(response_input)
            step_status = "COMPLETED"
            step_error = None

        except Exception as error:
            step_status = "FAILED"
            step_error = str(error)
            results["Response"] = f"Step failed: {error}"

        duration = time.perf_counter() - step_start
        monitor.log_step(
            step_name="Response", step_type="response",
            status=step_status, duration=duration, error=step_error,
        )
        repo.log_step(
            session, run_id, "Response", "response", step_status,
            duration_seconds=duration, error=step_error,
        )
        monitor.finish()

        final_status = "COMPLETED" if step_status == "COMPLETED" else "FAILED"
        message = (
            "Workflow resumed after human approval and completed successfully."
            if final_status == "COMPLETED"
            else f"Workflow resumed after approval but the Response step failed: {step_error}"
        )

        repo.update_run(
            session, run_id, status=final_status, message=message,
            results=results, finished=True,
        )
        repo.write_audit_log(
            session, run_id=run_id, workflow_id=db_run.workflow_id,
            user=resolved_by, status=final_status, error=step_error,
        )

        execution = {
            "status": final_status,
            "message": message,
            "workflow": workflow,
            "results": results,
            "metrics": monitor.get_metrics(),
            "run_id": run_id,
        }
        session.close()
        return execution

    # =============================================================
    # INTERNAL HELPERS
    # =============================================================

    def _fail_fast(self, session, workflow, results, monitor, message):
        if session:
            session.close()
        return {
            "status": "FAILED",
            "message": message,
            "workflow": workflow,
            "results": results,
            "metrics": monitor.get_metrics(),
        }

    def _run_step_with_resilience(self, step_type, component, query, results, step_name):
        """
        Runs a single step's underlying work with:
          - a timeout (STEP_TIMEOUT_SECONDS), enforced via a worker thread
          - retries for transient failures on retryable step types
        Raises on failure; on success, mutates `results` exactly like the
        original implementation did.
        """

        attempts = config.STEP_MAX_RETRIES + 1 if step_type in _RETRYABLE_STEP_TYPES else 1
        last_error = None

        for attempt in range(attempts):
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        self._dispatch_step, step_type, component, query, results, step_name,
                    )
                    try:
                        future.result(timeout=config.STEP_TIMEOUT_SECONDS)
                        return
                    except FutureTimeoutError:
                        raise StepTimeoutError(
                            f"Step '{step_name}' exceeded the "
                            f"{config.STEP_TIMEOUT_SECONDS}s timeout."
                        )

            except StepTimeoutError:
                raise  # timeouts are not retried

            except (AgentExecutionError, ToolExecutionError) as error:
                last_error = error
                if attempt < attempts - 1:
                    time.sleep(0.5)
                    continue
                raise

        if last_error:
            raise last_error

    def _dispatch_step(self, step_type, component, query, results, step_name):
        """
        Original step-dispatch logic, preserved from the initial
        implementation, factored out so it can be run inside a
        timeout-bounded worker thread.
        """

        # =================================================
        # PLANNER
        # =================================================
        if step_type == "planner" or _word_in(component, "planner"):
            results["planner"] = self.coordinator.run_planner(query)

        # =================================================
        # CALCULATOR / SEARCH / WEATHER / FILE (all tool steps)
        #
        # NOTE: these use exact step_type equality first, and a
        # *word-boundary* regex (not plain substring "in") against
        # component. This is a real, critical bug fix: the string
        # "research" contains "search" as a raw substring
        # ("re" + "search"), so a Research step whose component is
        # "Research Agent" used to be matched by
        # `"search" in component` and silently misrouted into the
        # Search Tool branch -- running the wrong tool, writing its
        # output to results["tool"] instead of results["research"],
        # and never raising an error. The step showed COMPLETED, the
        # overall workflow showed COMPLETED, and results["research"]
        # was simply never set -- exactly reproducing the reported
        # bug ("Workflow Completed Successfully!" while the Research
        # tab shows "Research output was not generated."). Using
        # `_word_in()` (a \b-bounded regex) instead of `in` fixes
        # this at the source; step_type equality is still checked
        # first as the primary, unambiguous signal.
        # =================================================
        elif step_type == "calculator" or _word_in(component, "calculator"):
            results["tool"] = self.coordinator.run_tool(query)

        elif step_type == "search" or _word_in(component, "search"):
            results["tool"] = self.coordinator.run_tool(query)

        elif step_type == "weather" or _word_in(component, "weather"):
            results["tool"] = self.coordinator.run_tool(query)

        elif step_type == "file" or _word_in(component, "file"):
            results["tool"] = self.coordinator.run_tool(query)

        # =================================================
        # RESEARCH
        # =================================================
        elif step_type == "research" or _word_in(component, "research"):
            plan = results.get("planner", query)
            tool_output = results.get("tool", "")

            research_input = (
                f"Business Query:\n{query}\n\n"
                f"Planner Output:\n{plan}\n\n"
                f"Tool Output:\n{tool_output}"
            )

            research_result = self.coordinator.run_research(research_input)

            # run_research() now raises AgentExecutionError on empty/
            # failed output (see agents/research_agent.py + core/
            # exceptions.py), so no truthiness re-check is needed here
            # -- if we got this far, research_result is guaranteed
            # non-empty, real content.
            results["research"] = str(research_result)

        # =================================================
        # ANALYSIS
        # =================================================
        elif step_type == "analysis" or _word_in(component, "analysis"):
            research = results.get("research", query)
            results["analysis"] = self.coordinator.run_analysis(research)

        # =================================================
        # DECISION
        # =================================================
        elif step_type == "decision" or _word_in(component, "decision"):
            analysis = results.get("analysis", query)
            decision = self.coordinator.run_decision(analysis, query)
            results["decision"] = decision

            decision_label = DecisionEngine.parse_decision(decision)

            branch_map = {
                "APPROVE": {
                    "decision": "APPROVE",
                    "action": "Approval Action",
                    "status": "Approved",
                    "next_step": "Proceed with the requested operation.",
                },
                "REJECT": {
                    "decision": "REJECT",
                    "action": "Rejection Action",
                    "status": "Rejected",
                    "next_step": "Stop the requested operation.",
                },
                "REVIEW": {
                    "decision": "REVIEW",
                    "action": "Human Review",
                    "status": "Requires Review",
                    "next_step": "Forward the request for human approval.",
                },
                "RECOMMEND": {
                    "decision": "RECOMMEND",
                    "action": "Recommendation Action",
                    "status": "Recommendation Generated",
                    "next_step": "Proceed using the recommended action.",
                },
            }

            branch = branch_map[decision_label]
            results["decision_branch"] = branch

            try:
                self.coordinator.shared_memory.save("decision_branch", branch)
            except Exception:
                pass

        # =================================================
        # RESPONSE
        # =================================================
        elif step_type == "response" or _word_in(component, "response") or _word_in(component, "notification"):
            analysis = results.get("analysis", "")
            decision = results.get("decision", "")
            branch = results.get("decision_branch", {})

            response_input = f"""
Generate the final enterprise business response.

Business Query:
{query}

Business Analysis:
{analysis}

Decision:
{decision}

Decision Branch:
{branch}

Return a concise, professional final response.
"""
            results["response"] = self.coordinator.run_response(response_input)

        # =================================================
        # UNKNOWN COMPONENT
        # =================================================
        else:
            raise ValueError(
                f"Unsupported workflow step: type='{step_type}', component='{component}'"
            )
