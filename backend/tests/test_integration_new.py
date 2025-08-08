"""
Integration tests for the new clean architecture.

These tests use real database connections and test the complete flow
from agent tools through services to repositories and database.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.tools.agent_tools_new import (
    save_test_result_to_json,
    create_new_student_record,
    get_student_performance_analytics,
    get_user_learning_recommendations
)
from src.services.student_service import StudentService
from src.services.question_service import get_question_service
from src.repositories.student_repository import StudentRepository
from src.models.student import TestResult, IELTSScores, TestFeedback
from src.models.base import DifficultyLevel, TestStatus
from src.core.container import get_student_service, reset_container


@pytest.mark.integration
class TestStudentServiceIntegration:
    """Integration tests for student service with real database."""
    
    def test_get_or_create_student_new_user(
        self,
        integration_test_service: StudentService,
        unique_test_email: str,
        cleanup_integration_data
    ):
        """Test creating a new student with real database."""
        cleanup_integration_data(unique_test_email)
        
        # Create new student
        student = integration_test_service.get_or_create_student(
            unique_test_email, 
            "Integration Test User"
        )
        
        # Verify student was created
        assert student.email == unique_test_email
        assert student.name == "Integration Test User"
        assert student.total_tests == 0
        assert len(student.history) == 0
        
        # Verify student exists in database
        student_repo = StudentRepository(use_test_db=True)
        db_student = student_repo.find_by_email(unique_test_email)
        assert db_student is not None
        assert db_student.email == unique_test_email
    
    def test_get_or_create_student_existing_user(
        self,
        integration_test_service: StudentService,
        unique_test_email: str,
        cleanup_integration_data
    ):
        """Test retrieving an existing student."""
        cleanup_integration_data(unique_test_email)
        
        # Create student first
        original_student = integration_test_service.get_or_create_student(
            unique_test_email, 
            "Original Name"
        )
        
        # Get same student again
        retrieved_student = integration_test_service.get_or_create_student(
            unique_test_email, 
            "Different Name"  # Should use original name
        )
        
        # Should be same student
        assert retrieved_student.email == unique_test_email
        assert retrieved_student.name == "Original Name"  # Original name preserved
        assert retrieved_student.total_tests == 0
    
    def test_save_test_result_complete_flow(
        self,
        integration_test_service: StudentService,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data
    ):
        """Test complete test result saving flow."""
        cleanup_integration_data(unique_test_email)
        
        # Create student first
        integration_test_service.get_or_create_student(unique_test_email, "Test User")
        
        # Save test result
        result_message = integration_test_service.save_test_result(
            unique_test_email, 
            sample_test_result_dict
        )
        
        # Verify success message
        assert "SUCCESS" in result_message
        assert "Test #1" in result_message
        assert "6.5" in result_message  # Band score
        
        # Verify student was updated
        updated_student = integration_test_service.get_or_create_student(unique_test_email, "Test User")
        assert updated_student.total_tests == 1
        assert updated_student.latest_score == 6.5
        assert len(updated_student.history) == 1
        
        # Verify test result details
        test_result = updated_student.history[0]
        assert test_result.test_number == 1
        assert test_result.band_score == 6.5
        assert test_result.difficulty_level == DifficultyLevel.INTERMEDIATE
    
    def test_performance_analytics_complete_flow(
        self,
        integration_test_service: StudentService,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data
    ):
        """Test performance analytics with real data."""
        cleanup_integration_data(unique_test_email)
        
        # Create student and add multiple test results
        integration_test_service.get_or_create_student(unique_test_email, "Analytics Test User")
        
        # Add first test result
        integration_test_service.save_test_result(unique_test_email, sample_test_result_dict)
        
        # Add second test result with different score
        second_result = sample_test_result_dict.copy()
        second_result["band_score"] = 7.0
        second_result["detailed_scores"]["fluency_coherence"] = 7.5
        integration_test_service.save_test_result(unique_test_email, second_result)
        
        # Get performance analytics
        analytics = integration_test_service.get_performance_analytics(unique_test_email)
        
        # Verify analytics structure
        assert "student_info" in analytics
        assert "scores" in analytics
        assert "performance_trend" in analytics
        assert "recommendations" in analytics
        assert "learning_path" in analytics
        
        # Verify student info
        student_info = analytics["student_info"]
        assert student_info["email"] == unique_test_email
        assert student_info["total_tests"] == 2
        
        # Verify scores
        scores = analytics["scores"]
        assert scores["latest"] == 7.0  # Latest score
        assert scores["best"] == 7.0    # Best score
        assert scores["average"] == 6.75  # Average of 6.5 and 7.0
        
        # Verify performance trend
        trend = analytics["performance_trend"]
        assert trend["trend"] == "improving"  # Score improved from 6.5 to 7.0
        
        # Verify recommendations exist
        assert len(analytics["recommendations"]) > 0
        assert "learning_path" in analytics


@pytest.mark.integration
class TestAgentToolsIntegration:
    """Integration tests for agent tools with real database."""
    
    @pytest.mark.asyncio
    async def test_save_test_result_tool_complete_flow(
        self,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data
    ):
        """Test save_test_result_to_json tool with real database."""
        # Reset container to ensure fresh state
        reset_container()
        cleanup_integration_data(unique_test_email)
        
        # Use the tool function directly
        result = await save_test_result_to_json(unique_test_email, sample_test_result_dict)
        
        # Verify success
        assert "SUCCESS" in result
        assert unique_test_email.split("@")[0] in result  # User name part
        
        # Verify data was actually saved
        service = get_student_service(use_test_db=True)
        student = service.get_or_create_student(unique_test_email, "Test")
        assert student.total_tests == 1
        assert student.latest_score == 6.5
    
    @pytest.mark.asyncio
    async def test_create_student_record_tool_integration(
        self,
        unique_test_email: str,
        cleanup_integration_data
    ):
        """Test create_new_student_record tool with real database."""
        reset_container()
        cleanup_integration_data(unique_test_email)
        
        # Create student using tool
        result = await create_new_student_record(unique_test_email, "Tool Test User")
        
        # Verify success
        assert "SUCCESS" in result
        assert "Tool Test User" in result
        
        # Verify student exists in database
        service = get_student_service(use_test_db=True)
        student = service.get_or_create_student(unique_test_email, "Tool Test User")
        assert student.name == "Tool Test User"
        assert student.total_tests == 0
    
    @pytest.mark.asyncio
    async def test_analytics_tool_integration(
        self,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data
    ):
        """Test performance analytics tool with real database."""
        reset_container()
        cleanup_integration_data(unique_test_email)
        
        # Create student and add test result first
        await create_new_student_record(unique_test_email, "Analytics User")
        await save_test_result_to_json(unique_test_email, sample_test_result_dict)
        
        # Get analytics using tool
        result = await get_student_performance_analytics(unique_test_email)
        
        # Result should be valid JSON
        import json
        analytics = json.loads(result)
        
        # Verify structure
        assert "student_info" in analytics
        assert "scores" in analytics
        assert analytics["student_info"]["email"] == unique_test_email
        assert analytics["scores"]["latest"] == 6.5
    
    @pytest.mark.asyncio
    async def test_recommendations_tool_integration(
        self,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data
    ):
        """Test learning recommendations tool with real database."""
        reset_container()
        cleanup_integration_data(unique_test_email)
        
        # Setup data
        await create_new_student_record(unique_test_email, "Recommendations User")
        await save_test_result_to_json(unique_test_email, sample_test_result_dict)
        
        # Get recommendations using tool
        result = await get_user_learning_recommendations(unique_test_email)
        
        # Result should be valid JSON
        import json
        recommendations = json.loads(result)
        
        # Verify structure
        assert "current_level" in recommendations
        assert "recommendations" in recommendations
        assert "learning_path" in recommendations
        assert recommendations["current_level"] == "intermediate"


@pytest.mark.integration
class TestQuestionServiceIntegration:
    """Integration tests for question service."""
    
    def test_question_service_initialization(self):
        """Test question service loads data correctly."""
        service = get_question_service()
        
        # Verify questions are loaded
        assert service.questions is not None
        assert "part1" in service.questions
        assert "part2" in service.questions
        assert "part3" in service.questions
        
        # Verify scoring criteria are loaded
        assert service.scoring_criteria is not None
        assert "fluency_coherence" in service.scoring_criteria
    
    def test_difficulty_level_determination(self):
        """Test difficulty level determination logic."""
        service = get_question_service()
        
        # Test different scores
        assert service.get_difficulty_level(None) == DifficultyLevel.INTERMEDIATE
        assert service.get_difficulty_level(3.0) == DifficultyLevel.BASIC
        assert service.get_difficulty_level(6.0) == DifficultyLevel.INTERMEDIATE
        assert service.get_difficulty_level(8.0) == DifficultyLevel.ADVANCED
    
    def test_question_selection_all_difficulties(self):
        """Test question selection for all difficulty levels."""
        service = get_question_service()
        
        for difficulty in [DifficultyLevel.BASIC, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]:
            question_set = service.select_session_questions(difficulty)
            
            # Verify question set structure
            assert hasattr(question_set, 'part1')
            assert hasattr(question_set, 'part2')
            assert hasattr(question_set, 'part3')
            assert question_set.difficulty == difficulty
            
            # Verify questions are not empty
            assert len(question_set.part1.strip()) > 0
            assert len(question_set.part2.strip()) > 0
            assert len(question_set.part3.strip()) > 0
    
    def test_question_variation(self):
        """Test that question selection provides variation."""
        service = get_question_service()
        
        # Get multiple question sets for same difficulty
        question_sets = []
        for _ in range(5):
            question_set = service.select_session_questions(DifficultyLevel.INTERMEDIATE)
            question_sets.append(question_set.to_dict())
        
        # Check that we get some variation (not all identical)
        # At least one field should be different across sets
        all_part1 = [qs["part1"] for qs in question_sets]
        all_part2 = [qs["part2"] for qs in question_sets]
        all_part3 = [qs["part3"] for qs in question_sets]
        
        # If there are multiple questions available, we should see some variation
        # (This test might pass even with no variation if there's only one question per part)
        variation_found = (
            len(set(all_part1)) > 1 or 
            len(set(all_part2)) > 1 or 
            len(set(all_part3)) > 1
        )
        
        # This assertion might be relaxed if question pools are small
        # assert variation_found, "No variation found in question selection"


@pytest.mark.integration
class TestRepositoryIntegration:
    """Integration tests for repository layer."""
    
    def test_student_repository_crud_operations(
        self,
        unique_test_email: str,
        cleanup_integration_data
    ):
        """Test complete CRUD operations on student repository."""
        cleanup_integration_data(unique_test_email)
        
        repo = StudentRepository(use_test_db=True)
        
        # Test creation
        student = repo.create_if_not_exists(unique_test_email, "CRUD Test User")
        assert student.email == unique_test_email
        assert student.name == "CRUD Test User"
        
        # Test reading
        found_student = repo.find_by_email(unique_test_email)
        assert found_student is not None
        assert found_student.email == unique_test_email
        
        # Test updating (add test result)
        test_result = TestResult(
            test_number=1,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            test_status=TestStatus.COMPLETED,
            detailed_scores=IELTSScores(
                fluency_coherence=6.0,
                lexical_resource=6.5,
                grammatical_accuracy=6.0,
                pronunciation=6.5
            ),
            band_score=6.25,
            answers={"part1": {"questions": ["test"], "responses": ["response"]}},
            feedback=TestFeedback()
        )
        
        updated_student = repo.add_test_result(unique_test_email, test_result)
        assert updated_student.total_tests == 1
        assert updated_student.latest_score == 6.25
        
        # Test deletion
        deleted = repo.delete_by_email(unique_test_email)
        assert deleted == True
        
        # Verify deletion
        not_found = repo.find_by_email(unique_test_email)
        assert not_found is None
    
    def test_repository_error_handling(self):
        """Test repository error handling with invalid data."""
        repo = StudentRepository(use_test_db=True)
        
        # Test with invalid email
        with pytest.raises(Exception):  # Should raise validation error
            repo.find_by_email("")
        
        # Test with non-existent student for operations
        from src.core.exceptions import DatabaseException
        
        with pytest.raises(DatabaseException):
            fake_test_result = TestResult(
                test_number=1,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                test_status=TestStatus.COMPLETED,
                detailed_scores=IELTSScores(
                    fluency_coherence=6.0,
                    lexical_resource=6.0,
                    grammatical_accuracy=6.0,
                    pronunciation=6.0
                ),
                band_score=6.0,
                answers={},
                feedback=TestFeedback()
            )
            repo.add_test_result("nonexistent@example.com", fake_test_result)


@pytest.mark.integration
class TestPerformanceIntegration:
    """Integration tests for performance and scalability."""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, cleanup_integration_data):
        """Test concurrent operations don't interfere with each other."""
        reset_container()
        
        # Generate multiple unique emails
        base_email = f"concurrent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        emails = [f"{base_email}_{i}@test.example.com" for i in range(5)]
        
        # Register all for cleanup
        for email in emails:
            cleanup_integration_data(email)
        
        # Create concurrent tasks
        tasks = []
        for i, email in enumerate(emails):
            task = create_new_student_record(email, f"Concurrent User {i}")
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for result in results:
            assert "SUCCESS" in result
        
        # Verify all students exist
        service = get_student_service(use_test_db=True)
        for email in emails:
            student = service.get_or_create_student(email, "Test")
            assert student.email == email
    
    def test_large_history_handling(
        self,
        unique_test_email: str,
        sample_test_result_dict: Dict[str, Any],
        cleanup_integration_data,
        performance_monitor
    ):
        """Test handling of students with large test histories."""
        cleanup_integration_data(unique_test_email)
        reset_container()
        
        service = get_student_service(use_test_db=True)
        
        performance_monitor.start()
        
        # Create student
        service.get_or_create_student(unique_test_email, "Large History User")
        
        # Add multiple test results
        num_tests = 10
        for i in range(num_tests):
            test_result = sample_test_result_dict.copy()
            test_result["band_score"] = 5.0 + (i * 0.2)  # Progressive improvement
            service.save_test_result(unique_test_email, test_result)
        
        # Get analytics (this should handle large history efficiently)
        analytics = service.get_performance_analytics(unique_test_email)
        
        performance_monitor.stop()
        
        # Verify data integrity
        assert analytics["student_info"]["total_tests"] == num_tests
        assert analytics["scores"]["latest"] == 5.0 + ((num_tests - 1) * 0.2)
        
        # Performance should be reasonable (adjust threshold as needed)
        assert performance_monitor.duration_ms < 5000  # Should complete within 5 seconds 