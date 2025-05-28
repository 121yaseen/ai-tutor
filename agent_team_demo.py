import os
import asyncio
import warnings
import logging

# Ignore all warnings and set logging level
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Configure environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Ensure API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file or system environment.")

print("Libraries imported and environment configured.")

# Define tools for sub-agents
def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# Create sub-agents
print("Creating sub-agents...")

greeting_agent = Agent(
    model="gemini-2.0-flash-live-001",
    name="greeting_specialist",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                "Use the 'say_hello' tool to generate the greeting. "
                "If the user provides their name, make sure to pass it to the tool. "
                "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
)
print(f"✅ Agent '{greeting_agent.name}' created.")

farewell_agent = Agent(
    model="gemini-2.0-flash-live-001",
    name="farewell_specialist",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
)
print(f"✅ Agent '{farewell_agent.name}' created.")

# Create root agent with sub-agents
print("Creating root agent with delegation capabilities...")

weather_team_agent = Agent(
    name="weather_team_coordinator",
    model="gemini-2.0-flash-live-001",
    description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
    instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                "You have specialized sub-agents: "
                "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                "For weather requests, use the tool directly. For greetings/farewells, delegate to the appropriate sub-agent.",
    tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent],
)
print(f"✅ Root Agent '{weather_team_agent.name}' created with sub-agents: {[sa.name for sa in weather_team_agent.sub_agents]}")

# Agent interaction function
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    # Execute the agent logic and yield Events
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # Check for final response
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")

# Main conversation function
async def run_team_conversation():
    print("\n--- Testing Agent Team Delegation ---")
    
    # Setup session service and runner
    session_service = InMemorySessionService()
    APP_NAME = "weather_tutorial_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"
    
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    runner = Runner(
        agent=weather_team_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # Test different types of queries to demonstrate delegation
    print("\n=== Testing Delegation Flow ===")
    
    # 1. Greeting (should delegate to greeting_agent)
    await call_agent_async("Hello there!", runner, USER_ID, SESSION_ID)
    
    # 2. Weather request (should be handled by root agent)
    await call_agent_async("What is the weather like in New York?", runner, USER_ID, SESSION_ID)
    
    # 3. Another weather request
    await call_agent_async("How about London?", runner, USER_ID, SESSION_ID)
    
    # 4. Farewell (should delegate to farewell_agent)
    await call_agent_async("Thanks, bye!", runner, USER_ID, SESSION_ID)

async def main():
    await run_team_conversation()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}") 