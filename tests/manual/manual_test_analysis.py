from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent

research = ResearchAgent()
analysis = AnalysisAgent()

query = "Online Bookstore"

research_result = research.research(query)

analysis_result = analysis.analyze(research_result)

print("\nResearch Output:\n")
print(research_result)

print("\nAnalysis Output:\n")
print(analysis_result)