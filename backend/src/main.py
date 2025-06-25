from dotenv import load_dotenv
import os
import re
import aiohttp
import orjson
from pathlib import Path
import asyncio
import json
from livekit.plugins import google
from google.genai.types import Modality

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    noise_cancellation,
)

from .database.student_db import StudentDB
from .agents.ielts_examiner_agent import IELTSExaminerAgent
from .tools.agent_tools import set_current_user_email, set_database

load_dotenv()

DATA_PATH = Path("data/student.json")

# Initialize database
db = StudentDB(DATA_PATH)
set_database(db)

async def entrypoint(ctx: agents.JobContext):
    # Extract user email from room metadata
    try:
        # Get metadata from room
        metadata = ctx.room.metadata
        
        if metadata:
            import json
            metadata_dict = json.loads(metadata)
            current_user_email = metadata_dict.get("userEmail")
            set_current_user_email(current_user_email)
            print(f"[LOG] User email set to: {current_user_email}")
        else:
            print("[LOG] No room metadata found")
    except Exception as e:
        print(f"[LOG] Error parsing room metadata: {e}")
    
    print(f"[LOG] Creating session")
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp", 
            modalities=[Modality.AUDIO], 
            voice="Puck",
            vertexai=False),
    )

    print(f"[LOG] Creating agent")
    agent = IELTSExaminerAgent()

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    await ctx.connect()
    
    # Add participant entry point and wait for user to join
    print(f"[LOG] Local participant: {ctx.room.local_participant}")
    
    # Wait for user participant to join and get their metadata
    async def wait_for_user_participant():
        attempts = 0
        while attempts < 10:  # Try for 5 seconds
            for participant in ctx.room.remote_participants.values():
                print(f"[LOG] Found participant: {participant.identity}, metadata: {participant.metadata}")
                if participant.metadata:
                    try:
                        import json
                        metadata_dict = json.loads(participant.metadata)
                        user_email = metadata_dict.get("userEmail")
                        print(f"[LOG] Parsed userEmail: {user_email}")
                        if user_email:
                            set_current_user_email(user_email)
                            print(f"[LOG] User email set from participant metadata: {user_email}")
                            return True
                    except Exception as e:
                        print(f"[LOG] Error parsing participant metadata: {e}")
            await asyncio.sleep(0.5)
            attempts += 1
        print("[LOG] No user participant with email found")
        return False
    
    # Wait for user to join
    await wait_for_user_participant()
    
    try:
        await asyncio.wait_for(
            session.generate_reply(
                instructions="Greet the student and start the IELTS speaking test."
            ),
            timeout=20, # Increased timeout
        )
    except Exception as e:
        print(f"[FALLBACK] LLM failed: {e}. Proceeding with default flow.")

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
