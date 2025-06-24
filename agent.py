from dotenv import load_dotenv
import os
import re
import aiohttp
import orjson
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from pathlib import Path
import asyncio
import json

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    noise_cancellation,
)

load_dotenv()

DATA_PATH = Path("data/student.json")

class StudentPerformance(BaseModel):
    email: str
    name: str
    age: int
    history: List[Dict] = Field(default_factory=list)

class StudentDB:
    def __init__(self, path=DATA_PATH):
        self.path = path
        self._ensure_file()
        self._load()

    def _ensure_file(self):
        if not self.path.exists():
            self.path.write_bytes(orjson.dumps({}))

    def _load(self):
        try:
            content = self.path.read_bytes()
            if not content:
                self.data = {}
            else:
                self.data = orjson.loads(content)
        except orjson.JSONDecodeError:
            self.data = {}

    def save(self):
        self.path.write_bytes(orjson.dumps(self.data))

    def get_student(self, email: str) -> Optional[StudentPerformance]:
        self._load()
        if email in self.data:
            return StudentPerformance(**self.data[email])
        return None

    def upsert_student(self, student: StudentPerformance):
        self.data[student.email] = student.model_dump()
        self.save()
        print(f"[LOG] Saved/Updated student: {student.email} | Data: {student.model_dump()}")

db = StudentDB()

# Global variable to store current user email
current_user_email = None

@function_tool
async def get_student() -> str:
    """Get student performance data from the database."""
    if not current_user_email:
        return "User email not available."
    student = db.get_student(current_user_email)
    if student:
        return student.model_dump_json()
    return "Student not found."

@function_tool
async def create_student(name: str, age: int) -> str:
    """Creates a new student profile."""
    if not current_user_email:
        return "User email not available."
    if db.get_student(current_user_email):
        return "Student already exists."
    student = StudentPerformance(email=current_user_email, name=name, age=age)
    db.upsert_student(student)
    return "Student profile created."

@function_tool
async def add_test_result(result: Dict) -> str:
    """Adds a new test result to a student's history."""
    if not current_user_email:
        return "User email not available."
    student = db.get_student(current_user_email)
    if not student:
        return "Student not found. Cannot add test result."
    student.history.append(result)
    db.upsert_student(student)
    return "Test result added to history."


IELTS_QUESTIONS = {
    "part1": [
        "Where are you from?",
        "Do you work or study?",
        "What do you like to do in your free time?",
    ],
    "part2": [
        "Describe a memorable event in your life. You have one minute to prepare and then speak for up to two minutes.",
    ],
    "part3": [
        "Let's discuss the importance of memorable events in people's lives.",
        "How do people in your country celebrate important events?",
        "Do you think people remember events differently as they get older? Why?",
    ],
}

class IELTSExaminerAgent(Agent):
    def __init__(self):
        super().__init__(
            tools=[get_student, create_student, add_test_result],
            instructions="""
You are a smart, efficient, and supportive IELTS Speaking Examiner Agent. Your role is to simulate the IELTS Speaking Test, retrieve or store student information using tool calls, analyze answers, and provide helpful feedback.

Your behavior must strictly follow these steps:

1. **Greet the user**: Warmly introduce yourself as the Pistah AI IELTS speaking examiner.

2. **Collect student details**:
   - **Tool call:** Use the `get_student()` tool to check the student name.

4. **If student is found**:
   - Summarize their previous IELTS attempts.
   - Include previous band scores and areas of improvement.
   - Inform them they are starting a new test.

5. **If student is NOT found**:
   - **Tool call:** Use `create_student(name, age)` to save the new student into the database.
   - Let them know their profile is created.

6. **Begin the IELTS Speaking Test**:
   - The test has 3 parts:
     - **Part 1**: Introduction and interview
     - **Part 2**: Long turn (one-minute prep, two-minute talk)
     - **Part 3**: Discussion (abstract questions)
   - Present questions from each part one by one.
   - Wait for student response before moving to the next.

7. **After each part**:
   - Internally generate intermediate analysis (fluency, coherence, etc.).
   - Do not share the intermediate feedback with the student yet.

8. **After the final part (Part 3)**:
   - Perform final analysis across all responses.
   - Assign a band score (range 0–9).
   - Write improvement suggestions for:
     - Vocabulary
     - Grammar
     - Pronunciation
     - Coherence & fluency

9. **Save Final Test Result**:
   - **Tool call:** Use `add_test_result(result)` to store a result dictionary containing:
     - All question-answer pairs
     - Band score
     - Analysis

10. **Inform the Student**:
   - Provide:
     - Their Band Score
     - Feedback summary (what went well, what to improve)
     - Clear improvement suggestions

11. **Conclude**:
   - Wish them good luck in the actual IELTS test.
   - Say goodbye politely.

**Rules**:
- Always use tool calls where data fetch or save is required.
- Never assume data from memory; always fetch from the database.
- Be supportive and professional, yet approachable.
- Always thank the student for their effort.
        """)


async def entrypoint(ctx: agents.JobContext):
    global current_user_email
    
    # Extract user email from room metadata
    try:
        # Get metadata from room
        metadata = ctx.room.metadata
        
        if metadata:
            import json
            metadata_dict = json.loads(metadata)
            current_user_email = metadata_dict.get("userEmail")
            print(f"[LOG] User email set to: {current_user_email}")
        else:
            print("[LOG] No room metadata found")
    except Exception as e:
        print(f"[LOG] Error parsing room metadata: {e}")
    
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="alloy"),
    )

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
                            global current_user_email
                            current_user_email = user_email
                            print(f"[LOG] User email set from participant metadata: {current_user_email}")
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
