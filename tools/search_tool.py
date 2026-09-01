from core.exceptions import ToolExecutionError


class SearchTool:
    """
    Simulates an enterprise search tool.

    In production this would call out to a real search/knowledge-base
    API; here it returns a deterministic simulated result so the rest
    of the workflow has something concrete to reason over.
    """

    def search(self, query):
        query = (query or "").strip()

        if not query:
            raise ToolExecutionError("Search Tool", "No search query provided.")

        return f"""Search Tool Executed Successfully

Search Query:
{query}

Relevant Information:
This is simulated search data related to the user's query.

In a real enterprise AI system, this tool would retrieve
information from:
- Databases
- Enterprise APIs
- Knowledge Bases
- Search Engines
"""
