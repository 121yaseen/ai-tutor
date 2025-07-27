"""
Question service for IELTS test question management.

This module handles the selection and management of IELTS questions
with proper validation and business logic.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..models.base import DifficultyLevel, TestPart
from ..core.config import settings
from ..core.logging import get_logger, log_performance
from ..core.exceptions import (
    configuration_error,
    validation_error,
    BusinessLogicException,
    ErrorCode
)

logger = get_logger(__name__)


@dataclass
class QuestionSet:
    """Represents a set of questions for a complete IELTS test."""
    
    part1_main: str
    part1_follow_ups: List[str]
    part2_topic: str
    part3_main: str
    part3_follow_ups: List[str]
    difficulty: DifficultyLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by agent."""
        return {
            "part1": {
                "main_question": self.part1_main,
                "follow_up_questions": self.part1_follow_ups
            },
            "part2": {
                "topic": self.part2_topic
            },
            "part3": {
                "main_question": self.part3_main,
                "follow_up_questions": self.part3_follow_ups
            }
        }


class QuestionService:
    """Service for managing IELTS test questions."""
    
    def __init__(self):
        """Initialize the question service."""
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
        self._questions_cache: Optional[Dict[str, Any]] = None
        self._scoring_criteria_cache: Optional[Dict[str, Any]] = None
        
        # Load initial data
        self._load_questions()
        self._load_scoring_criteria()
    
    def _load_questions(self) -> None:
        """Load questions from configuration file."""
        try:
            questions_file = settings.app.questions_file
            file_path = Path(__file__).parent.parent / "config/agent_data" / questions_file
            
            if not file_path.exists():
                raise configuration_error(
                    f"Questions file not found: {file_path}",
                    config_key="questions_file"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self._questions_cache = json.load(f)
            
            # Validate questions structure
            self._validate_questions_structure(self._questions_cache)
            
            self.logger.info(
                "Questions loaded successfully",
                extra={"extra_fields": {
                    "file_path": str(file_path),
                    "total_parts": len(self._questions_cache),
                    "difficulties": list(self._questions_cache.get("part1", {}).keys())
                }}
            )
            
        except Exception as e:
            if isinstance(e, configuration_error):
                raise
            
            self.logger.error(
                "Failed to load questions",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise configuration_error(
                f"Failed to load questions: {e}",
                config_key="questions_file",
                original_exception=e
            )
    
    def _load_scoring_criteria(self) -> None:
        """Load scoring criteria from configuration file."""
        try:
            criteria_file = settings.app.scoring_criteria_file
            file_path = Path(__file__).parent.parent / "config/agent_data" / criteria_file
            
            if not file_path.exists():
                raise configuration_error(
                    f"Scoring criteria file not found: {file_path}",
                    config_key="scoring_criteria_file"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self._scoring_criteria_cache = json.load(f)
            
            # Validate scoring criteria structure
            self._validate_scoring_criteria_structure(self._scoring_criteria_cache)
            
            self.logger.info(
                "Scoring criteria loaded successfully",
                extra={"extra_fields": {
                    "file_path": str(file_path),
                    "criteria_count": len(self._scoring_criteria_cache)
                }}
            )
            
        except Exception as e:
            if isinstance(e, configuration_error):
                raise
            
            self.logger.error(
                "Failed to load scoring criteria",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise configuration_error(
                f"Failed to load scoring criteria: {e}",
                config_key="scoring_criteria_file",
                original_exception=e
            )
    
    def _validate_questions_structure(self, questions: Dict[str, Any]) -> None:
        """Validate the structure of questions data."""
        required_parts = ["part1", "part2", "part3"]
        required_difficulties = ["basic", "intermediate", "advanced"]
        
        for part in required_parts:
            if part not in questions:
                raise validation_error(f"Missing required part: {part}")
            
            part_data = questions[part]
            if not isinstance(part_data, dict):
                raise validation_error(f"Part {part} must be a dictionary")
            
            for difficulty in required_difficulties:
                if difficulty not in part_data:
                    raise validation_error(f"Missing difficulty '{difficulty}' in {part}")
                
                questions_list = part_data[difficulty]
                if not isinstance(questions_list, list) or not questions_list:
                    raise validation_error(f"Part {part}, difficulty {difficulty} must be a non-empty list")
                
                # Validate question structure based on part
                for i, question_item in enumerate(questions_list):
                    if not isinstance(question_item, dict):
                        raise validation_error(f"Question item {i} in {part}, {difficulty} must be a dictionary")
                    
                    if part == "part1":
                        if "main_question" not in question_item:
                            raise validation_error(f"Part 1 question {i} missing 'main_question'")
                        if "follow_up_questions" not in question_item:
                            raise validation_error(f"Part 1 question {i} missing 'follow_up_questions'")
                        if not isinstance(question_item["follow_up_questions"], list):
                            raise validation_error(f"Part 1 question {i} 'follow_up_questions' must be a list")
                    
                    elif part == "part2":
                        if "topic" not in question_item:
                            raise validation_error(f"Part 2 question {i} missing 'topic'")
                        if "linked_part3_questions" not in question_item:
                            raise validation_error(f"Part 2 question {i} missing 'linked_part3_questions'")
                        if not isinstance(question_item["linked_part3_questions"], list):
                            raise validation_error(f"Part 2 question {i} 'linked_part3_questions' must be a list")
                    
                    elif part == "part3":
                        if "main_question" not in question_item:
                            raise validation_error(f"Part 3 question {i} missing 'main_question'")
                        if "follow_up_questions" not in question_item:
                            raise validation_error(f"Part 3 question {i} missing 'follow_up_questions'")
                        if not isinstance(question_item["follow_up_questions"], list):
                            raise validation_error(f"Part 3 question {i} 'follow_up_questions' must be a list")
    
    def _validate_scoring_criteria_structure(self, criteria: Dict[str, Any]) -> None:
        """Validate the structure of scoring criteria data."""
        required_criteria = ["fluency_coherence", "lexical_resource", "grammatical_accuracy", "pronunciation"]
        
        for criterion in required_criteria:
            if criterion not in criteria:
                raise validation_error(f"Missing required scoring criterion: {criterion}")
            
            criterion_data = criteria[criterion]
            if not isinstance(criterion_data, dict):
                raise validation_error(f"Scoring criterion {criterion} must be a dictionary")
    
    @property
    def questions(self) -> Dict[str, Any]:
        """Get questions data (cached)."""
        if self._questions_cache is None:
            self._load_questions()
        return self._questions_cache
    
    @property
    def scoring_criteria(self) -> Dict[str, Any]:
        """Get scoring criteria data (cached)."""
        if self._scoring_criteria_cache is None:
            self._load_scoring_criteria()
        return self._scoring_criteria_cache
    
    @log_performance("question_service_get_difficulty_level")
    def get_difficulty_level(self, score: Optional[float]) -> DifficultyLevel:
        """
        Determine appropriate difficulty level based on band score.
        
        Args:
            score: IELTS band score (0-9) or None
            
        Returns:
            Appropriate difficulty level
        """
        if score is None:
            self.logger.debug("No score provided, defaulting to intermediate difficulty")
            return DifficultyLevel.INTERMEDIATE
        
        difficulty = DifficultyLevel.from_score(score)
        
        self.logger.debug(
            f"Determined difficulty level: {difficulty.value}",
            extra={"extra_fields": {"score": score}}
        )
        
        return difficulty
    
    @log_performance("question_service_select_questions")
    def select_session_questions(
        self,
        difficulty: DifficultyLevel,
        exclude_recent: Optional[List[Dict[str, str]]] = None
    ) -> QuestionSet:
        """
        Select random questions for a session based on difficulty.
        
        Args:
            difficulty: Difficulty level for question selection
            exclude_recent: Recently used questions to avoid (optional)
            
        Returns:
            QuestionSet with selected questions
            
        Raises:
            BusinessLogicException: If question selection fails
        """
        try:
            difficulty_key = difficulty.value
            questions_data = self.questions
            
            # Validate difficulty exists
            if not all(difficulty_key in questions_data[part] for part in ["part1", "part2", "part3"]):
                raise BusinessLogicException(
                    f"Difficulty level '{difficulty_key}' not available",
                    error_code=ErrorCode.QUESTION_SELECTION_ERROR,
                    details={"difficulty": difficulty_key}
                )
            
            # Get available questions for each part
            part1_questions = questions_data["part1"][difficulty_key].copy()
            part2_questions = questions_data["part2"][difficulty_key].copy()
            part3_questions = questions_data["part3"][difficulty_key].copy()
            
            # Remove recently used questions if provided
            if exclude_recent:
                part1_questions = self._filter_recent_questions(part1_questions, exclude_recent, "part1")
                part2_questions = self._filter_recent_questions(part2_questions, exclude_recent, "part2")
                part3_questions = self._filter_recent_questions(part3_questions, exclude_recent, "part3")
            
            # Ensure we have questions available
            if not part1_questions or not part2_questions or not part3_questions:
                self.logger.warning(
                    "Some question pools are empty after filtering, using full pools",
                    extra={"extra_fields": {
                        "difficulty": difficulty_key,
                        "part1_available": len(part1_questions),
                        "part2_available": len(part2_questions),
                        "part3_available": len(part3_questions)
                    }}
                )
                
                # Fall back to full pools if filtering left us with empty lists
                part1_questions = questions_data["part1"][difficulty_key]
                part2_questions = questions_data["part2"][difficulty_key]
                part3_questions = questions_data["part3"][difficulty_key]
            
            
            # Select random Part 1 question set
            selected_part1_set = random.choice(part1_questions)
            part1_main = selected_part1_set["main_question"]
            part1_follow_ups = selected_part1_set["follow_up_questions"]
            
            # Select random Part 2 topic
            selected_part2_set = random.choice(part2_questions)
            part2_topic = selected_part2_set["topic"]
            linked_part3_questions = selected_part2_set["linked_part3_questions"]
            
            # Select random Part 3 question set (independent of Part 2 for variety)
            selected_part3_set = random.choice(part3_questions)
            part3_main = selected_part3_set["main_question"]
            part3_follow_ups = selected_part3_set["follow_up_questions"]
            
            # Create question set with linked topics
            question_set = QuestionSet(
                part1_main=part1_main,
                part1_follow_ups=part1_follow_ups,
                part2_topic=part2_topic,
                part3_main=part3_main,
                part3_follow_ups=part3_follow_ups,
                difficulty=difficulty
            )
            
            self.logger.info(
                f"Selected questions for difficulty '{difficulty_key}'",
                extra={"extra_fields": {
                    "difficulty": difficulty_key,
                    "part1_main": part1_main[:50] + "..." if len(part1_main) > 50 else part1_main,
                    "part1_follow_ups_count": len(part1_follow_ups),
                    "part2_topic": part2_topic[:50] + "..." if len(part2_topic) > 50 else part2_topic,
                    "part3_main": part3_main[:50] + "..." if len(part3_main) > 50 else part3_main,
                    "part3_follow_ups_count": len(part3_follow_ups),
                    "linked_part3_questions_count": len(linked_part3_questions)
                }}
            )
            
            return question_set
            
        except Exception as e:
            if isinstance(e, BusinessLogicException):
                raise
            
            self.logger.error(
                f"Error selecting questions for difficulty '{difficulty.value}'",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise BusinessLogicException(
                f"Failed to select questions: {e}",
                error_code=ErrorCode.QUESTION_SELECTION_ERROR,
                details={"difficulty": difficulty.value},
                original_exception=e
            )
    
    def _filter_recent_questions(
        self,
        available_questions: List[str],
        recent_questions: List[Dict[str, str]],
        part: str
    ) -> List[str]:
        """
        Filter out recently used questions from available pool.
        
        Args:
            available_questions: List of available questions
            recent_questions: List of recently used question sets
            part: Test part being filtered
            
        Returns:
            Filtered list of questions
        """
        if not recent_questions:
            return available_questions
        
        # Extract questions used in this part from recent sessions
        used_questions = set()
        for question_set in recent_questions:
            if part in question_set:
                used_questions.add(question_set[part])
        
        # Filter out used questions
        filtered = [q for q in available_questions if q not in used_questions]
        
        # Return filtered list or original if all were filtered out
        return filtered if filtered else available_questions
    
    @log_performance("question_service_get_scoring_criteria_json")
    def get_scoring_criteria_json(self) -> str:
        """
        Get scoring criteria as formatted JSON string.
        
        Returns:
            JSON string of scoring criteria
        """
        return json.dumps(self.scoring_criteria, indent=2)
    
    def get_questions_for_part(self, part: TestPart, difficulty: DifficultyLevel) -> List[str]:
        """
        Get all available questions for a specific part and difficulty.
        
        Args:
            part: Test part
            difficulty: Difficulty level
            
        Returns:
            List of available questions
        """
        part_key = part.value
        difficulty_key = difficulty.value
        
        questions_data = self.questions
        
        if part_key not in questions_data:
            raise validation_error(f"Invalid test part: {part_key}")
        
        if difficulty_key not in questions_data[part_key]:
            raise validation_error(f"Invalid difficulty for {part_key}: {difficulty_key}")
        
        return questions_data[part_key][difficulty_key].copy()
    
    def get_question_stats(self) -> Dict[str, Any]:
        """
        Get statistics about available questions.
        
        Returns:
            Dictionary with question statistics
        """
        questions_data = self.questions
        stats = {
            "total_questions": 0,
            "by_part": {},
            "by_difficulty": {}
        }
        
        for part in ["part1", "part2", "part3"]:
            part_stats = {}
            for difficulty in ["basic", "intermediate", "advanced"]:
                count = len(questions_data[part][difficulty])
                part_stats[difficulty] = count
                stats["total_questions"] += count
                
                if difficulty not in stats["by_difficulty"]:
                    stats["by_difficulty"][difficulty] = 0
                stats["by_difficulty"][difficulty] += count
            
            stats["by_part"][part] = part_stats
        
        return stats
    
    def reload_questions(self) -> None:
        """Reload questions from configuration files."""
        self._questions_cache = None
        self._scoring_criteria_cache = None
        self._load_questions()
        self._load_scoring_criteria()
        
        self.logger.info("Questions and scoring criteria reloaded")


# Global instance for easy access
_question_service: Optional[QuestionService] = None


def get_question_service() -> QuestionService:
    """
    Get the global question service instance.
    
    Returns:
        QuestionService instance
    """
    global _question_service
    
    if _question_service is None:
        _question_service = QuestionService()
    
    return _question_service 