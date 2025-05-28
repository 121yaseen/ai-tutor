# Environment Setup Guide

## API Key Configuration

After removing the hardcoded API keys from the codebase, you'll need to set up your environment variables properly.

### Option 1: Using a .env file (Recommended)

Create a `.env` file in the root directory of your project with the following content:

```bash
# Google AI Studio API Key (Required)
# Get from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_actual_google_api_key_here

# Optional: Other AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google GenAI Configuration
GOOGLE_GENAI_USE_VERTEXAI=False
```

### Option 2: System Environment Variables

Export the environment variables in your shell:

```bash
export GOOGLE_API_KEY="your_actual_google_api_key_here"
export GOOGLE_GENAI_USE_VERTEXAI="False"
```

### Option 3: Jupyter Notebook Setup

In your Jupyter notebook, add this cell at the beginning:

```python
import os

# Set your API keys
os.environ["GOOGLE_API_KEY"] = "your_actual_google_api_key_here"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
```

## Security Notes

1. **Never commit API keys to version control**
2. **Add `.env` to your `.gitignore` file**
3. **Use environment variables or secure key management systems in production**
4. **Regularly rotate your API keys**

## Getting API Keys

### Google AI Studio API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and use it in your environment configuration

## Running the Application

Once you've set up your environment variables, you can run the application:

```bash
# Make sure you're in the project directory
cd /path/to/ai-tutor

# Run with ADK web server
adk web --port 8000

# Or run individual scripts
python main.py
python agent_team_demo.py
python memory_personalization_demo.py
```

## Troubleshooting

If you see the error "GOOGLE_API_KEY environment variable is required", make sure:

1. Your `.env` file exists and contains the correct key
2. The environment variable is properly exported in your shell
3. You've restarted your terminal/IDE after setting environment variables
4. The API key is valid and has the necessary permissions 