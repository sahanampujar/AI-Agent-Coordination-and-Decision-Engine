from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.response_agent import ResponseAgent

research = ResearchAgent()
analysis = AnalysisAgent()
response = ResponseAgent()

query = "Online Bookstore"

research_result = research.research(query)

analysis_result = analysis.analyze(research_result)

final_report = response.generate(analysis_result)

print("\nFinal Report\n")

print(final_report)