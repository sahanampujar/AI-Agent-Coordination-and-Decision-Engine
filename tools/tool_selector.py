import re

from core.exceptions import ToolExecutionError
from tools.calculator import CalculatorTool
from tools.file_tool import FileTool
from tools.search_tool import SearchTool
from tools.weather_tool import WeatherTool


class ToolSelector:
    """
    Selects the appropriate tool based on the user's query.
    """

    def __init__(self):
        self.calculator = CalculatorTool()
        self.file_tool = FileTool()
        self.search_tool = SearchTool()
        self.weather_tool = WeatherTool()

    def execute(self, query):

        if not query or not query.strip():
            raise ToolExecutionError("Tool Selector", "No query provided.")

        query_lower = query.lower().strip()

        # -----------------------------
        # Calculator Tool
        # Only mathematical expressions
        # -----------------------------
        expression = query_lower.replace("calculate", "").strip()

        if re.fullmatch(r"[0-9+\-*/(). ]+", expression):
            return self.calculator.calculate(expression)

        # -----------------------------
        # Weather Tool
        # -----------------------------
        elif "weather" in query_lower:
            city = query_lower.replace("weather", "").replace("in", "").strip()
            return self.weather_tool.get_weather(city)

        # -----------------------------
        # File Tool
        # -----------------------------
        elif query_lower.endswith(".txt"):
            return self.file_tool.read_file(query.strip())

        # -----------------------------
        # Search Tool
        # -----------------------------
        else:
            return self.search_tool.search(query)