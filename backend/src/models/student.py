"""
Enhanced student models with proper validation and relationships.

This module defines the student-related data models with comprehensive validation,
proper typing, and business logic for the IELTS examination system.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from pydantic import Field, validator, root_validator

from .base import (
    BaseEntityModel, 
    TimestampMixin, 
    DifficultyLevel, 
    TestPart, 
    TestStatus,
    validate_email,
    validate_band_score,
    validate_non_empty_string
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class IELTSScores(BaseEntityModel):
    """Detailed IELTS scoring breakdown."""
    
    fluency_coherence: float = Field(
        ...,
        description="Fluency and Coherence score (0-9)",
        ge=0,
        le=9
    )
    lexical_resource: float = Field(
        ...,
        description="Lexical Resource score (0-9)",
        ge=0,
        le=9
    )
    grammatical_accuracy: float = Field(
        ...,
        description="Grammatical Range and Accuracy score (0-9)",
        ge=0,
        le=9
    )
    pronunciation: float = Field(
        ...,
        description="Pronunciation score (0-9)",
        ge=0,
        le=9
    )
    
    # Validators
    _validate_fluency = validator('fluency_coherence', allow_reuse=True)(validate_band_score)
    _validate_lexical = validator('lexical_resource', allow_reuse=True)(validate_band_score)
    _validate_grammar = validator('grammatical_accuracy', allow_reuse=True)(validate_band_score)
    _validate_pronunciation = validator('pronunciation', allow_reuse=True)(validate_band_score)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall band score from individual scores."""
        total = (
            self.fluency_coherence + 
            self.lexical_resource + 
            self.grammatical_accuracy + 
            self.pronunciation
        )
        average = total / 4
        # Round to nearest 0.5 as per IELTS standards
        return round(average * 2) / 2
    
    def to_summary_dict(self) -> Dict[str, float]:
        """Get a summary dictionary of all scores."""
        return {
            "fluency_coherence": self.fluency_coherence,
            "lexical_resource": self.lexical_resource,
            "grammatical_accuracy": self.grammatical_accuracy,
            "pronunciation": self.pronunciation,
            "overall_score": self.overall_score
        }


class TestAnswer(BaseEntityModel):
    """Model for test answers in each part."""
    
    part: TestPart = Field(..., description="Which part of the test")
    questions: List[str] = Field(
        default_factory=list,
        description="Questions asked in this part"
    )
    topic: Optional[str] = Field(
        None,
        description="Topic for Part 2 (if applicable)"
    )
    responses: List[str] = Field(
        default_factory=list,
        description="User responses to questions"
    )
    response: Optional[str] = Field(
        None,
        description="Single response for Part 2"
    )
    
    @validator('questions')
    def validate_questions(cls, v):
        """Ensure questions are not empty strings."""
        if not v:
            return v
        return [q.strip() for q in v if q and q.strip()]
    
    @validator('responses')
    def validate_responses(cls, v):
        """Ensure responses are not empty strings."""
        if not v:
            return v
        return [r.strip() for r in v if r and r.strip()]
    
    @root_validator
    def validate_part_specific_data(cls, values):
        """Validate data based on test part requirements."""
        part = values.get('part')
        questions = values.get('questions', [])
        topic = values.get('topic')
        responses = values.get('responses', [])
        response = values.get('response')
        
        if part == TestPart.PART_2:
            # Part 2 should have topic and single response
            if not topic and not response:
                raise ValueError("Part 2 must have either topic or response")
        else:
            # Parts 1 and 3 should have questions and responses
            if not questions and not responses:
                raise ValueError(f"{part} must have questions and responses")
        
        return values


