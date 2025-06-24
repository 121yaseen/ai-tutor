# AI IELTS Speaking Examiner

This project is a voice-based AI assistant that acts as an IELTS Speaking Examiner. It allows users to practice the IELTS speaking test and receive feedback on their performance.

![App screenshot](./frontend/.github/assets/frontend-screenshot.jpeg)

## 🏗️ Project Structure

The project has been refactored into a clean, modular structure:

```
ai-voice-assistant-livekit/
├── backend/                          # Python backend application
│   ├── src/                         # Source code
│   │   ├── agents/                  # AI agent implementations
│   │   │   └── ielts_examiner_agent.py
│   │   ├── models/                  # Data models
│   │   │   └── student_models.py
│   │   ├── database/                # Database management
│   │   │   └── student_db.py
│   │   ├── tools/                   # Agent function tools
│   │   │   └── agent_tools.py
│   │   ├── config/                  # Configuration files
│   │   │   └── ielts_questions.py
│   │   └── main.py                  # Main application entry point
│   ├── data/                        # Data storage
│   │   └── student.json
│   └── requirements.txt             # Python dependencies
├── frontend/                        # Next.js frontend application
│   ├── app/                        # Next.js app router
│   ├── components/                 # React components
│   ├── hooks/                      # Custom React hooks
│   └── lib/                        # Utility libraries
├── docs/                           # Documentation
│   ├── DESIGN_PLAN.md             # Architecture design plan
│   └── PROJECT_README.md          # Original project documentation
├── scripts/                        # Utility scripts
│   ├── setup.sh                   # Project setup script
│   ├── run_backend.sh             # Backend runner script
│   └── run_frontend.sh            # Frontend runner script
├── config/                         # Global configuration
├── shared/                         # Shared types and utilities
└── venv/                          # Python virtual environment
```

## ✨ Features

- **Realistic IELTS Speaking Test Simulation:** The agent simulates all three parts of the IELTS speaking test.
- **AI-Powered Analysis:** The agent uses a Large Language Model (LLM) to analyze the user's performance and provide a band score.
- **Detailed Feedback:** The user receives detailed feedback on their fluency, coherence, vocabulary, grammar, and pronunciation.
- **Real-time Voice Communication:** The user can speak to the agent in real-time using their microphone.
- **Conversation Transcription:** The conversation between the user and the agent is transcribed and displayed on the screen.
- **User Authentication:** Secure login/signup with Supabase authentication.
- **Test History:** All test results are saved and can be reviewed by the user.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js and pnpm
- LiveKit account and API credentials
- Supabase account (for authentication)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ai-voice-assistant-livekit.git
   cd ai-voice-assistant-livekit
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure environment variables:**
   - Create a `.env` file in the root directory
   - Add your LiveKit and OpenAI API credentials
   - Create a `.env.local` file in the `frontend/` directory with Supabase credentials

### Running the Application

#### Option 1: Using Scripts (Recommended)

1. **Start the backend:**
   ```bash
   ./scripts/run_backend.sh
   ```

2. **Start the frontend (in a new terminal):**
   ```bash
   ./scripts/run_frontend.sh
   ```

#### Option 2: Manual Execution

1. **Backend:**
   ```bash
   source venv/bin/activate
   cd backend
   python -m src.main
   ```

2. **Frontend:**
   ```bash
   cd frontend
   pnpm dev
   ```

3. **Open [http://localhost:3000](http://localhost:3000) in your browser.**

## 🔧 Development

### Backend Architecture

The backend follows a modular architecture:

- **`agents/`**: Contains the main IELTS examiner agent logic
- **`models/`**: Pydantic models for data validation
- **`database/`**: Database abstraction layer (currently JSON, migrating to Supabase)
- **`tools/`**: Function tools used by the AI agent
- **`config/`**: Configuration files and constants

### Frontend Architecture

The frontend is built with Next.js 14 and includes:

- **Authentication**: Supabase-based auth with protected routes
- **Real-time Communication**: LiveKit WebRTC integration
- **Voice Interface**: Real-time transcription and audio visualization
- **Responsive Design**: Tailwind CSS with custom LiveKit styling

### Tech Stack

#### Backend
- **Framework**: LiveKit Agents v1.1.1
- **AI**: OpenAI Realtime API
- **Data**: JSON storage (migrating to Supabase PostgreSQL)
- **Audio**: LiveKit WebRTC + noise cancellation

#### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Authentication**: Supabase Auth
- **Styling**: Tailwind CSS
- **Real-time**: LiveKit Client SDK
- **Animations**: Framer Motion

## 📚 Documentation

- [Design Plan](./docs/DESIGN_PLAN.md) - Detailed architecture and migration plan
- [Original Documentation](./docs/PROJECT_README.md) - Original project information

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## 📄 License

This project is licensed under the MIT License - see the frontend/LICENSE file for details. 