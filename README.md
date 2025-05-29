# Audio Streaming Custom App

This project demonstrates a web application that allows users to interact with an AI agent, specifically an AI Tutor for IELTS speaking assessments. It supports both text and real-time audio communication.

## Project Structure

The project is organized into the following main directories:

- `frontend/`: Contains all UI and frontend-related code (HTML, CSS, JavaScript).
- `api_server/`: Contains the backend API server code (FastAPI application).
- `agents/`: Contains the code for the AI agents (Google ADK based).

## Setup Instructions

Follow these steps to set up and run the project:

### 1. Create and Activate Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

**Create the virtual environment:**

```bash
python -m venv .venv
```

**Activate the virtual environment (run this command each time you open a new terminal for this project):**

- **macOS/Linux (bash/zsh):**

    ```bash
    source .venv/bin/activate
    ```

- **Windows (Command Prompt):**

    ```bash
    .venv\\Scripts\\activate.bat
    ```

- **Windows (PowerShell):**

    ```powershell
    .venv\\Scripts\\Activate.ps1
    ```

### 2. Install Dependencies

Install the required Python packages. Currently, the main dependency is `google-adk`.

```bash
pip install google-adk==1.0.0 uvicorn fastapi python-dotenv
```

*Added `uvicorn`, `fastapi`, and `python-dotenv` as they are used in the project.*

### 3. Configure SSL Certificate (if needed)

If you encounter SSL issues, you might need to set the `SSL_CERT_FILE` environment variable to use certifi's certificate bundle.

```bash
export SSL_CERT_FILE=$(python -m certifi)
```

*Note: For Windows, you might need to set this environment variable differently, e.g., through System Properties.*

### 4. Set Up Google API Key

You need an API key from Google AI Studio to use the generative AI models.

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and get an API key.
2. Create a file named `.env` in the project root directory (`audio-streaming-custom/app/.env`).
3. Copy and paste the following into the `.env` file:

    ```env
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
    ```

4. Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with the actual API key you obtained from Google AI Studio.

### 5. Start the Application

Once the setup is complete, you can start the FastAPI application using Uvicorn. Make sure you are in the project root directory (`audio-streaming-custom/app/`).

```bash
uvicorn api_server.main:app --reload
```

The application will typically be available at `http://127.0.0.1:8000`. The `--reload` flag enables auto-reloading when code changes are detected.

To use Gunicorn for production, you can run:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server.main:app
```

This command runs 4 worker processes, each using Uvicorn as the ASGI server.
