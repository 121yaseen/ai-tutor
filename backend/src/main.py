from dotenv import load_dotenv
import os
import re
import aiohttp
import orjson
from pathlib import Path
import asyncio
import json
import datetime
from typing import Optional
from livekit.plugins import google
from google.genai.types import Modality

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    noise_cancellation,
)

from src.database.student_db import StudentDB
from src.agents.ielts_examiner_agent import IELTSExaminerAgent
from src.tools.agent_tools import set_current_user_email, set_database
from src.database.user_db import UserDB
from src.database.profile_db import ProfileDB
from src.config.ielts_questions import get_difficulty_level, select_session_questions
load_dotenv()

# Initialize database
db = StudentDB()
set_database(db)

user_db = UserDB()
profile_db = ProfileDB()

async def get_user_data_for_instructions(email: str) -> (str, Optional[float]):
    """Fetch user data, format it for agent instructions, and return latest score."""
    if not email:
        print("[LOG] No user email provided. Cannot fetch user data.")
        return "ERROR: No user email provided. User data unavailable.", None

    print(f"[LOG] Fetching user data for: {email}")
    student = db.get_student(email)
    user_profile = profile_db.get_profile_for_instruction(email)

    history = []
    if student and student.get('history'):
        history = student['history']
        print(f"[LOG] Found {len(history)} previous test(s) for the user.")
    else:
        print(f"[LOG] No previous test history found. This is a new user.")

    user_data = {
        "user_profile": json.loads(user_profile) if user_profile else None,
        "history_summary": [{"test_number": t.get('test_number'), "band_score": t.get('band_score')} for t in history]
    }

    latest_score = history[-1].get('band_score') if history else None
    print(f"[LOG] User's latest score is: {latest_score}")

    # Format the main instruction text
    instruction_text = f"""--- USER DATA ---
{json.dumps(user_data, indent=2)}
"""

    if not history:
        instruction_text += """--- NOTES ---
- This is the user's first session. Please be extra encouraging.
- Your goal is to establish a baseline score.
"""
    else:
        # Add performance summary for returning users
        recent_scores = [test.get('band_score', 0) for test in history if 'band_score' in test]
        if recent_scores:
            avg_score = round(sum(recent_scores) / len(recent_scores), 1)
            best_score = max(recent_scores)
            trend = "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "needs focus"
            instruction_text += f"""--- PERFORMANCE SUMMARY ---
- Average Score: {avg_score}
- Best Score: {best_score}
- Most Recent Score: {latest_score}
- Performance Trend: {trend}
"""

    instruction_text += "-----------------"
    return instruction_text, latest_score

async def entrypoint(ctx: agents.JobContext):
    """The main entrypoint for the agent job."""
    # 1. Connect to the room and get user identity
    await ctx.connect()
    print("[LOG] Successfully connected to the room.")

    current_user_email = None
    try:
        metadata_dict = json.loads(ctx.room.metadata)
        current_user_email = metadata_dict.get("userEmail")
        if current_user_email:
            set_current_user_email(current_user_email)
            print(f"[LOG] User email from room metadata: {current_user_email}")
    except Exception as e:
        print(f"[LOG] No email in room metadata: {e}")

    final_user_email = await _wait_for_user(ctx, current_user_email)
    if not final_user_email:
        print("[ERROR] Could not determine user email. Aborting session.")
        return

    # 2. Fetch user data and select questions
    print(f"[LOG] Preparing user data for: {final_user_email}")
    user_data_instructions, latest_score = await get_user_data_for_instructions(final_user_email)
    
    difficulty = get_difficulty_level(latest_score)
    session_questions = select_session_questions(difficulty)

    # 3. Create the Agent with session-specific configuration
    print(f"[LOG] Creating agent for difficulty '{difficulty}'.")
    agent = IELTSExaminerAgent(session_questions=session_questions)

    # 4. Create and start the AgentSession
    print("[LOG] Creating and starting the agent session.")
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-live-2.5-flash-preview",
            modalities=[Modality.AUDIO],
            voice="Leda",
            vertexai=False),
    )
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # 5. Generate the initial prompt to start the test
    print("[LOG] Sending initial instructions to the agent.")
    full_instructions = (
        f"{user_data_instructions}\n"
        f"Your instructions for this session are based on the data above.\n\n"
        f"## IMMEDIATE ACTIONS:\n"
        f"1.  **GREET THE USER**: Use their name from the user data. If not available, a generic greeting is fine.\n"
        f"2.  **CONDUCT THE TEST**: You must use the specific questions assigned to you for this session.\n"
        f"3.  **SAVE THE RESULT**: After the test, call the `save_test_result_to_json` function with the user's email: `{final_user_email}`.\n"
        f"4.  **DELIVER FEEDBACK**: Provide clear, constructive feedback.\n\n"
        f"Begin the test now by greeting the user."
    )

    try:
        await asyncio.wait_for(
            session.generate_reply(instructions=full_instructions),
            timeout=20,
        )
    except Exception as e:
        print(f"[FALLBACK] LLM failed to generate initial reply: {e}")

async def _wait_for_user(ctx: agents.JobContext, current_user_email: Optional[str]) -> Optional[str]:
    """Wait for a participant with a userEmail in their metadata to join."""
    for participant in ctx.room.remote_participants.values():
        if participant.metadata:
            try:
                metadata_dict = json.loads(participant.metadata)
                user_email = metadata_dict.get("userEmail")
                if user_email:
                    print(f"[LOG] Found user email in participant metadata: {user_email}")
                    set_current_user_email(user_email)
                    return user_email
            except Exception:
                continue # Ignore metadata parsing errors
    
    # Fallback to email from room metadata if no participant has it
    if current_user_email:
        print(f"[LOG] Using user email from room metadata as fallback: {current_user_email}")
        return current_user_email

    print("[LOG] No user participant with email found yet.")
    return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    