class TestFeedback(BaseEntityModel):
    """Model for test feedback and improvement suggestions."""
    
    strengths: List[str] = Field(
        default_factory=list,
        description="User's strengths identified during the test"
    )
    improvements: List[str] = Field(
        default_factory=list,
        description="Areas for improvement"
    )
    detailed_feedback: Dict[str, str] = Field(
        default_factory=dict,
        description="Detailed feedback for each scoring criterion"
    )
    examiner_notes: Optional[str] = Field(
        None,
        description="Additional notes from the AI examiner"
    )
    
    @validator('strengths', 'improvements')
    def validate_feedback_lists(cls, v):
        """Ensure feedback items are not empty."""
        if not v:
            return v
        return [item.strip() for item in v if item and item.strip()]
    
    @validator('detailed_feedback')
    def validate_detailed_feedback(cls, v):
        """Validate detailed feedback structure."""
        if not v:
            return v
        
        # Ensure feedback values are not empty
        return {k: str(val).strip() for k, val in v.items() if val and str(val).strip()}


class TestResult(BaseEntityModel, TimestampMixin):
    """Comprehensive test result model."""
    
    test_number: int = Field(
        ...,
        description="Sequential test number for the student",
        ge=1
    )
    test_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the test was taken"
    )
    test_status: TestStatus = Field(
        default=TestStatus.COMPLETED,
        description="Status of the test"
    )
    difficulty_level: DifficultyLevel = Field(
        ...,
        description="Difficulty level of the test"
    )
    
    # Test content
    answers: Dict[str, TestAnswer] = Field(
        default_factory=dict,
        description="Answers for each part of the test"
    )
    
    # Scoring
    detailed_scores: IELTSScores = Field(
        ...,
        description="Detailed breakdown of IELTS scores"
    )
    band_score: float = Field(
        ...,
        description="Overall band score",
        ge=0,
        le=9
    )
    
    # Feedback
    feedback: TestFeedback = Field(
        default_factory=TestFeedback,
        description="Feedback and improvement suggestions"
    )
    
    # Session metadata
    session_id: Optional[str] = Field(
        None,
        description="LiveKit session identifier"
    )
    duration_minutes: Optional[int] = Field(
        None,
        description="Test duration in minutes",
        ge=0
    )
    
    # Validators
    _validate_band_score = validator('band_score', allow_reuse=True)(validate_band_score)
    
    @validator('answers')
    def validate_answers(cls, v):
        """Validate test answers structure."""
        if not v:
            return v
        
        # Convert string keys to TestPart enum if needed
        validated_answers = {}
        for key, answer in v.items():
            if isinstance(key, str):
                try:
                    part_key = TestPart(key)
                except ValueError:
                    # Try to match with enum values
                    part_mapping = {
                        "Part 1": TestPart.PART_1,
                        "Part 2": TestPart.PART_2,
                        "Part 3": TestPart.PART_3,
                        "part1": TestPart.PART_1,
                        "part2": TestPart.PART_2,
                        "part3": TestPart.PART_3,
                    }
                    part_key = part_mapping.get(key)
                    if not part_key:
                        continue  # Skip invalid keys
            else:
                part_key = key
            
            # Ensure answer is TestAnswer instance
            if isinstance(answer, dict):
                answer['part'] = part_key
                answer = TestAnswer(**answer)
            elif not isinstance(answer, TestAnswer):
                continue  # Skip invalid answers
            
            validated_answers[part_key.value] = answer
        
        return validated_answers
    
    @root_validator
    def validate_band_score_consistency(cls, values):
        """Ensure band score is consistent with detailed scores."""
        detailed_scores = values.get('detailed_scores')
        band_score = values.get('band_score')
        
        if detailed_scores and band_score is not None:
            calculated_score = detailed_scores.overall_score
            # Allow small differences due to rounding
            if abs(calculated_score - band_score) > 0.5:
                logger.warning(
                    f"Band score inconsistency: calculated={calculated_score}, provided={band_score}"
                )
                # Use calculated score as authoritative
                values['band_score'] = calculated_score
        
        return values
    
    def get_difficulty_progression(self) -> DifficultyLevel:
        """
        Suggest next difficulty level based on performance.
        
        Returns:
            Recommended difficulty level for next test
        """
        if self.band_score >= 7.0:
            return DifficultyLevel.ADVANCED
        elif self.band_score >= 5.0:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BASIC
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of test performance.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "test_number": self.test_number,
            "band_score": self.band_score,
            "difficulty_level": self.difficulty_level.value,
            "test_date": self.test_date.isoformat(),
            "detailed_scores": self.detailed_scores.to_summary_dict(),
            "strengths_count": len(self.feedback.strengths),
            "improvements_count": len(self.feedback.improvements),
            "duration_minutes": self.duration_minutes,
            "recommended_next_level": self.get_difficulty_progression().value
        }


