# AI Tutor - Agent Team System

This project demonstrates a multi-agent system built with Google's Agent Development Kit (ADK), featuring intelligent delegation between specialized agents and advanced memory capabilities.

## Project Structure

```
agents/
├── weather_agent/          # Weather agents (original + stateful)
│   ├── agent.py           # Original single weather agent
│   └── stateful_agent.py  # Memory-enabled weather agent
├── greeting_agent/         # Specialized greeting agent
├── farewell_agent/         # Specialized farewell agent
└── weather_team/           # Root agent that coordinates the team

agent.py                        # Root-level agent for ADK web interface
memory_personalization_demo.py  # Demo of memory features
MEMORY_PERSONALIZATION.md      # Detailed memory documentation
```

## Agent Team Architecture

### Root Agent: `weather_team`
- **Role**: Main coordinator that receives all user queries
- **Capabilities**: 
  - Handles weather requests directly using `get_weather` tool
  - Delegates greetings to `greeting_agent`
  - Delegates farewells to `farewell_agent`
- **Intelligence**: Analyzes user intent and routes to appropriate specialist
- **Model**: Uses `gemini-2.0-flash` for enhanced capabilities

### Stateful Weather Agent: `weather_agent_v4_stateful`
- **Role**: Advanced weather agent with memory and personalization
- **Capabilities**:
  - Remembers user temperature preferences (Celsius/Fahrenheit)
  - Maintains session state across conversations
  - Automatically saves responses using `output_key`
  - Uses `ToolContext` for state management
- **Tools**: `get_weather_stateful` - state-aware weather lookup
- **Model**: Uses `gemini-2.0-flash` for enhanced capabilities

### Sub-Agents

#### `weather_team_coordinator`
- **Purpose**: Main orchestrator that coordinates the weather team
- **Tools**: `get_weather()` - retrieves weather information for cities
- **Delegation**: Routes greetings to `greeting_agent`, farewells to `farewell_agent`
- **Triggers**: Weather requests like "What's the weather in London?"
- **Model**: Uses `gemini-2.0-flash-live-001` for live API capabilities

#### `greeting_agent`
- **Purpose**: Specialized agent for handling user greetings
- **Tool**: `say_hello()` - provides personalized greeting messages
- **Triggers**: "Hi", "Hello", "Hey there", "Good morning", etc.
- **Model**: Uses `gemini-2.0-flash-live-001` for live API capabilities

#### `farewell_agent`
- **Purpose**: Handles goodbyes and conversation endings
- **Tool**: `say_goodbye()` - provides polite farewell messages
- **Triggers**: "Bye", "Goodbye", "See you later", "Thanks, bye", etc.
- **Model**: Uses `gemini-2.0-flash-live-001` for live API capabilities

## Memory and Personalization Features

### Session State Management
- **User Preferences**: Stores temperature unit preferences (Celsius/Fahrenheit)
- **Conversation Context**: Remembers last cities checked
- **Response History**: Automatically saves agent responses
- **State Persistence**: Maintains data across multiple interactions

### ToolContext Integration
- **State Access**: Tools can read/write session state via `ToolContext`
- **Preference Reading**: `tool_context.state.get("user_preference_temperature_unit", "Celsius")`
- **State Writing**: `tool_context.state["last_city_checked"] = city`
- **Safe Defaults**: Always provides fallback values for missing state

### Output Key Mechanism
- **Automatic Saving**: Agent responses saved to state using `output_key`
- **Response History**: Track conversation flow and agent outputs
- **State Updates**: Each response overwrites previous value

## Delegation Flow Example

1. **User**: "Hello there!"
   - **Flow**: Root agent → delegates to `greeting_agent` → calls `say_hello` tool
   - **Response**: "Hello, there!"

2. **User**: "What's the weather in New York?"
   - **Flow**: Root agent → handles directly → calls `get_weather` tool
   - **Response**: Weather information for New York

