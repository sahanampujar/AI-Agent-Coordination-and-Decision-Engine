"""
Simple command-line entrypoint for the Enterprise Workflow Platform.

This complements (does not replace) the Streamlit UI and REST API --
useful for quick local testing/scripting without a browser.

BUG FIX: this previously called `coordinator.execute(query)`, a
method that does not exist on AgentCoordinator (it has
`run_workflow_builder()` + `run_workflow()`), so running
`python app.py` would always crash with an AttributeError. Fixed to
build a workflow first and then execute it, exactly like the
Streamlit UI does.
"""

import json

from workflows.coordinator import AgentCoordinator


def main():
    coordinator = AgentCoordinator()

    print("=" * 50)
    print("AI Agent Coordination & Decision Engine")
    print("=" * 50)

    query = input("\nEnter your business problem:\n> ")

    workflow = coordinator.run_workflow_builder(query)
    execution = coordinator.run_workflow(query, workflow)

    print("\n" + "=" * 50)
    print(f"STATUS: {execution.get('status')}")
    print("=" * 50)
    print(execution.get("message", ""))

    results = execution.get("results", {})
    final_report = results.get("response")

    if final_report:
        print("\nFINAL REPORT")
        print("-" * 50)
        print(final_report)
    else:
        print("\nNo final response was generated. Full results:")
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
