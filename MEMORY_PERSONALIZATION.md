# Memory and Personalization with ADK

This document explains the Memory and Personalization features implemented in the AI Tutor project, based on Step 4 of the ADK tutorial. These features enable agents to remember user preferences and maintain context across conversations using session state.

## Overview

The Memory and Personalization system allows agents to:

1. **Remember user preferences** across multiple conversational turns
2. **Maintain session state** that persists throughout a user session
3. **Automatically save agent responses** using the `output_key` mechanism
4. **Read and write state** within tools using `ToolContext`
5. **Provide personalized experiences** based on stored preferences

## Key Components

### 1. Session State

Session state is a Python dictionary (`session.state`) that:
- Is tied to a specific user session (identified by `APP_NAME`, `USER_ID`, `SESSION_ID`)
- Persists information across multiple conversational turns within that session
- Can be read from and written to by agents and tools

### 2. ToolContext

`ToolContext` is an object that provides tools with access to session context:
- Automatically injected by ADK when declared as the last parameter of a tool function
- Provides direct access to session state via `tool_context.state`
- Allows tools to read preferences and save results during execution

### 3. Output Key

The `output_key` parameter on an Agent:
- Automatically saves the agent's final textual response to the session state
- Uses the specified key name to store the response
- Overwrites previous values on each agent response

## Implementation

### Stateful Weather Tool

The `get_weather_stateful` function demonstrates how to use `ToolContext`:

```python
def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    
    # Read preference from state
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    
    # ... weather logic ...
    
    # Format temperature based on preference
    if preferred_unit == "Fahrenheit":
        temp_value = (temp_c * 9/5) + 32
        temp_unit = "°F"
    else:
        temp_value = temp_c
        temp_unit = "°C"
    
    # Write back to state
    tool_context.state["last_city_checked_stateful"] = city
    
    return result
```

### Stateful Agent Configuration

The agent is configured with memory features:

```python
stateful_weather_agent = Agent(
    name="stateful_weather_coordinator",
    model="gemini-1.5-flash",
    tools=[get_weather_stateful],  # Uses state-aware tool
    sub_agents=[greeting_agent, farewell_agent],
    output_key="last_weather_report"  # Auto-save responses
)
```

### Session Initialization

Sessions are created with initial state:

```python
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state
)
```

## Usage Examples

### Running the Demo

Execute the memory and personalization demo:

```bash
python memory_personalization_demo.py
```

This will demonstrate:
1. Initial state setup with Celsius preference
2. Weather request using Celsius
3. State update to Fahrenheit preference
4. Weather request using Fahrenheit
5. Delegation to sub-agents
6. Final state inspection

### Key Features Demonstrated

1. **State Read**: Tool reads temperature preference from session state
2. **State Update**: Preference changes from Celsius to Fahrenheit
3. **State Persistence**: Updated preference affects subsequent requests
4. **Tool State Write**: Tool saves last checked city to state
5. **Delegation**: Sub-agents handle greetings and farewells
6. **Output Key**: Agent responses are automatically saved to state

## State Management

### Reading from State

```python
# Safe reading with default value
preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
```

### Writing to State

```python
# Direct assignment
tool_context.state["last_city_checked"] = city
```

### State Inspection

```python
# Get session and inspect state
session = session_service.get_session(app_name, user_id, session_id)
print(f"Current state: {dict(session.state)}")
```

## Benefits

### For Users
- **Personalized Experience**: Preferences are remembered across conversations
- **Context Continuity**: Agents remember previous interactions
- **Consistent Behavior**: Settings persist throughout the session

### For Developers
- **Simple API**: Easy to read/write state using `ToolContext`
- **Automatic Persistence**: `output_key` handles response saving
- **Flexible Storage**: State can hold any JSON-serializable data
- **Session Isolation**: Each user session maintains separate state

## Best Practices

1. **Use Default Values**: Always provide defaults when reading from state
   ```python
   value = tool_context.state.get("key", "default_value")
   ```

2. **Clear Documentation**: Document what state keys your tools use
   ```python
   def my_tool(param: str, tool_context: ToolContext) -> str:
       """
       Tool that uses state.
       
       State keys used:
       - user_preference_x: User's preference for X
       - last_action_y: Last Y action performed
       """
   ```

3. **State Validation**: Validate state values before using them
   ```python
   unit = tool_context.state.get("temperature_unit", "Celsius")
   if unit not in ["Celsius", "Fahrenheit"]:
       unit = "Celsius"  # Fallback to safe default
   ```

4. **Minimal State**: Only store necessary information to avoid bloat
   ```python
   # Good: Store essential preference
   tool_context.state["temperature_unit"] = "Fahrenheit"
   
   # Avoid: Storing large or temporary data
   # tool_context.state["full_weather_history"] = large_data_structure
   ```

## Integration with Existing System

The memory and personalization features integrate seamlessly with:

- **Multi-Agent Delegation**: Sub-agents can also access and modify state
- **Tool System**: Any tool can read/write state using `ToolContext`
- **Session Management**: Works with any ADK session service
- **Safety Callbacks**: Callbacks can inspect and modify state

## Files Structure

```
agents/
├── weather_agent/
│   ├── __init__.py
│   ├── agent.py              # Original agent
│   └── stateful_agent.py     # Memory-enabled agent
└── ...

memory_personalization_demo.py  # Demonstration script
MEMORY_PERSONALIZATION.md      # This documentation
```

## Next Steps

The memory and personalization system provides the foundation for:

1. **User Profiles**: Store long-term user preferences
2. **Conversation History**: Maintain context across sessions
3. **Learning Systems**: Adapt behavior based on user interactions
4. **Recommendation Engines**: Personalize suggestions based on history
5. **Safety Guardrails**: Use state to track and prevent problematic patterns

This implementation demonstrates the core concepts needed to build sophisticated, context-aware agent systems that provide personalized user experiences. 