3. **User**: "Thanks, bye!"
   - **Flow**: Root agent → delegates to `farewell_agent` → calls `say_goodbye` tool
   - **Response**: "Goodbye! Have a great day."

### Memory-Enabled Flow Example

1. **User**: "What's the weather in London?" (Initial: Celsius preference)
   - **Response**: "The weather in London is cloudy with a temperature of 15°C."
   - **State**: Saves London as last checked city

2. **System**: Updates preference to Fahrenheit
   - **State**: `user_preference_temperature_unit` = "Fahrenheit"

3. **User**: "How about New York?"
   - **Response**: "The weather in New York is sunny with a temperature of 77°F."
   - **State**: Updates last checked city to New York

## Running the System

### Option 1: Memory and Personalization Demo
```bash
source venv/bin/activate
python memory_personalization_demo.py
```
This demonstrates:
- Initial state setup with user preferences
- Temperature unit conversion based on state
- State persistence across conversations
- Automatic response saving with `output_key`

### Option 2: ADK Web Interface
```bash
source venv/bin/activate
adk web --port 8000
```
Then visit `http://localhost:8000/dev-ui` and select `agents` to interact with the full weather team system.

**✅ Fixed**: Resolved the `AttributeError: module 'agents' has no attribute 'agent'` issue by:
- Creating proper `agents/__init__.py` that exports the main agent
- Adding root-level `agent.py` for ADK web interface compatibility
- The system now properly exposes the weather team agent through the web interface

### Option 3: Python Script
```bash
source venv/bin/activate
python agent_team_demo.py
```

### Option 4: Original Single Agent
```bash
source venv/bin/activate
python main.py
```

## Available Weather Cities

The system provides mock weather data for:
- **New York**: Sunny, 25°C (77°F)
- **London**: Cloudy, 15°C (59°F)
- **Tokyo**: Light rain, 18°C (64°F)
- **Paris**: Partly cloudy, 20°C (68°F)
- **Berlin**: Overcast, 12°C (54°F)
- **Sydney**: Clear, 22°C (72°F)

## Key Features

### Core Agent System
- **Automatic Delegation**: Root agent intelligently routes queries based on content
- **Specialized Agents**: Each sub-agent is optimized for its specific task
- **Modular Design**: Easy to add new specialized agents
- **Session Management**: Maintains conversation context across interactions
- **Tool Integration**: Each agent has access to relevant tools for its domain
- **Live Interface Compatible**: Uses `gemini-2.0-flash` for stable web interface support

### Memory and Personalization
- **User Preferences**: Remember temperature units and other settings
- **Session State**: Persistent storage across conversation turns
- **ToolContext**: Easy state access within tools
- **Output Key**: Automatic response saving to state
- **State Validation**: Safe defaults and error handling
- **Preference Changes**: Dynamic updates affect subsequent interactions

## Configuration

