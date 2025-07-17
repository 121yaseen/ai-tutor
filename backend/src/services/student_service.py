"""
Student service with business logic and dependency injection.

This module implements the service layer for student-related operations,
handling business logic, validation, and coordination between repositories.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ..repositories.student_repository import StudentRepository
from ..repositories.user_repository import UserRepository
from ..repositories.profile_repository import ProfileRepository
from ..models.student import StudentProfile, TestResult, TestFeedback, IELTSScores
from ..models.base import DifficultyLevel, TestStatus
from ..core.logging import get_logger, log_performance, set_request_context
from ..core.exceptions import (
    student_not_found,
    validation_error,
    BusinessLogicException,
    ErrorCode
)

logger = get_logger(__name__)


class StudentService:
    """Service for student-related business operations."""
    
    def __init__(
        self,
        student_repository: Optional[StudentRepository] = None,
        user_repository: Optional[UserRepository] = None,
        profile_repository: Optional[ProfileRepository] = None,
        use_test_db: bool = False
    ):
        """
        Initialize student service with dependency injection.
        
        Args:
            student_repository: Injected student repository
            user_repository: Injected user repository
            profile_repository: Injected profile repository
            use_test_db: Whether to use test database
        """
        self.student_repo = student_repository or StudentRepository(use_test_db)
        self.user_repo = user_repository or UserRepository(use_test_db)
        self.profile_repo = profile_repository or ProfileRepository(use_test_db)
        
        self.logger = get_logger(f"{__class__.__module__}.{__class__.__name__}")
    
    @log_performance("student_service_get_or_create")
    def get_or_create_student(self, email: str, name: Optional[str] = None) -> StudentProfile:
        """
        Get existing student or create new one.
        
        Args:
            email: Student's email address
            name: Student's name (will be fetched if not provided)
            
        Returns:
            StudentProfile instance
            
        Raises:
            ValidationException: If email is invalid
            BusinessLogicException: If business rules are violated
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        # Set logging context
        set_request_context(user_email=email)
        
        self.logger.info(f"Getting or creating student: {email}")
        
        # Try to find existing student
        existing_student = self.student_repo.find_by_email(email)
        if existing_student:
            self.logger.debug(f"Found existing student: {email}")
            return existing_student
        
        # Get user name if not provided
        if not name:
            name = self.user_repo.get_user_name(email)
            if not name:
                name = "User"  # Fallback
        
        # Create new student
        new_student = self.student_repo.create_if_not_exists(email, name)
        
        self.logger.info(
            f"Created new student: {email}",
            extra={"extra_fields": {"name": name}}
        )
        
        return new_student
    
    @log_performance("student_service_get_user_data")
    def get_user_data_for_instructions(self, email: str) -> tuple[str, Optional[float]]:
        """
        Fetch comprehensive user data and format for AI instructions.
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (formatted_instructions, latest_score)
            
        Raises:
            ValidationException: If email is invalid
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        set_request_context(user_email=email)
        
        self.logger.info(f"Fetching user data for instructions: {email}")
        
        # Get student data
        student = self.student_repo.find_by_email(email)
        
        # Get profile data
        profile_data = self.profile_repo.get_profile_for_instruction(email)
        
        # Build user data structure
        user_data = {
            "user_profile": profile_data,
            "history_summary": []
        }
        
        latest_score = None
        
        if student and student.history:
            completed_tests = [
                test for test in student.history 
                if test.test_status == TestStatus.COMPLETED
            ]
            
            user_data["history_summary"] = [
                {
                    "test_number": test.test_number,
                    "band_score": test.band_score,
                    "test_date": test.test_date.isoformat(),
                    "difficulty_level": test.difficulty_level.value
                }
                for test in completed_tests[:5]  # Last 5 tests
            ]
            
            if completed_tests:
                latest_score = completed_tests[0].band_score  # Most recent
        
        # Format instructions
        instruction_text = f"--- USER DATA ---\n{user_data}\n"
        
        if not student or not student.history:
            instruction_text += """--- NOTES ---
