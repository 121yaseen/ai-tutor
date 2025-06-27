from dotenv import load_dotenv
import os
import re
import aiohttp
import orjson
from pathlib import Path
import asyncio
import json
import datetime
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
load_dotenv()

# Initialize database
db = StudentDB()
set_database(db)

user_db = UserDB()
profile_db = ProfileDB()

async def get_user_data_for_instructions(email: str) -> str:
    """Fetch all user data upfront and format it for agent instructions"""
    if not email:
        return "ERROR: No user email provided. User data unavailable."
    
    # Get user from database first
    student = db.get_student(email)
    user_profile = profile_db.get_profile_for_instruction(email)
    
    # Handle new users who don't have a student record yet
    if student is None:
        history = []
        print(f"[LOG] New user detected: {email}. No history available yet.")
    else:
        history = student.get('history', [])
    
    user_data = {
        "user_profile": user_profile,
        "history": history
    }
    
    # Initialize variables
    performance_summary = None
    latest_feedback = None
    
    if history:
        recent_scores = [test.get('band_score', 0) for test in history if 'band_score' in test]
        if recent_scores:
            avg_score = sum(recent_scores) / len(recent_scores)
            best_score = max(recent_scores)
            recent_score = recent_scores[-1] if recent_scores else 0
            
            performance_summary = {
                "average_band_score": round(avg_score, 1),
                "best_band_score": best_score,
                "most_recent_score": recent_score,
                "improvement_trend": "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "needs_focus",
                "total_tests": len(history)
            }
            
            # Get latest feedback
            latest_test = history[-1] if history else {}
            if 'feedback' in latest_test:
                latest_feedback = latest_test['feedback']
    
    # Format data for instructions
    instruction_text = f"""
=== USER DATA ===
{user_data}
"""
    
    # Add specific note for new users
    if not history:
        instruction_text += """
*** NEW USER DETECTED ***
This is the user's first IELTS practice session. No previous test history available.
- Start with standard IELTS difficulty level
- Be extra encouraging and supportive
- Explain the test structure clearly
- Focus on comprehensive assessment to establish baseline
"""
    
    if performance_summary:
        instruction_text += f"""
PERFORMANCE SUMMARY:
- Average Band Score: {performance_summary['average_band_score']}
- Best Score: {performance_summary['best_band_score']}
- Most Recent Score: {performance_summary['most_recent_score']}
- Trend: {performance_summary['improvement_trend']}
"""
    
    if latest_feedback:
        instruction_text += f"""
LATEST FEEDBACK:
{latest_feedback}
"""
    
    if history:
        instruction_text += f"""
RECENT TEST HISTORY (Last 3 tests):
"""
        recent_tests = history[-3:]
        for i, test in enumerate(recent_tests):
            test_date = test.get('test_date', 'Unknown date')
            band_score = test.get('band_score', 'No score')
            test_num = len(history) - len(recent_tests) + i + 1
            instruction_text += f"Test {test_num}: Band {band_score} on {test_date}\n"
    
    instruction_text += "================="
    
    return instruction_text

async def entrypoint(ctx: agents.JobContext):
    current_user_email = None
    
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
            model="gemini-live-2.5-flash-preview", 
            modalities=[Modality.AUDIO], 
            voice="Leda",
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
                            return user_email
                    except Exception as e:
                        print(f"[LOG] Error parsing participant metadata: {e}")
            await asyncio.sleep(0.5)
            attempts += 1
        print("[LOG] No user participant with email found")
        return None
    
    # Wait for user to join
    final_user_email = await wait_for_user_participant()
    if not final_user_email and current_user_email:
        final_user_email = current_user_email
    
    # Fetch user data upfront
    print(f"[LOG] Fetching user data for email: {final_user_email}")
    user_data_instructions = await get_user_data_for_instructions(final_user_email)
    print(f"[LOG] User data prepared: {user_data_instructions}")
    
    # Create comprehensive instructions with user data
    full_instructions = f"""
You are an IELTS Speaking Examiner Agent and your name is Pistah. The user data has been pre-loaded for you below.

{user_data_instructions}

Based on this user data, follow these instructions:

## YOUR ROLE:
- You are a professional IELTS Speaking examiner
- Conduct a complete IELTS speaking test based on the user's history and performance level
- Provide detailed assessment and feedback
- Save the test results at the end

## IMMEDIATE ACTIONS:
1. **GREET THE USER**: Use their name from the user data above. If it's "User", just say "Hello! Welcome to your IELTS Speaking Practice session with Pistah AI."

2. **REFERENCE THEIR HISTORY**: 
   - If first-time user: "I can see this is your first test with us. We'll start with a standard IELTS speaking assessment."
   - If returning user: Reference their previous performance, scores, and areas for improvement

3. **CONDUCT IELTS TEST**: Adapt the difficulty and focus based on their history:

### Part 1: Introduction and Interview (4-5 minutes)
- Ask about: hometown, work/study, hobbies, family
- Adapt questions based on previous performance level
- Use simpler questions for beginners, complex follow-ups for advanced students

### Part 2: Long Turn (3-4 minutes)  
- Give topic card relevant to their weak areas (if known from history)
- 1 minute preparation time
- 2 minutes speaking
- Choose difficulty based on their previous performance

### Part 3: Two-way Discussion (4-5 minutes)
- Abstract questions related to Part 2 topic  
- Adjust complexity based on their demonstrated ability
- Focus on their identified improvement areas from previous feedback

## ASSESSMENT AND SCORING:

### Evaluation Criteria (Score 0-9 each):
1. **Fluency and Coherence**: Flow, hesitation, logical organization
2. **Lexical Resource**: Vocabulary range, accuracy, appropriateness  
3. **Grammatical Range and Accuracy**: Sentence structures, error frequency
4. **Pronunciation**: Clarity, stress, intonation patterns

### FINAL STEP - SAVE RESULTS:
After completing the test, you MUST call the save_test_result_to_json function with:
- email: "{final_user_email}" (use this exact email)
- test_result: dict with this structure:
  * "answers": dict with "Part 1", "Part 2", "Part 3" keys
  * "band_score": X.X (overall average)
  * "detailed_scores": dict with "fluency", "vocabulary", "grammar", "pronunciation" keys
  * "feedback": dict with detailed analysis for each area
  * "strengths": list of what they did well
  * "improvements": list of specific areas to work on

Then provide clear feedback to the user:
- Their band score and what it means
- Strengths they demonstrated  
- Specific improvement areas with examples
- Comparison with previous tests (if any)
- Actionable advice for improvement

## CRITICAL RULES:
- NEVER ask for user's name or personal details - it's provided above
- Be encouraging and professional throughout
- Provide specific, actionable feedback with examples
- Always save test results using the tool at the end
- Start immediately with the greeting and test - no tool calls needed for user data

Start the session now by greeting the user and beginning the IELTS test!
"""
    
    try:
        await asyncio.wait_for(
            session.generate_reply(
                instructions=full_instructions
            ),
            timeout=20, # Increased timeout
        )
    except Exception as e:
        print(f"[FALLBACK] LLM failed: {e}. Proceeding with default flow.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    
