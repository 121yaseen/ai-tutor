import os
import warnings
import logging

# Ignore all warnings and set logging level
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# Configure environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Ensure API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file or system environment.")

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state.
    
    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").
        tool_context (ToolContext): Context object providing access to session state.
    
    Returns:
        dict: A dictionary containing the weather information with temperature
              formatted according to user preference stored in session state.
    """
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")  # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
        "paris": {"temp_c": 20, "condition": "partly cloudy"},
        "berlin": {"temp_c": 12, "condition": "overcast"},
        "sydney": {"temp_c": 22, "condition": "clear"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32  # Calculate Fahrenheit
            temp_unit = "°F"
        else:  # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}


def say_hello() -> str:
    """Provides a friendly greeting message."""
    print("--- Tool: say_hello called ---")
    return "Hello there! I'm your friendly weather assistant. How can I help you today?"


def say_goodbye() -> str:
    """Provides a polite farewell message."""
    print("--- Tool: say_goodbye called ---")
    return "Goodbye! Thanks for using the weather service. Have a great day!"


# Create specialized sub-agents
greeting_agent = Agent(
    model="gemini-2.0-flash-live-001",
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
)

farewell_agent = Agent(
    model="gemini-2.0-flash-live-001",
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
)

# Create the stateful weather agent with memory capabilities
stateful_weather_agent = Agent(
    name="stateful_weather_agent",
    model="gemini-2.0-flash-live-001",
    description="A weather agent that remembers user preferences and provides personalized weather information.",
    instruction="You are a personalized weather assistant. "
                "Remember user preferences like their preferred temperature unit (Celsius or Fahrenheit). "
                "When providing weather information, use their preferred unit. "
                "If they haven't specified a preference, ask them or use Celsius as default. "
                "Use the 'get_weather_stateful' tool to fetch weather data.",
    tools=[get_weather_stateful],
    sub_agents=[greeting_agent, farewell_agent],
    output_key="last_weather_report"
) 