The system uses the Google Gemini API. Ensure your API key is set in the `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

## Model Information

### All Agents
All agents now use **Gemini 2.0 Flash Live** (`gemini-2.0-flash-live-001`) which provides:
- **Live API Support**: Specifically designed for real-time audio/video interactions
- **WebSocket Compatibility**: Supports bidirectional streaming for Live API
- **Multi-modal Support**: Text, audio, and video processing in real-time
- **Low Latency**: Optimized for interactive voice conversations
- **Function Calling**: Full tool integration support
- **ADK Integration**: Works seamlessly with ADK web interface

**Important**: The Live API requires the specific model `gemini-2.0-flash-live-001`. Regular `gemini-2.0-flash` does NOT support Live API functionality.

## Documentation

- **[MEMORY_PERSONALIZATION.md](MEMORY_PERSONALIZATION.md)**: Comprehensive guide to memory and personalization features
- **[adk_tutorial.ipynb](adk_tutorial.ipynb)**: Complete ADK tutorial notebook with all implementation steps

## Recent Updates

### ✅ Live API Model Fix
All agents now use **Gemini 2.0 Flash** (`gemini-2.0-flash`) which provides:
- **Full ADK Web Interface Support**: Compatible with `adk web` streaming interface and Live API
- **Automatic Live API Support**: ADK automatically uses `gemini-2.0-flash-live-001` for Live API when needed
- **Enhanced Performance**: Latest model with improved capabilities  
- **Multi-modal Support**: Text, images, audio, and video processing
- **Large Context Window**: Up to 1M tokens for complex conversations
- **Cost Effective**: Optimized pricing for high-volume usage

**✅ Fixed Live API Compatibility**: Updated all agents to use `gemini-2.0-flash-live-001` for:
- Proper `bidiGenerateContent` support for live conversations
- Full streaming support via `adk web`
- Elimination of "model not supported" errors
- Stable web interface functionality
- Enhanced real-time user experience

**✅ Memory and Personalization System**: Implemented comprehensive memory features including:
- Session state management with user preferences
- ToolContext integration for state access
- Output key mechanism for automatic response saving
- Temperature unit conversion based on user preferences
- Demonstration scripts and comprehensive documentation

## Architecture Benefits

1. **Modularity**: Each agent has a single, well-defined responsibility
2. **Scalability**: Easy to add new specialized agents (e.g., forecast agent, location agent)
3. **Efficiency**: Can use different models for different complexity levels
4. **Maintainability**: Changes to one agent don't affect others
5. **Testability**: Each agent can be tested independently
6. **Compatibility**: Uses stable models for reliable web interface support
7. **Memory**: Persistent state enables personalized, context-aware interactions
8. **Flexibility**: State system supports any JSON-serializable data 

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API Key (get from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation & Setup

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo-url>
   cd ai-tutor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set your Google API Key:**
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Test the system:**
   ```bash
   # Test memory and personalization features
   python memory_personalization_demo.py
   
   # Test agent team delegation
   python agent_team_demo.py
   
   # Test basic weather functionality
   python main.py
   ```

4. **Launch the web interface:**
   ```bash
   adk web --port 8000
   ```
   Then open http://localhost:8000 in your browser.

## ✅ Current Status

**All systems are fully functional and tested:**

- ✅ **Memory & Personalization**: Session state management working perfectly
- ✅ **Agent Team Delegation**: Multi-agent coordination functioning correctly  
- ✅ **Web Interface**: ADK web interface accessible and responsive
- ✅ **Model Compatibility**: All agents using `gemini-2.0-flash` (Live API compatible)
- ✅ **Live API Support**: Full `bidiGenerateContent` support for real-time conversations
- ✅ **Import Structure**: All module imports resolved and working
- ✅ **Temperature Conversion**: Dynamic unit conversion based on user preferences
- ✅ **State Persistence**: Session state maintained across conversations
- ✅ **Tool Integration**: All tools (weather, greeting, farewell) working correctly

## 🧪 Testing Results

**Memory Demo Output:**
- ✅ State Read: Tool correctly reads temperature preference from state
- ✅ State Update: Preference successfully changes from Celsius to Fahrenheit  
- ✅ State Persistence: Tool uses updated preference for subsequent requests
- ✅ Tool State Write: Tool writes 'last_city_checked_stateful' to state
- ✅ Delegation: Sub-agents handle greetings and farewells correctly
- ✅ output_key: Agent's final responses saved to 'last_weather_report'

**Team Demo Output:**
- ✅ Greeting delegation to specialist agent
- ✅ Weather requests handled by main coordinator
- ✅ Farewell delegation to specialist agent
- ✅ All tools executing correctly

**Web Interface:**
- ✅ Server starts successfully on port 8000
- ✅ HTTP 307 redirect response (normal ADK behavior)
- ✅ Live chat interface accessible
- ✅ No import or model compatibility errors 