- This is the user's first session. Please be extra encouraging.
- Your goal is to establish a baseline score.
"""
        else:
            # Add performance summary
            performance_trend = student.get_performance_trend()
            instruction_text += f"""--- PERFORMANCE SUMMARY ---
- Total Tests: {student.total_tests}
- Latest Score: {student.latest_score}
- Best Score: {student.best_score}
- Average Score: {student.average_score}
- Current Level: {student.current_level.value}
- Performance Trend: {performance_trend.get('trend', 'unknown')}
"""
        
        instruction_text += "-----------------"
        
        self.logger.debug(
            f"Generated user instructions for: {email}",
            extra={"extra_fields": {
                "has_history": bool(student and student.history),
                "latest_score": latest_score,
                "total_tests": student.total_tests if student else 0
            }}
        )
        
        return instruction_text, latest_score
    
    @log_performance("student_service_save_test_result")
    def save_test_result(self, email: str, test_result_data: Dict[str, Any]) -> str:
        """
        Save test result with validation and business logic.
        
        Args:
            email: Student's email address
            test_result_data: Test result data dictionary
            
        Returns:
            Success message with summary
            
        Raises:
            ValidationException: If data is invalid
            BusinessLogicException: If business rules are violated
        """
        if not email:
            raise validation_error("Email is required", field_name="email")
        
        if not test_result_data:
            raise validation_error("Test result data is required")
        
        set_request_context(user_email=email)
        
        self.logger.info(f"Saving test result for: {email}")
        
        # Validate required fields
        required_fields = ['band_score', 'answers', 'detailed_scores']
        missing_fields = [field for field in required_fields if field not in test_result_data]
        if missing_fields:
            raise validation_error(
                f"Test result missing required fields: {missing_fields}",
                field_value=missing_fields
            )
        
        try:
            # Create TestResult object with validation
            test_result = TestResult(**test_result_data)
            
            # Get or create student
            student = self.get_or_create_student(email)
            
            # Check for duplicate test (business rule)
            if self._is_duplicate_test(student, test_result):
                raise BusinessLogicException(
                    "Duplicate test detected within short time period",
                    error_code=ErrorCode.TEST_ALREADY_IN_PROGRESS,
                    user_email=email
                )
            
            # Add test result to student
            updated_student = self.student_repo.add_test_result(email, test_result)
            
            # Generate success message
            success_message = (
                f"SUCCESS: Test result saved for {updated_student.name}. "
                f"Test #{test_result.test_number} completed with band score: {test_result.band_score}. "
                f"Total tests taken: {updated_student.total_tests}"
            )
            
            self.logger.info(
                f"Test result saved successfully for: {email}",
                extra={"extra_fields": {
                    "test_number": test_result.test_number,
                    "band_score": test_result.band_score,
                    "total_tests": updated_student.total_tests
                }}
            )
            
            return success_message
            
        except Exception as e:
            if isinstance(e, (validation_error, BusinessLogicException)):
                raise
            
            self.logger.error(
                f"Error saving test result for: {email}",
                extra={"extra_fields": {"error": str(e)}},
                exc_info=True
            )
            
            raise BusinessLogicException(
                f"Failed to save test result: {e}",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                user_email=email,
                original_exception=e
            )
    
    def _is_duplicate_test(self, student: StudentProfile, new_test: TestResult) -> bool:
        """
        Check if test is a duplicate (business rule).
        
        Args:
            student: Student profile
            new_test: New test result
            
        Returns:
            True if duplicate is detected
        """
        if not student.history:
            return False
        
        # Check if there's a recent test (within last 5 minutes)
        recent_threshold = datetime.now(timezone.utc).timestamp() - 300  # 5 minutes
        
        for test in student.history:
            if test.test_date.timestamp() > recent_threshold:
                # Recent test found - check for similarity
                if (test.band_score == new_test.band_score and 
                    test.difficulty_level == new_test.difficulty_level):
                    return True
        
        return False
    
    @log_performance("student_service_get_difficulty_level")
    def get_difficulty_level(self, email: str) -> DifficultyLevel:
        """
        Determine appropriate difficulty level for user.
        
        Args:
            email: User's email address
            
        Returns:
            Appropriate difficulty level
        """
        student = self.student_repo.find_by_email(email)
        
        if not student or not student.latest_score:
            # Check profile for previous attempts
            profile_context = self.profile_repo.get_learning_context(email)
            previous_score = profile_context.get('previous_score')
            
            if previous_score:
                return DifficultyLevel.from_score(previous_score)
            
            return DifficultyLevel.INTERMEDIATE  # Default
        
        return student.current_level
    
    @log_performance("student_service_get_performance_analytics")
    def get_performance_analytics(self, email: str) -> Dict[str, Any]:
        """
        Get comprehensive performance analytics for a student.
        
        Args:
            email: Student's email address
            
        Returns:
            Dictionary with comprehensive analytics
            
        Raises:
            DatabaseException: If student not found
        """
        student = self.student_repo.find_by_email(email)
        if not student:
            raise student_not_found(email)
        
        # Get basic stats
        stats = self.student_repo.get_performance_stats(email)
        
        # Add advanced analytics
        analytics = {
            **stats,
            "advanced_metrics": self._calculate_advanced_metrics(student),
            "recommendations": self._generate_recommendations(student),
            "learning_path": self._suggest_learning_path(student)
        }
        
        return analytics
    
    def _calculate_advanced_metrics(self, student: StudentProfile) -> Dict[str, Any]:
        """Calculate advanced performance metrics."""
        if not student.history:
            return {}
        
        completed_tests = [
            test for test in student.history 
            if test.test_status == TestStatus.COMPLETED
        ]
        
        if not completed_tests:
            return {}
        
        # Score distribution
        scores = [test.band_score for test in completed_tests]
        
        # Skill analysis
        skill_scores = {
            'fluency_coherence': [],
            'lexical_resource': [],
            'grammatical_accuracy': [],
            'pronunciation': []
        }
        
        for test in completed_tests:
            if hasattr(test.detailed_scores, 'fluency_coherence'):
                skill_scores['fluency_coherence'].append(test.detailed_scores.fluency_coherence)
                skill_scores['lexical_resource'].append(test.detailed_scores.lexical_resource)
                skill_scores['grammatical_accuracy'].append(test.detailed_scores.grammatical_accuracy)
                skill_scores['pronunciation'].append(test.detailed_scores.pronunciation)
        
        metrics = {
            "score_distribution": {
                "min": min(scores),
                "max": max(scores),
                "median": sorted(scores)[len(scores)//2],
                "std_dev": self._calculate_std_dev(scores)
            },
            "consistency_score": self._calculate_consistency(scores),
            "improvement_rate": self._calculate_improvement_rate(scores),
            "skill_breakdown": {
                skill: {
                    "average": sum(scores)/len(scores) if scores else 0,
                    "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
                }
                for skill, scores in skill_scores.items() if scores
            }
        }
        
        return metrics
    
    def _calculate_std_dev(self, scores: List[float]) -> float:
        """Calculate standard deviation of scores."""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate consistency score (lower std_dev = higher consistency)."""
        if len(scores) < 2:
            return 1.0
        
        std_dev = self._calculate_std_dev(scores)
        # Normalize to 0-1 scale (lower std_dev = higher consistency)
        return max(0, 1 - (std_dev / 2))  # Assuming std_dev rarely exceeds 2
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate improvement rate over time."""
        if len(scores) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(scores)
        x_sum = sum(range(n))
        y_sum = sum(scores)
        xy_sum = sum(i * score for i, score in enumerate(scores))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _generate_recommendations(self, student: StudentProfile) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if not student.history:
            recommendations.append("Take your first practice test to get personalized feedback")
            return recommendations
        
        latest_test = student.history[0]
        
        # Score-based recommendations
        if student.latest_score < 5.0:
            recommendations.append("Focus on fundamental English skills and basic vocabulary")
        elif student.latest_score < 6.5:
            recommendations.append("Work on fluency and sentence structure complexity")
        elif student.latest_score < 7.5:
            recommendations.append("Practice advanced vocabulary and natural speech patterns")
        else:
            recommendations.append("Maintain excellence with challenging practice materials")
        
        # Trend-based recommendations
        trend = student.get_performance_trend()
        if trend["trend"] == "declining":
            recommendations.append("Review recent mistakes and focus on consistent practice")
        elif trend["trend"] == "improving":
            recommendations.append("Continue current study approach - great progress!")
        
        # Skill-specific recommendations
        if hasattr(latest_test, 'detailed_scores'):
            lowest_skill = min([
                ('fluency_coherence', latest_test.detailed_scores.fluency_coherence),
                ('lexical_resource', latest_test.detailed_scores.lexical_resource),
                ('grammatical_accuracy', latest_test.detailed_scores.grammatical_accuracy),
                ('pronunciation', latest_test.detailed_scores.pronunciation)
            ], key=lambda x: x[1])
            
            skill_recommendations = {
                'fluency_coherence': "Practice speaking continuously without long pauses",
                'lexical_resource': "Expand vocabulary and practice using varied expressions",
                'grammatical_accuracy': "Focus on complex sentence structures and accuracy",
                'pronunciation': "Work on clear pronunciation and natural intonation"
            }
            
            recommendations.append(skill_recommendations[lowest_skill[0]])
        
        return recommendations
    
    def _suggest_learning_path(self, student: StudentProfile) -> Dict[str, Any]:
        """Suggest personalized learning path."""
        if not student.latest_score:
            return {
                "current_focus": "Assessment",
                "next_steps": ["Take diagnostic test", "Identify strengths and weaknesses"],
                "target_timeline": "1-2 weeks"
            }
        
        current_level = student.current_level
        target_score = student.latest_score + 0.5  # Incremental improvement
        
        learning_path = {
            "current_level": current_level.value,
            "current_score": student.latest_score,
            "target_score": min(9.0, target_score),
            "estimated_timeline": self._estimate_timeline(student.latest_score, target_score),
            "recommended_frequency": "2-3 practice sessions per week",
            "focus_areas": self._get_focus_areas(current_level)
        }
        
        return learning_path
    
    def _estimate_timeline(self, current_score: float, target_score: float) -> str:
        """Estimate timeline for score improvement."""
        score_gap = target_score - current_score
        
        if score_gap <= 0.5:
            return "2-4 weeks"
        elif score_gap <= 1.0:
            return "1-2 months"
        elif score_gap <= 1.5:
            return "2-3 months"
        else:
            return "3-6 months"
    
    def _get_focus_areas(self, level: DifficultyLevel) -> List[str]:
        """Get focus areas based on difficulty level."""
        focus_areas = {
            DifficultyLevel.BASIC: [
                "Basic vocabulary building",
                "Simple sentence structures",
                "Clear pronunciation",
                "Confidence building"
            ],
            DifficultyLevel.INTERMEDIATE: [
                "Complex sentence structures",
                "Academic vocabulary",
                "Fluency development",
                "Coherent idea organization"
            ],
            DifficultyLevel.ADVANCED: [
                "Idiomatic expressions",
                "Natural speech patterns",
                "Advanced discourse markers",
                "Sophisticated argumentation"
            ]
        }
        
        return focus_areas.get(level, focus_areas[DifficultyLevel.INTERMEDIATE]) 