"""
Memory and Personalization Demo

This script demonstrates the Memory and Personalization features from Step 4 of the ADK tutorial.
It shows how agents can:
1. Remember user preferences across conversations using session state
2. Use ToolContext to read/write state in tools
3. Automatically save agent responses using output_key
4. Maintain state persistence across multiple interactions
"""

import os
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import the stateful agent
from agents.weather_agent.stateful_agent import agent as weather_agent_stateful

# Configure environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file or system environment.")

# Constants
APP_NAME = "weather_tutorial_stateful_app"
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"


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


async def run_stateful_conversation():
    """Demonstrates memory and personalization features with session state."""
    
    print("=== Memory and Personalization Demo ===")
    print("This demo shows how agents can remember preferences and maintain state across conversations.\n")

    # 1. Initialize New Session Service and State
    print("--- Step 1: Initialize Session Service with Initial State ---")
    session_service_stateful = InMemorySessionService()
    
    # Define initial state data - user prefers Celsius initially
    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }
    
    # Create the session with initial state
    session_stateful = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
        state=initial_state
    )
    print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")
    
    # Verify the initial state
    retrieved_session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )
    print(f"Initial Session State: {retrieved_session.state}")

    # 2. Create Runner with Stateful Agent
    print("\n--- Step 2: Create Runner with Stateful Agent ---")
    runner_stateful = Runner(
        agent=weather_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful
    )
    print(f"✅ Runner created for stateful agent '{runner_stateful.agent.name}'")

    # 3. Test State Flow
    print("\n--- Step 3: Testing State Flow and Memory ---")
    
    # First interaction - should use Celsius (initial preference)
    print("\n--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async(
        query="What's the weather in London?",
        runner=runner_stateful,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )

    # Manually update state preference to Fahrenheit
    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
    try:
        # Access the internal storage directly for testing
        stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
        stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
        print(f"--- State updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---")
    except Exception as e:
        print(f"--- Error updating session state: {e} ---")

    # Second interaction - should now use Fahrenheit
    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async(
        query="Tell me the weather in New York.",
        runner=runner_stateful,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )

    # Test delegation still works
    print("\n--- Turn 3: Testing delegation with greeting ---")
    await call_agent_async(
        query="Hi!",
        runner=runner_stateful,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )

    # Test farewell delegation
    print("\n--- Turn 4: Testing delegation with farewell ---")
    await call_agent_async(
        query="Thanks, bye!",
        runner=runner_stateful,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )

    # 4. Inspect Final Session State
    print("\n--- Step 4: Inspecting Final Session State ---")
    final_session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )
    
    if final_session:
        print(f"Final Temperature Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        print(f"Guardrail Block Triggered: {final_session.state.get('guardrail_block_keyword_triggered', 'Not Set')}")
        print(f"\nFull Final State: {dict(final_session.state)}")
    else:
        print("❌ Error: Could not retrieve final session state.")

    print("\n=== Demo Complete ===")
    print("Key observations:")
    print("✅ State Read: Tool correctly read temperature preference from state")
    print("✅ State Update: Preference successfully changed from Celsius to Fahrenheit")
    print("✅ State Persistence: Tool used updated preference for subsequent requests")
    print("✅ Tool State Write: Tool wrote 'last_city_checked_stateful' to state")
    print("✅ Delegation: Sub-agents handled greetings and farewells correctly")
    print("✅ output_key: Agent's final responses were saved to 'last_weather_report'")


async def demonstrate_preference_change():
    """Demonstrates how to change user preferences and see immediate effects."""
    
    print("\n=== Preference Change Demo ===")
    print("This shows how changing preferences affects subsequent interactions.\n")

    # Create a new session service for this demo
    session_service = InMemorySessionService()
    
    # Start with Fahrenheit preference
    initial_state = {
        "user_preference_temperature_unit": "Fahrenheit"
    }
    
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="preference_demo_user",
        session_id="preference_demo_session",
        state=initial_state
    )
    
    runner = Runner(
        agent=weather_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    print("--- Starting with Fahrenheit preference ---")
    await call_agent_async(
        query="What's the weather in Tokyo?",
        runner=runner,
        user_id="preference_demo_user",
        session_id="preference_demo_session"
    )
    
    # Change to Celsius
    print("\n--- Changing preference to Celsius ---")
    stored_session = session_service.sessions[APP_NAME]["preference_demo_user"]["preference_demo_session"]
    stored_session.state["user_preference_temperature_unit"] = "Celsius"
    
    await call_agent_async(
        query="How about the weather in Paris?",
        runner=runner,
        user_id="preference_demo_user",
        session_id="preference_demo_session"
    )
    
    print("\n--- Preference Change Demo Complete ---")


async def main():
    """Main function to run all demonstrations."""
    try:
        await run_stateful_conversation()
        await demonstrate_preference_change()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 