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

    def get_student(self, name: str) -> Optional[StudentPerformance]:
        self._load()
        if name in self.data:
            return StudentPerformance(**self.data[name])
        return None

    def upsert_student(self, student: StudentPerformance):
        self.data[student.name] = student.model_dump()
        self.save()
        print(f"[LOG] Saved/Updated student: {student.name} | Data: {student.model_dump()}")

db = StudentDB()

@function_tool
async def get_student(name: str) -> str:
    """Get student performance data from the database."""
    student = db.get_student(name)
    if student:
        return student.model_dump_json()
    return "Student not found."

@function_tool
async def create_student(name: str, age: int) -> str:
    """Creates a new student profile."""
    if db.get_student(name):
        return "Student already exists."
    student = StudentPerformance(name=name, age=age)
    db.upsert_student(student)
    return "Student profile created."

@function_tool
async def add_test_result(name: str, result: Dict) -> str:
    """Adds a new test result to a student's history."""
    student = db.get_student(name)
    if not student:
        return "Student not found. Cannot add test result."
    student.history.append(result)
    db.upsert_student(student)
    return "Test result added to history."


IELTS_QUESTIONS = {
    "part1": [
        "Can you tell me your full name?",
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

1. **Greet the user**: Warmly introduce yourself as the AI IELTS speaking examiner.

2. **Collect student details**:
   - Ask for their full name first.
   - Then ask for their age.

3. **After age is received**:
   - **Tool call:** Use the `get_student(name)` tool to check if this student already exists.

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
   - **Tool call:** Use `add_test_result(name, result)` to store a result dictionary containing:
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
