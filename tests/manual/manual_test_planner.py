from agents.planner_agent import PlannerAgent


planner = PlannerAgent()

query = "Develop a business strategy for an online bookstore."

result = planner.plan(query)

print("\nPlanner Agent Output:\n")
print(result)