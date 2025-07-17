"""
Enhanced IELTS Examiner Agent using clean architecture.

This module implements the IELTS examiner agent with proper dependency injection,
comprehensive error handling, and clean separation of concerns.
"""

from typing import Dict, Any
from livekit.agents import Agent

from ..core.logging import get_logger
from ..services.question_service import get_question_service
from ..tools.agent_tools_new import (
    save_test_result_to_json,
    create_new_student_record,
    get_student_performance_analytics,
    get_user_learning_recommendations
)

logger = get_logger(__name__)


class IELTSExaminerAgentNew(Agent):
    """
    Enhanced IELTS Examiner Agent with clean architecture.
    
    This agent conducts comprehensive IELTS speaking tests with proper
    validation, error handling, and business logic separation.
    """
    
    def __init__(self, session_questions: Dict[str, str]):
        """
        Initialize the IELTS examiner agent.
        
        Args:
            session_questions: Dictionary with questions for each part
        """
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
        
        # Validate session questions
        self._validate_session_questions(session_questions)
        
        # Get scoring criteria from question service
        question_service = get_question_service()
        scoring_criteria = question_service.get_scoring_criteria_json()
        
        # Generate instructions with session questions
        instructions = self._generate_instructions(session_questions, scoring_criteria)
        
        # Initialize parent with tools and instructions
        super().__init__(
            tools=[
                save_test_result_to_json,
                create_new_student_record,
                get_student_performance_analytics,
                get_user_learning_recommendations
            ],
            instructions=instructions
        )
        
        self.logger.info(
            "IELTS Examiner Agent initialized",
            extra={"extra_fields": {
                "has_part1": bool(session_questions.get('part1')),
                "has_part2": bool(session_questions.get('part2')),
                "has_part3": bool(session_questions.get('part3')),
                "tools_count": len(self.tools) if hasattr(self, 'tools') else 0
            }}
        )
    
    def _validate_session_questions(self, questions: Dict[str, str]) -> None:
        """
        Validate that session questions are properly formatted.
        
        Args:
            questions: Dictionary with session questions
            
        Raises:
            ValueError: If questions are invalid
        """
        required_parts = ['part1', 'part2', 'part3']
        
        for part in required_parts:
            if part not in questions:
                raise ValueError(f"Missing required question part: {part}")
            
            if not isinstance(questions[part], str) or not questions[part].strip():
                raise ValueError(f"Invalid question for {part}: must be non-empty string")
        
        self.logger.debug(
            "Session questions validated successfully",
            extra={"extra_fields": {
                "part1_length": len(questions['part1']),
                "part2_length": len(questions['part2']),
                "part3_length": len(questions['part3'])
            }}
        )
    
    def _generate_instructions(self, questions: Dict[str, str], scoring_criteria: str) -> str:
        """
        Generate comprehensive instructions for the agent.
        
        Args:
            questions: Session-specific questions
            scoring_criteria: JSON string of scoring criteria
            
        Returns:
            Complete instruction string
        """
        instructions = f"""
You are an IELTS Speaking Examiner Agent and your name is Pistah.

Your purpose is to conduct a complete, professional IELTS speaking test. You MUST strictly follow the 3-part structure and use ONLY the questions provided below for this session.

## SESSION-SPECIFIC QUESTIONS:

### Part 1: Introduction and Interview (4-5 minutes)
- You MUST ask the user the following question exactly as it is written:
- **Question:** "{questions['part1']}"

### Part 2: Long Turn (3-4 minutes)
- You MUST give the user the following topic exactly as it is written:
- **Topic:** "{questions['part2']}"
- After presenting the topic, give the user 1 minute to prepare and then ask them to speak for up to 2 minutes.

### Part 3: Two-way Discussion (4-5 minutes)
- After the user finishes their Part 2 talk, you MUST ask them the following follow-up question exactly as it is written:
- **Question:** "{questions['part3']}"

## ASSESSMENT AND SCORING
You must evaluate the user on the 4 official IELTS criteria, each on a 0-9 scale. The detailed scoring criteria are provided below:

{scoring_criteria}

## ENHANCED FEATURES
Beyond the basic test, you can also:
- Provide detailed performance analytics using `get_student_performance_analytics(email)`
- Offer personalized learning recommendations using `get_user_learning_recommendations(email)`
- Create student records for new users using `create_new_student_record(email, name)`

## SAVE RESULTS AND PROVIDE FEEDBACK
After the test, you MUST perform the following actions:

**A. Create the Test Result:**
Generate a test result with this exact JSON structure:
```json
{{
  "answers": {{
    "Part 1": {{"questions": ["{questions['part1']}"], "responses": ["..."]}},
    "Part 2": {{"topic": "{questions['part2']}", "response": "..."}},
    "Part 3": {{"questions": ["{questions['part3']}"], "responses": ["..."]}}
  }},
  "band_score": X.X,
  "detailed_scores": {{
    "fluency_coherence": X.X,
    "lexical_resource": X.X,
    "grammatical_accuracy": X.X,
    "pronunciation": X.X
  }},
  "feedback": {{
    "strengths": ["..."],
    "improvements": ["..."],
    "detailed_feedback": {{
      "fluency_coherence": "...",
      "lexical_resource": "...",
      "grammatical_accuracy": "...",
      "pronunciation": "..."
    }},
    "examiner_notes": "..."
  }},
  "test_status": "completed",
  "difficulty_level": "intermediate"
}}
```

**B. Save the Result:**
- Call the `save_test_result_to_json(email, test_result)` function. The user's email will be provided in the session instructions.

**C. Deliver Feedback to the User:**
- Clearly present their overall band score, strengths, and areas for improvement.
- Be encouraging and constructive in your feedback.
- Provide specific examples from their performance.

## PROFESSIONAL GUIDELINES:
- Maintain a warm, professional, and encouraging demeanor throughout
- Provide clear instructions for each part of the test
- Give appropriate timing guidance but be flexible with natural conversation flow
- Ask follow-up questions naturally if responses are too brief
- Ensure the user feels comfortable and supported
- Use positive reinforcement throughout the test

## CRITICAL RULES:
- **DO NOT** ask any questions other than the ones provided above.
- **NEVER** ask for the user's name or personal details. This information will be provided to you.
- **ALWAYS** wait for the session-specific user data and instructions before you begin.
- **MUST** complete all three parts of the test before providing final assessment.
- **ENSURE** proper timing for each section while maintaining natural conversation flow.

## ERROR HANDLING:
- If any tool calls fail, continue with the test and mention any limitations in your feedback
- Always prioritize completing the test even if some features are unavailable
- Provide helpful error messages if technical issues occur

Wait for the session-specific user data and instructions before you begin the test.
        """
        
        self.logger.debug(
            "Agent instructions generated",
            extra={"extra_fields": {
                "instruction_length": len(instructions),
                "includes_scoring_criteria": "scoring criteria" in instructions.lower(),
                "includes_session_questions": all(q in instructions for q in questions.values())
            }}
        )
        
        return instructions.strip()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session configuration.
        
        Returns:
            Dictionary with session information
        """
        return {
            "agent_type": "IELTSExaminerAgentNew",
            "tools_available": [tool.__name__ for tool in self.tools] if hasattr(self, 'tools') else [],
            "architecture": "clean_architecture",
            "features": [
                "session_specific_questions",
                "comprehensive_scoring",
                "performance_analytics",
                "learning_recommendations",
                "enhanced_error_handling"
            ]
        } 