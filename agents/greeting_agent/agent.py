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

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

# Create the greeting agent
greeting_agent = Agent(
    name="greeting_specialist",
    model="gemini-2.0-flash-live-001",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                "Use the 'say_hello' tool to generate the greeting. "
                "If the user provides their name, make sure to pass it to the tool. "
                "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
) 