class StudentProfile(BaseEntityModel, TimestampMixin):
    """Enhanced student profile model."""
    
    email: str = Field(..., description="Student's email address")
    name: str = Field(..., description="Student's full name")
    
    # Test history and performance
    history: List[TestResult] = Field(
        default_factory=list,
        description="Complete test history"
    )
    total_tests: int = Field(
        default=0,
        description="Total number of tests taken",
        ge=0
    )
    
    # Performance metrics
    current_level: DifficultyLevel = Field(
        default=DifficultyLevel.INTERMEDIATE,
        description="Current difficulty level"
    )
    latest_score: Optional[float] = Field(
        None,
        description="Most recent band score",
        ge=0,
        le=9
    )
    best_score: Optional[float] = Field(
        None,
        description="Best band score achieved",
        ge=0,
        le=9
    )
    average_score: Optional[float] = Field(
        None,
        description="Average band score across all tests",
        ge=0,
        le=9
    )
    
    # Validators
    _validate_email = validator('email', allow_reuse=True)(validate_email)
    _validate_name = validator('name', allow_reuse=True)(
        lambda v: validate_non_empty_string(v, "name")
    )
    _validate_latest_score = validator('latest_score', allow_reuse=True)(
        lambda v: validate_band_score(v) if v is not None else v
    )
    _validate_best_score = validator('best_score', allow_reuse=True)(
        lambda v: validate_band_score(v) if v is not None else v
    )
    _validate_average_score = validator('average_score', allow_reuse=True)(
        lambda v: validate_band_score(v) if v is not None else v
    )
    
    @validator('history')
    def validate_history(cls, v):
        """Validate and sort test history."""
        if not v:
            return v
        
        # Ensure all items are TestResult instances
        validated_history = []
        for item in v:
            if isinstance(item, dict):
                try:
                    test_result = TestResult(**item)
                    validated_history.append(test_result)
                except Exception as e:
                    logger.warning(f"Skipping invalid test result: {e}")
            elif isinstance(item, TestResult):
                validated_history.append(item)
        
        # Sort by test date (newest first)
        return sorted(validated_history, key=lambda x: x.test_date, reverse=True)
    
    @root_validator
    def update_computed_fields(cls, values):
        """Update computed fields based on history."""
        history = values.get('history', [])
        
        if history:
            scores = [test.band_score for test in history if test.test_status == TestStatus.COMPLETED]
            
            values['total_tests'] = len(history)
            values['latest_score'] = scores[0] if scores else None
            values['best_score'] = max(scores) if scores else None
            values['average_score'] = round(sum(scores) / len(scores), 1) if scores else None
            
            # Update current level based on latest score
            if values['latest_score'] is not None:
                values['current_level'] = DifficultyLevel.from_score(values['latest_score'])
        
        return values
    
    def add_test_result(self, test_result: TestResult) -> None:
        """
        Add a new test result and update computed fields.
        
        Args:
            test_result: New test result to add
        """
        # Set test number
        test_result.test_number = len(self.history) + 1
        
        # Add to history
        self.history.insert(0, test_result)  # Add at beginning (newest first)
        
        # Update computed fields
        self._update_computed_fields()
        
        # Update timestamp
        self.update_timestamp()
        
        logger.info(
            f"Added test result for student {self.email}",
            extra={"extra_fields": {
                "test_number": test_result.test_number,
                "band_score": test_result.band_score,
                "total_tests": self.total_tests
            }}
        )
    
    def _update_computed_fields(self) -> None:
        """Update computed fields based on current history."""
        if not self.history:
            return
        
        completed_tests = [
            test for test in self.history 
            if test.test_status == TestStatus.COMPLETED
        ]
        
        if completed_tests:
            scores = [test.band_score for test in completed_tests]
            
            self.total_tests = len(self.history)
            self.latest_score = scores[0]  # history is sorted newest first
            self.best_score = max(scores)
            self.average_score = round(sum(scores) / len(scores), 1)
            self.current_level = DifficultyLevel.from_score(self.latest_score)
    
    def get_performance_trend(self, last_n_tests: int = 5) -> Dict[str, Any]:
        """
        Analyze performance trend over recent tests.
        
        Args:
            last_n_tests: Number of recent tests to analyze
            
        Returns:
            Performance trend analysis
        """
        if len(self.history) < 2:
            return {"trend": "insufficient_data", "tests_count": len(self.history)}
        
        recent_tests = self.history[:last_n_tests]
        completed_tests = [
            test for test in recent_tests 
            if test.test_status == TestStatus.COMPLETED
        ]
        
        if len(completed_tests) < 2:
            return {"trend": "insufficient_data", "tests_count": len(completed_tests)}
        
        scores = [test.band_score for test in completed_tests]
        first_score = scores[-1]  # Oldest in the recent set
        last_score = scores[0]   # Newest
        
        improvement = last_score - first_score
        
        if improvement > 0.5:
            trend = "improving"
        elif improvement < -0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "improvement": improvement,
            "tests_analyzed": len(completed_tests),
            "score_range": {"min": min(scores), "max": max(scores)},
            "average_recent": round(sum(scores) / len(scores), 1)
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Generate learning insights based on test history.
        
        Returns:
            Learning insights and recommendations
        """
        if not self.history:
            return {"message": "No test history available"}
        
        completed_tests = [
            test for test in self.history 
            if test.test_status == TestStatus.COMPLETED
        ]
        
        if not completed_tests:
            return {"message": "No completed tests available"}
        
        # Analyze strengths and weaknesses
        all_strengths = []
        all_improvements = []
        
        for test in completed_tests:
            all_strengths.extend(test.feedback.strengths)
            all_improvements.extend(test.feedback.improvements)
        
        # Get performance trend
        trend = self.get_performance_trend()
        
        return {
            "total_tests": len(completed_tests),
            "performance_trend": trend,
            "current_level": self.current_level.value,
            "score_progression": {
                "latest": self.latest_score,
                "best": self.best_score,
                "average": self.average_score
            },
            "common_strengths": list(set(all_strengths))[:5],  # Top 5 unique strengths
            "areas_for_improvement": list(set(all_improvements))[:5],  # Top 5 unique areas
            "recommendation": self._get_recommendation()
        }
    
    def _get_recommendation(self) -> str:
        """Generate a recommendation based on performance."""
        if not self.latest_score:
            return "Take your first test to get personalized recommendations."
        
        trend = self.get_performance_trend()
        
        if trend["trend"] == "improving":
            return f"Great progress! Continue practicing at {self.current_level.value} level."
        elif trend["trend"] == "declining":
            return "Consider reviewing fundamentals and taking practice tests."
        else:
            if self.latest_score < 5.0:
                return "Focus on basic English skills and vocabulary building."
            elif self.latest_score < 7.0:
                return "Work on fluency and complex sentence structures."
            else:
                return "Maintain your excellent level with advanced practice."


# Legacy model for backward compatibility
class StudentPerformance(BaseEntityModel):
    """Legacy student performance model for backward compatibility."""
    
    email: str = Field(..., description="Student's email address")
    name: str = Field(..., description="Student's name")
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Test history as list of dictionaries"
    )
    
    _validate_email = validator('email', allow_reuse=True)(validate_email)
    _validate_name = validator('name', allow_reuse=True)(
        lambda v: validate_non_empty_string(v, "name")
    )
    
    def to_student_profile(self) -> StudentProfile:
        """Convert to enhanced StudentProfile model."""
        # Convert history to TestResult objects
        test_results = []
        for i, test_data in enumerate(self.history):
            try:
                # Ensure test_number is set
                if 'test_number' not in test_data:
                    test_data['test_number'] = i + 1
                
                test_result = TestResult(**test_data)
                test_results.append(test_result)
            except Exception as e:
                logger.warning(
                    f"Skipping invalid test result during conversion: {e}",
                    extra={"extra_fields": {"test_data": test_data}}
                )
        
        return StudentProfile(
            email=self.email,
            name=self.name,
            history=test_results
        ) 