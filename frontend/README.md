<img src="https://www.livekit.io/images/press-kit/livekit-logomark-color.png" alt="LiveKit Logo" width="100" height="100">

# AI IELTS Speaking Examiner - Frontend

This is the frontend for the AI-powered IELTS Speaking Examiner. It provides a voice interface for users to practice the IELTS speaking test. This application is built with [Next.js](https://nextjs.org/) and uses the [LiveKit's React SDK](https://docs.livekit.io/components/react/) to connect to the backend agent and handle real-time voice communication.

![App screenshot](/.github/assets/frontend-screenshot.jpeg)

## Features

-   Real-time voice communication with the AI agent.
-   Transcription of the conversation.
-   Visualization of the agent's voice.
-   A clean and simple user interface.

## Getting Started

### Prerequisites

-   Node.js and pnpm installed.
-   A running instance of the [AI IELTS Speaking Examiner agent](../agent.py).

### Installation

1.  Clone the repository.
2.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
3.  Install the dependencies:
    ```bash
    pnpm install
    ```
4.  Create a `.env.local` file by copying the `.env.example` file and fill in the required environment variables:
    ```bash
    cp .env.example .env.local
    ```
5.  Run the development server:
    ```bash
    pnpm dev
    ```
6.  Open [http://localhost:3000](http://localhost:3000) in your browser.

## How It Works

1.  When you click the "Start the test" button, the application sends a request to the `/api/connection-details` endpoint.
2.  This endpoint generates a LiveKit access token.
3.  The application uses this token to connect to a LiveKit room.
4.  Once connected, the AI agent on the backend is notified and joins the room.
5.  The agent starts the IELTS speaking test, and the conversation begins.
6.  The user's voice is streamed to the agent, and the agent's voice is streamed back to the user in real-time.

## Contributing

This template is open source and we welcome contributions! Please open a PR or issue through GitHub, and don't forget to join us in the [LiveKit Community Slack](https://livekit.io/join-slack)!
