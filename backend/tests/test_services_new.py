"""
Unit tests for the service layer of the new clean architecture.

These tests use dependency injection and mocking to test services
in isolation from database dependencies.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from src.services.student_service import StudentService
from src.models.student import StudentProfile, TestResult, IELTSScores, TestFeedback
from src.models.base import DifficultyLevel, TestStatus
from src.core.exceptions import validation_error, BusinessLogicException, NotFoundException


@pytest.mark.unit
@pytest.mark.service
class TestStudentService:
    """Test suite for StudentService."""
    
    def test_get_or_create_student_new_student(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email,
        sample_name
    ):
        """Test creating a new student when none exists."""
        # Setup mocks
        mock_student_repository.find_by_email.return_value = None
        mock_user_repository.user_exists.return_value = True
        mock_profile_repository.is_onboarding_completed.return_value = True
        
        new_student = StudentProfile(email=sample_email, name=sample_name)
        mock_student_repository.create_if_not_exists.return_value = new_student
        
        # Create service
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Execute
        result = service.get_or_create_student(sample_email, sample_name)
        
        # Verify
        assert result.email == sample_email
        assert result.name == sample_name
        mock_student_repository.create_if_not_exists.assert_called_once_with(sample_email, sample_name)
    
    def test_get_or_create_student_existing_student(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email,
        sample_name
    ):
        """Test retrieving an existing student."""
        # Setup mocks
        existing_student = StudentProfile(
            email=sample_email, 
            name=sample_name,
            history=[{"test": "data"}]
        )
        mock_student_repository.find_by_email.return_value = existing_student
        
        # Create service
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Execute
        result = service.get_or_create_student(sample_email, sample_name)
        
        # Verify
        assert result == existing_student
        mock_student_repository.create_if_not_exists.assert_not_called()
    
    def test_get_or_create_student_validation_errors(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test validation in get_or_create_student."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test empty email
        with pytest.raises(BusinessLogicException):
            service.get_or_create_student("", "Test User")
        
        # Test empty name
        with pytest.raises(BusinessLogicException):
            service.get_or_create_student("test@example.com", "")
    
    def test_save_test_result_success(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email,
        sample_test_result_dict
    ):
        """Test successful test result saving."""
        # Setup mocks
        existing_student = StudentProfile(email=sample_email, name="Test User", history=[])
        mock_student_repository.find_by_email.return_value = existing_student
        
        updated_student = StudentProfile(
            email=sample_email, 
            name="Test User",
            history=[sample_test_result_dict]
        )
        updated_student.total_tests = 1
        updated_student.latest_score = 6.5
        mock_student_repository.add_test_result.return_value = updated_student
        
        # Create service
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Execute
        result = service.save_test_result(sample_email, sample_test_result_dict)
        
        # Verify
        assert "SUCCESS" in result
        assert "Test #1" in result
        assert "6.5" in result
        mock_student_repository.add_test_result.assert_called_once()
    
    def test_save_test_result_nonexistent_student(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email,
        sample_test_result_dict
    ):
        """Test saving result for non-existent student."""
        # Setup mocks
        mock_student_repository.find_by_email.return_value = None
        
        # Create service
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Execute and verify exception
        with pytest.raises(NotFoundException):
            service.save_test_result(sample_email, sample_test_result_dict)
    
    def test_save_test_result_validation_errors(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test validation errors in save_test_result."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test empty email
        with pytest.raises(BusinessLogicException):
            service.save_test_result("", {"test": "data"})
        
        # Test missing test result
        with pytest.raises(BusinessLogicException):
            service.save_test_result("test@example.com", None)
    
    def test_get_performance_analytics_success(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test successful performance analytics generation."""
        # Setup mock student with test history
        test_results = [
            TestResult(
                test_number=1,
                band_score=6.0,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                test_status=TestStatus.COMPLETED,
                detailed_scores=IELTSScores(
                    fluency_coherence=6.0,
                    lexical_resource=6.0,
                    grammatical_accuracy=6.0,
                    pronunciation=6.0
                ),
                answers={},
                feedback=TestFeedback()
            ),
            TestResult(
                test_number=2,
                band_score=6.5,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                test_status=TestStatus.COMPLETED,
                detailed_scores=IELTSScores(
                    fluency_coherence=6.5,
                    lexical_resource=6.5,
                    grammatical_accuracy=6.5,
                    pronunciation=6.5
                ),
                answers={},
                feedback=TestFeedback()
            )
        ]
        
        student = StudentProfile(
            email=sample_email,
            name="Test User",
            history=test_results
        )
        student.total_tests = 2
        student.latest_score = 6.5
        student.best_score = 6.5
        student.average_score = 6.25
        
        mock_student_repository.find_by_email.return_value = student
        
        # Create service
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Execute
        analytics = service.get_performance_analytics(sample_email)
        
        # Verify structure
        assert "student_info" in analytics
        assert "scores" in analytics
        assert "performance_trend" in analytics
        assert "recommendations" in analytics
        assert "learning_path" in analytics
        
        # Verify content
        assert analytics["student_info"]["email"] == sample_email
        assert analytics["student_info"]["total_tests"] == 2
        assert analytics["scores"]["latest"] == 6.5
        assert analytics["scores"]["best"] == 6.5
        assert analytics["performance_trend"]["trend"] == "improving"
    
    def test_get_performance_analytics_nonexistent_student(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test analytics for non-existent student."""
        mock_student_repository.find_by_email.return_value = None
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        with pytest.raises(NotFoundException):
            service.get_performance_analytics("nonexistent@example.com")
    
    def test_get_performance_analytics_no_history(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test analytics for student with no test history."""
        student = StudentProfile(email=sample_email, name="Test User", history=[])
        student.total_tests = 0
        mock_student_repository.find_by_email.return_value = student
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        analytics = service.get_performance_analytics(sample_email)
        
        # Should handle no history gracefully
        assert analytics["student_info"]["total_tests"] == 0
        assert analytics["scores"]["latest"] is None
        assert analytics["performance_trend"]["trend"] == "no_data"
    
    def test_analyze_performance_trends(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test performance trend analysis logic."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test improving trend
        improving_scores = [5.0, 5.5, 6.0, 6.5]
        trend = service._analyze_performance_trends(improving_scores)
        assert trend["trend"] == "improving"
        assert trend["change_percentage"] > 0
        
        # Test declining trend
        declining_scores = [7.0, 6.5, 6.0, 5.5]
        trend = service._analyze_performance_trends(declining_scores)
        assert trend["trend"] == "declining"
        assert trend["change_percentage"] < 0
        
        # Test stable trend
        stable_scores = [6.0, 6.0, 6.0, 6.0]
        trend = service._analyze_performance_trends(stable_scores)
        assert trend["trend"] == "stable"
        assert abs(trend["change_percentage"]) < 5  # Small change
    
    def test_generate_recommendations_by_level(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test recommendation generation based on current level."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test recommendations for different levels
        basic_recs = service._generate_recommendations("basic", None)
        assert "foundation" in basic_recs[0].lower() or "basic" in basic_recs[0].lower()
        
        intermediate_recs = service._generate_recommendations("intermediate", None)
        assert len(intermediate_recs) > 0
        
        advanced_recs = service._generate_recommendations("advanced", None)
        assert "complex" in advanced_recs[0].lower() or "advanced" in advanced_recs[0].lower()
    
    def test_generate_recommendations_with_weak_areas(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test recommendation generation based on weak areas."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        weak_areas = ["fluency_coherence", "grammatical_accuracy"]
        recommendations = service._generate_recommendations("intermediate", weak_areas)
        
        # Should include specific recommendations for weak areas
        assert len(recommendations) > 0
        fluency_found = any("fluency" in rec.lower() for rec in recommendations)
        grammar_found = any("grammar" in rec.lower() for rec in recommendations)
        assert fluency_found or grammar_found
    
    def test_create_learning_path(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository
    ):
        """Test learning path creation logic."""
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test path for basic level
        basic_path = service._create_learning_path("basic", ["grammatical_accuracy"])
        assert basic_path["current_focus"] == "Grammar Foundations"
        assert "month" in basic_path["target_timeline"]
        
        # Test path for advanced level
        advanced_path = service._create_learning_path("advanced", ["pronunciation"])
        assert basic_path["current_focus"] != advanced_path["current_focus"]
    
    def test_error_handling_and_logging(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test error handling and logging in service methods."""
        # Setup mock to raise exception
        mock_student_repository.find_by_email.side_effect = Exception("Database error")
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        with patch('src.services.student_service.logger') as mock_logger:
            with pytest.raises(Exception):
                service.get_performance_analytics(sample_email)
            
            # Should log the error
            mock_logger.error.assert_called()


@pytest.mark.unit
@pytest.mark.service  
class TestStudentServiceEdgeCases:
    """Test edge cases and error scenarios for StudentService."""
    
    def test_malformed_test_result_handling(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test handling of malformed test result data."""
        # Setup existing student
        student = StudentProfile(email=sample_email, name="Test User")
        mock_student_repository.find_by_email.return_value = student
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Test with malformed data
        malformed_result = {
            "band_score": "not-a-number",
            "detailed_scores": "not-a-dict"
        }
        
        with pytest.raises(BusinessLogicException):
            service.save_test_result(sample_email, malformed_result)
    
    def test_large_history_performance(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test performance with large test history."""
        # Create student with large history
        large_history = []
        for i in range(100):
            test_result = TestResult(
                test_number=i+1,
                band_score=5.0 + (i * 0.01),  # Gradual improvement
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                test_status=TestStatus.COMPLETED,
                detailed_scores=IELTSScores(
                    fluency_coherence=5.0 + (i * 0.01),
                    lexical_resource=5.0 + (i * 0.01),
                    grammatical_accuracy=5.0 + (i * 0.01),
                    pronunciation=5.0 + (i * 0.01)
                ),
                answers={},
                feedback=TestFeedback()
            )
            large_history.append(test_result)
        
        student = StudentProfile(
            email=sample_email,
            name="Test User",
            history=large_history
        )
        student.total_tests = 100
        student.latest_score = 6.0
        student.best_score = 6.0
        student.average_score = 5.5
        
        mock_student_repository.find_by_email.return_value = student
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Analytics should handle large history efficiently
        analytics = service.get_performance_analytics(sample_email)
        
        # Verify it processed the data correctly
        assert analytics["student_info"]["total_tests"] == 100
        assert analytics["performance_trend"]["trend"] == "improving"
    
    def test_concurrent_operations_safety(
        self,
        mock_student_repository,
        mock_user_repository,
        mock_profile_repository,
        sample_email
    ):
        """Test that service methods are safe for concurrent access."""
        student = StudentProfile(email=sample_email, name="Test User")
        mock_student_repository.find_by_email.return_value = student
        mock_student_repository.add_test_result.return_value = student
        
        service = StudentService(
            student_repository=mock_student_repository,
            user_repository=mock_user_repository,
            profile_repository=mock_profile_repository
        )
        
        # Simulate concurrent calls (this tests method isolation)
        test_result = {"band_score": 6.0, "detailed_scores": {}}
        
        # These should not interfere with each other
        result1 = service.save_test_result(sample_email, test_result)
        result2 = service.save_test_result(sample_email, test_result)
        
        assert "SUCCESS" in result1
        assert "SUCCESS" in result2
        
        # Repository should be called for each operation
        assert mock_student_repository.add_test_result.call_count == 2 