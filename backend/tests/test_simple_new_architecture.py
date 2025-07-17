"""
Simple test to demonstrate the new clean architecture is working.

This test verifies that the new models, services, and core components
can be imported and instantiated correctly.
"""

import pytest
from unittest.mock import Mock

def test_imports():
    """Test that all new architecture components can be imported."""
    # Test core components
    from src.core.exceptions import BusinessLogicException, ValidationException
    from src.models.base import BaseEntityModel, DifficultyLevel, TestStatus
    from src.models.student import StudentProfile, TestResult, IELTSScores
    
    # Test that enums work
    assert DifficultyLevel.BASIC == "basic"
    assert TestStatus.COMPLETED == "completed"
    
    print("✅ All imports successful!")

def test_model_creation():
    """Test that new models can be created and validated."""
    from src.models.student import StudentProfile, IELTSScores
    
    # Test basic model creation
    student = StudentProfile(
        email="test@example.com",
        name="Test User",
        history=[]
    )
    
    assert student.email == "test@example.com"
    assert student.name == "Test User"
    assert student.total_tests == 0
    
    # Test IELTS scores
    scores = IELTSScores(
        fluency_coherence=6.5,
        lexical_resource=7.0,
        grammatical_accuracy=6.0,
        pronunciation=7.0
    )
    
    assert scores.overall_score == 6.625  # Average calculation
    
    print("✅ Model creation successful!")

def test_service_with_mocks():
    """Test that service can be created with mock dependencies."""
    from src.services.student_service import StudentService
    
    # Create mock dependencies
    mock_student_repo = Mock()
    mock_user_repo = Mock()
    mock_profile_repo = Mock()
    
    # Create service
    service = StudentService(
        student_repository=mock_student_repo,
        user_repository=mock_user_repo,
        profile_repository=mock_profile_repo
    )
    
    assert service is not None
    assert service.student_repository == mock_student_repo
    
    print("✅ Service creation with dependency injection successful!")

def test_exceptions():
    """Test that custom exceptions work correctly."""
    from src.core.exceptions import BusinessLogicException, validation_error
    
    # Test business logic exception
    try:
        raise BusinessLogicException("Test error", error_code="TEST_ERROR")
    except BusinessLogicException as e:
        assert str(e) == "Test error"
        assert e.error_code == "TEST_ERROR"
    
    # Test validation error helper
    validation_exc = validation_error("Invalid email", field_name="email")
    assert "Invalid email" in str(validation_exc)
    
    print("✅ Exception handling working correctly!")

if __name__ == "__main__":
    test_imports()
    test_model_creation()
    test_service_with_mocks()
    test_exceptions()
    print("\n🎉 All architecture tests passed! The new clean architecture is ready.") 