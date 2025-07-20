"""
Refactored main entry point using clean architecture and dependency injection.

This module provides the main entry point for the IELTS examiner agent with
proper separation of concerns, comprehensive error handling, and scalable architecture.
"""

import asyncio
import json
import sys
from typing import Optional
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation
from google.genai.types import Modality

# Import our clean architecture components
from src.core.config import settings
from src.core.logging import (
    get_logger, 
    set_request_context, 
    generate_request_id,
    performance_logger
)
from src.core.exceptions import (
    IELTSExaminerException,
    configuration_error,
    agent_error,
    livekit_error
)
from src.core.container import get_student_service
from src.services.question_service import get_question_service
from src.agents.ielts_examiner_agent_new import IELTSExaminerAgentNew
from src.tools.agent_tools_new import (
    initialize_session_context,
    set_current_user_email,
    set_current_session_id
)

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class SessionManager:
    """Manages IELTS examination sessions with proper lifecycle management."""
    
    def __init__(self):
        """Initialize session manager."""
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
        self.student_service = get_student_service()
        self.question_service = get_question_service()
    
    async def create_session(self, ctx: agents.JobContext) -> AgentSession:
        """
        Create and configure an agent session.
        
        Args:
            ctx: LiveKit job context
            
        Returns:
            Configured AgentSession
            
        Raises:
            AgentException: If session creation fails
        """
        try:
            # Create Google Gemini Live model
            llm = google.beta.realtime.RealtimeModel(
                model=settings.google_ai.model_name,
                modalities=[Modality.AUDIO],
                voice=settings.google_ai.voice,
                vertexai=False
            )
            
            # Create agent session with noise cancellation
            session = AgentSession(
                llm=llm,
            )
            
            self.logger.info(
                "Agent session created successfully",
                extra={"extra_fields": {
                    "model": settings.google_ai.model_name,
                    "voice": settings.google_ai.voice
                }}
            )
            
            return session
            
        except Exception as e:
            self.logger.error(
                "Failed to create agent session",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise agent_error(
                "Failed to create agent session",
                original_exception=e
            )
    
    async def extract_user_context(self, ctx: agents.JobContext) -> tuple[str, Optional[str]]:
        """
        Extract user context from room metadata and participants.
        
        Args:
            ctx: LiveKit job context
            
        Returns:
            Tuple of (user_email, session_id)
            
        Raises:
            AgentException: If user context cannot be determined
        """
        session_id = generate_request_id()
        user_email = None
        
        try:
            # Try to get user email from room metadata
            if ctx.room.metadata:
                try:
                    metadata_dict = json.loads(ctx.room.metadata)
                    user_email = metadata_dict.get("userEmail")
                    if user_email:
                        self.logger.debug(f"Found user email in room metadata: {user_email}")
                except json.JSONDecodeError:
                    self.logger.warning("Invalid JSON in room metadata")
            
            # Try to get user email from participant metadata if not found in room
            if not user_email:
                user_email = await self._wait_for_participant_email(ctx)
            
            if not user_email:
                raise agent_error(
                    "Could not determine user email from room or participant metadata",
                    session_id=session_id
                )
            
            self.logger.info(
                "User context extracted successfully",
                extra={"extra_fields": {
                    "user_email": user_email,
                    "session_id": session_id
                }}
            )
            
            return user_email, session_id
            
        except Exception as e:
            if isinstance(e, agent_error):
                raise
            
            self.logger.error(
                "Error extracting user context",
                extra={"extra_fields": {
                    "error": str(e),
                    "session_id": session_id
                }},
                exc_info=True
            )
            
            raise agent_error(
                f"Failed to extract user context: {e}",
                session_id=session_id,
                original_exception=e
            )
    
    async def _wait_for_participant_email(self, ctx: agents.JobContext, timeout: int = 10) -> Optional[str]:
        """
        Wait for a participant with userEmail in metadata to join.
        
        Args:
            ctx: LiveKit job context
            timeout: Maximum wait time in seconds
            
        Returns:
            User email or None if not found within timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check existing participants
            for participant in ctx.room.remote_participants.values():
                if participant.metadata:
                    try:
                        metadata_dict = json.loads(participant.metadata)
                        user_email = metadata_dict.get("userEmail")
                        if user_email:
                            self.logger.debug(f"Found user email in participant metadata: {user_email}")
                            return user_email
                    except json.JSONDecodeError:
                        continue
            
            # Wait a bit before checking again
            await asyncio.sleep(0.5)
        
        self.logger.warning(f"No participant with email found within {timeout} seconds")
        return None
    
    async def prepare_user_data(self, user_email: str) -> tuple[str, Optional[float]]:
        """
        Prepare comprehensive user data for AI instructions.
        
        Args:
            user_email: User's email address
            
        Returns:
            Tuple of (formatted_instructions, latest_score)
        """
        try:
            # Get user data through service layer
            instructions, latest_score = self.student_service.get_user_data_for_instructions(user_email)
            
            self.logger.debug(
                f"User data prepared for: {user_email}",
                extra={"extra_fields": {
                    "has_instructions": bool(instructions),
                    "latest_score": latest_score,
                    "instruction_length": len(instructions) if instructions else 0
                }}
            )
            
            return instructions, latest_score
            
        except Exception as e:
            self.logger.error(
                f"Error preparing user data: {user_email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            # Return basic fallback data
            fallback_instructions = f"""--- USER DATA ---
{{"user_profile": null, "history_summary": []}}
--- NOTES ---
- Error occurred while loading user data
- Proceeding with basic assessment
-----------------"""
            
            return fallback_instructions, None
    
    async def select_questions(self, user_email: str, latest_score: Optional[float]) -> dict:
        """
        Select appropriate questions based on user's skill level.
        
        Args:
            user_email: User's email address
            latest_score: User's latest band score
            
        Returns:
            Dictionary with selected questions
        """
        try:
            # Determine difficulty level
            difficulty = self.question_service.get_difficulty_level(latest_score)
            
            # Select questions for the session
            question_set = self.question_service.select_session_questions(difficulty)
            
            self.logger.info(
                f"Questions selected for {user_email}",
                extra={"extra_fields": {
                    "difficulty": difficulty.value,
                    "latest_score": latest_score
                }}
            )
            
            return question_set.to_dict()
            
        except Exception as e:
            self.logger.error(
                f"Error selecting questions for {user_email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            # Return fallback intermediate questions
            fallback_questions = {
                "part1": "Tell me about your hometown.",
                "part2": "Describe a person who has influenced you. You should say: who this person is, how you know them, what they are like, and explain how they have influenced you.",
                "part3": "How do you think technology has changed the way people communicate?"
            }
            
            return fallback_questions
    
    async def create_agent(self, session_questions: dict) -> Agent:
        """
        Create the IELTS examiner agent with session-specific configuration.
        
        Args:
            session_questions: Selected questions for the session
            
        Returns:
            Configured IELTSExaminerAgent
        """
        try:
            agent = IELTSExaminerAgentNew(session_questions=session_questions)
            
            self.logger.info(
                "IELTS examiner agent created successfully",
                extra={"extra_fields": {
                    "has_questions": bool(session_questions),
                    "parts_count": len(session_questions)
                }}
            )
            
            return agent
            
        except Exception as e:
            self.logger.error(
                "Failed to create IELTS examiner agent",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise agent_error(
                "Failed to create IELTS examiner agent",
                original_exception=e
            )
    
    async def generate_initial_instructions(
        self,
        user_email: str,
        user_data_instructions: str
    ) -> str:
        """
        Generate comprehensive initial instructions for the agent.
        
        Args:
            user_email: User's email address
            user_data_instructions: Formatted user data instructions
            
        Returns:
            Complete instruction string for the agent
        """
        instructions = f"""{user_data_instructions}

Your instructions for this session are based on the data above.

## IMMEDIATE ACTIONS:
1.  **GREET THE USER**: Use their name from the user data. If not available, a generic greeting is fine.
2.  **CONDUCT THE TEST**: You must use the specific questions assigned to you for this session.
3.  **SAVE THE RESULT**: After the test, call the `save_test_result_to_json` function with the user's email: `{user_email}`.
4.  **DELIVER FEEDBACK**: Provide clear, constructive feedback.

## SESSION GUIDELINES:
- Follow the 3-part IELTS speaking test structure strictly
- Maintain professional but friendly demeanor
- Provide encouragement and support throughout
- Focus on accurate assessment using official IELTS criteria
- Ensure all parts are completed within appropriate time limits

Begin the test now by greeting the user and starting with Part 1."""
        
        self.logger.debug(
            f"Initial instructions generated for: {user_email}",
            extra={"extra_fields": {
                "instruction_length": len(instructions),
                "includes_user_data": "USER DATA" in instructions
            }}
        )
        
        return instructions


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the IELTS examiner agent.
    
    This function orchestrates the entire session lifecycle with proper
    error handling, logging, and performance monitoring.
    
    Args:
        ctx: LiveKit job context
    """
    session_manager = SessionManager()
    request_id = generate_request_id()
    
    # Set initial logging context
    set_request_context(request_id=request_id)
    
    logger.info(
        "IELTS examiner session starting",
        extra={"extra_fields": {
            "request_id": request_id,
            "room_name": ctx.room.name if ctx.room else "unknown",
            "environment": settings.app.environment
        }}
    )
    
    performance_start = asyncio.get_event_loop().time()
    
    try:
        # Step 1: Connect to the room
        logger.info("Connecting to LiveKit room")
        await ctx.connect()
        logger.info("Successfully connected to LiveKit room")
        
        # Step 2: Extract user context
        logger.info("Extracting user context")
        user_email, session_id = await session_manager.extract_user_context(ctx)
        
        # Initialize session context
        initialize_session_context(user_email=user_email, session_id=session_id)
        set_request_context(request_id=request_id, user_email=user_email, session_id=session_id)
        
        # Step 3: Prepare user data and select questions
        logger.info(f"Preparing session for user: {user_email}")
        
        # Run these in parallel for better performance
        user_data_task = session_manager.prepare_user_data(user_email)
        
        user_data_instructions, latest_score = await user_data_task
        session_questions = await session_manager.select_questions(user_email, latest_score)
        
        # Step 4: Create agent and session
        logger.info("Creating agent and session")
        agent = await session_manager.create_agent(session_questions)
        session = await session_manager.create_session(ctx)
        
        # Step 5: Start the agent session
        logger.info("Starting agent session")
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        
        # Step 6: Generate and send initial instructions
        logger.info("Sending initial instructions to agent")
        initial_instructions = await session_manager.generate_initial_instructions(
            user_email, user_data_instructions
        )
        
        try:
            await asyncio.wait_for(
                session.generate_reply(instructions=initial_instructions),
                timeout=settings.app.session_timeout
            )
            
            logger.info("Initial instructions sent successfully")
            
        except asyncio.TimeoutError:
            logger.warning("Initial instruction generation timed out, using fallback")
            
            # Send a simple fallback greeting
            await session.generate_reply(
                instructions="Greet the user and begin the IELTS speaking test with Part 1."
            )
        
        # Log session completion
        session_duration = asyncio.get_event_loop().time() - performance_start
        
        performance_logger.log_execution_time(
            operation="ielts_session_complete",
            duration_ms=session_duration * 1000,
            success=True,
            user_email=user_email,
            session_id=session_id
        )
        
        logger.info(
            "IELTS examiner session completed successfully",
            extra={"extra_fields": {
                "request_id": request_id,
                "user_email": user_email,
                "session_id": session_id,
                "duration_seconds": round(session_duration, 2)
            }}
        )
        
    except IELTSExaminerException as e:
        # Handle application-specific errors
        logger.error(
            f"IELTS examiner error: {e}",
            extra={"extra_fields": {
                "request_id": request_id,
                "error_code": e.error_code.value,
                "error_details": e.details
            }},
            exc_info=True
        )
        
        # Log performance with error
        session_duration = asyncio.get_event_loop().time() - performance_start
        performance_logger.log_execution_time(
            operation="ielts_session_error",
            duration_ms=session_duration * 1000,
            success=False,
            error_code=e.error_code.value
        )
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(
            f"Unexpected error in IELTS examiner session: {e}",
            extra={"extra_fields": {
                "request_id": request_id,
                "error_type": type(e).__name__
            }},
            exc_info=True
        )
        
        # Log performance with error
        session_duration = asyncio.get_event_loop().time() - performance_start
        performance_logger.log_execution_time(
            operation="ielts_session_error",
            duration_ms=session_duration * 1000,
            success=False,
            error="unexpected_error"
        )


def validate_environment():
    """
    Validate that all required environment variables and configurations are present.
    
    Raises:
        ConfigurationException: If required configuration is missing
    """
    try:
        # Test settings access (will raise if configuration is invalid)
        _ = settings.app.app_name
        _ = settings.database.connection_string
        _ = settings.livekit.api_key
        _ = settings.google_ai.model_name
        
        logger.info(
            "Environment validation passed",
            extra={"extra_fields": {
                "environment": settings.app.environment,
                "app_name": settings.app.app_name,
                "log_level": settings.app.log_level
            }}
        )
        
    except Exception as e:
        logger.error(
            "Environment validation failed",
            extra={"extra_fields": {"error": str(e)}},
            exc_info=True
        )
        
        raise configuration_error(
            f"Environment validation failed: {e}",
            original_exception=e
        )


def main():
    """Main entry point for the application."""
    try:
        # Validate environment before starting
        validate_environment()
        
        # Log startup information
        logger.info(
            "IELTS Examiner Agent starting",
            extra={"extra_fields": {
                "version": settings.app.version,
                "environment": settings.app.environment,
                "debug": settings.app.debug,
                "python_version": sys.version
            }}
        )
        
        # Run the LiveKit agent
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        
    except Exception as e:
        logger.error(
            "Failed to start IELTS Examiner Agent",
            extra={"extra_fields": {"error": str(e)}},
            exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    main() 