# AI IELTS Speaking Examiner

This project is a voice-based AI assistant that acts as an IELTS Speaking Examiner. It allows users to practice the IELTS speaking test and receive feedback on their performance.

![App screenshot](./frontend/.github/assets/frontend-screenshot.jpeg)

## Project Structure

The project is divided into two main parts:

-   **Backend (`agent.py`):** An AI agent built with the `livekit-agents` framework that simulates the IELTS speaking test, analyzes the user's performance, and provides feedback.
-   **Frontend (`frontend` directory):** A Next.js application that provides a user interface for interacting with the AI agent using real-time voice communication.

## Features

-   **Realistic IELTS Speaking Test Simulation:** The agent simulates all three parts of the IELTS speaking test.
-   **AI-Powered Analysis:** The agent uses a Large Language Model (LLM) to analyze the user's performance and provide a band score.
-   **Detailed Feedback:** The user receives detailed feedback on their fluency, coherence, vocabulary, grammar, and pronunciation.
-   **Real-time Voice Communication:** The user can speak to the agent in real-time using their microphone.
-   **Conversation Transcription:** The conversation between the user and the agent is transcribed and displayed on the screen.

## Getting Started

### Prerequisites

-   Python 3.9+
-   Node.js and pnpm
-   LiveKit account and API credentials

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```
2.  **Backend Setup:**
    -   Navigate to the root directory.
    -   Create a virtual environment:
        ```bash
        python3 -m venv venv
        ```
    -   Activate the virtual environment:
        ```bash
        source venv/bin/activate
        ```
    -   Install the Python dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    -   Create a `.env` file and add your LiveKit and OpenAI API credentials.
3.  **Frontend Setup:**
    -   Navigate to the `frontend` directory:
        ```bash
        cd frontend
        ```
    -   Install the dependencies:
        ```bash
        pnpm install
        ```
    -   Create a `.env.local` file by copying the `.env.example` file and fill in the required environment variables.
4.  **Running the Application:**
    -   Start the backend agent from the root directory:
        ```bash
        python agent.py
        ```
    -   Start the frontend application from the `frontend` directory:
        ```bash
        pnpm dev
        ```
    -   Open [http://localhost:3000](http://localhost:3000) in your browser.

## How It Works

The application uses the `livekit-agents` framework to connect the frontend to the backend agent. When the user starts the test, the frontend connects to a LiveKit room. The backend agent also joins the room and starts the test. The user's voice is streamed to the agent, which processes the audio and responds in real-time.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue. 