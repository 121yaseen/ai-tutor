import os
import warnings
import logging

# Ignore all warnings and set logging level
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

from google.adk.agents import Agent

# Configure environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Ensure API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file or system environment.")

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

# Create the farewell agent
farewell_agent = Agent(
    name="farewell_specialist",
    model="gemini-2.0-flash-live-001",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
) 