from core.exceptions import ToolExecutionError


class WeatherTool:
    """
    Simulates a weather information tool.
    """

    _WEATHER_DATA = {
        "bangalore": "Bangalore: 26C, Partly Cloudy",
        "bengaluru": "Bengaluru: 26C, Partly Cloudy",
        "bagalkote": "Bagalkote: 34C, Sunny",
        "mysore": "Mysore: 25C, Light Rain",
        "delhi": "Delhi: 38C, Hot",
        "mumbai": "Mumbai: 29C, Heavy Rain",
        "hyderabad": "Hyderabad: 31C, Cloudy",
        "chennai": "Chennai: 33C, Sunny",
    }

    def get_weather(self, city):
        city_key = (city or "").strip().lower()

        if not city_key:
            raise ToolExecutionError("Weather Tool", "No city provided.")

        if city_key in self._WEATHER_DATA:
            return self._WEATHER_DATA[city_key]

        # Unknown city is a legitimate "no data" case, not a system
        # failure -- return an informative (non-empty) message instead
        # of raising, so the workflow can still complete.
        return f"No weather information available for '{city}'."
