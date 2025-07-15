# AI IELTS Speaking Examiner - Backend

This directory contains the backend for the AI-powered IELTS Speaking Examiner. It is a Python application built on the `livekit-agents` framework that simulates an IELTS speaking test, provides real-time feedback, and stores user progress.

## 🚀 Core Features

-   **Realistic Test Simulation**: Conducts a full 3-part IELTS speaking test.
-   **Dynamic Questioning**: Selects questions randomly based on the user's skill level, ensuring variety in every session.
-   **AI-Powered Assessment**: Uses a Google Gemini LLM to analyze user responses and provide a band score.
-   **Personalized Experience**: Adapts to the user's performance history to provide a tailored test experience.
-   **Secure Data Storage**: Securely stores user profiles and test history in a Supabase PostgreSQL database.

## 🏗️ Architecture

The backend is designed with a modular and scalable architecture:

-   **`src/main.py`**: The main entrypoint for the LiveKit agent. It orchestrates the entire workflow, from user identification to agent creation and session management.
-   **`src/agents/`**: Contains the core logic for the `IELTSExaminerAgent`, including its instruction prompt and tool definitions.
-   **`src/database/`**: A dedicated module for all database interactions, abstracting the Supabase connection and queries.
-   **`src/config/`**: Manages all configuration, including the dynamic loading of questions and scoring criteria from external JSON files.
-   **`src/tools/`**: Defines the functions that the AI agent can execute, such as saving test results.
-   **`tests/`**: Includes a comprehensive suite of unit and integration tests to ensure code quality and reliability.

## 🔧 Setup and Running

For detailed setup and execution instructions, please refer to the main `README.md` in the root directory of this project.

### Testing

The backend includes a robust testing suite to ensure reliability.

-   **Unit Tests (Fast, No DB required)**:
    ```bash
    python3 run_tests.py
    ```
-   **Integration Tests (Requires Test Database)**:
    *First, ensure your `.env` file is configured with `TEST_SUPABASE_CONNECTION_STRING` as described in `INTEGRATION_TESTS_SETUP.md`.*
    ```bash
    python3 run_integration_tests.py
    ```

## 🌟 World-Class Milestones

To see the future development roadmap for elevating this backend to a world-class standard, please refer to the [MILESTONES.md](./MILESTONES.md) file.
