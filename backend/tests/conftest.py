"""
Enhanced pytest configuration for the new clean architecture.

This module provides comprehensive test fixtures and configuration for testing
the refactored backend with dependency injection and clean architecture.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, MagicMock
from dotenv import load_dotenv
from typing import Optional, Generator

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def pytest_configure(config):
    """Register custom markers for the new architecture."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require real database)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (use mocks and dependency injection)"
    )
    config.addinivalue_line(
        "markers", "service: marks tests for service layer"
    )
    config.addinivalue_line(
        "markers", "repository: marks tests for repository layer"
    )
    config.addinivalue_line(
        "markers", "agent: marks tests for agent functionality"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and validate configuration."""
    from src.core.config import settings
    
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FORMAT"] = "text"
    
    # Set required test configs if not present
    if not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    
    test_db_available = bool(os.getenv("TEST_SUPABASE_CONNECTION_STRING"))
    
    if test_db_available:
        print(f"\n🗄️  Test database connection available - integration tests will run")
    else:
        print(f"\n⚠️  TEST_SUPABASE_CONNECTION_STRING not found - integration tests will be skipped")
        print("    Set TEST_SUPABASE_CONNECTION_STRING to run integration tests")
    
    return test_db_available


@pytest.fixture
def clean_container():
    """Reset the dependency injection container for clean test state."""
    from src.core.container import reset_container
    
    # Reset container before test
    reset_container()
    
    yield
    
    # Reset container after test
    reset_container()


@pytest.fixture
def mock_student_repository():
    """Create a mock student repository for unit tests."""
    mock_repo = Mock()
    
    # Configure common mock behaviors
    mock_repo.find_by_email.return_value = None
    mock_repo.save.return_value = None
    mock_repo.create_if_not_exists.return_value = None
    mock_repo.add_test_result.return_value = None
    
    return mock_repo


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository for unit tests."""
    mock_repo = Mock()
    
    # Configure common mock behaviors
    mock_repo.get_user_name.return_value = "Test User"
    mock_repo.find_by_email.return_value = None
    mock_repo.user_exists.return_value = True
    
    return mock_repo


@pytest.fixture
def mock_profile_repository():
    """Create a mock profile repository for unit tests."""
    mock_repo = Mock()
    
    # Configure common mock behaviors
    mock_repo.get_profile_by_email.return_value = None
    mock_repo.get_profile_for_instruction.return_value = None
    mock_repo.is_onboarding_completed.return_value = True
    
    return mock_repo


@pytest.fixture
def mock_student_service(mock_student_repository, mock_user_repository, mock_profile_repository):
    """Create a mock student service with injected dependencies."""
    from src.services.student_service import StudentService
    
    service = StudentService(
        student_repository=mock_student_repository,
        user_repository=mock_user_repository,
        profile_repository=mock_profile_repository
    )
    
    return service


@pytest.fixture
def sample_email():
    """Sample email for testing."""
    return "test@example.com"


@pytest.fixture
def sample_name():
    """Sample name for testing."""
    return "Test User"


@pytest.fixture
def sample_student_profile():
    """Sample student profile for testing."""
    from src.models.student import StudentProfile
    
    return StudentProfile(
        email="test@example.com",
        name="Test User",
        history=[]
    )


@pytest.fixture
def sample_test_result():
    """Sample test result based on the new architecture."""
    from src.models.student import TestResult, IELTSScores, TestFeedback
    from src.models.base import DifficultyLevel, TestStatus
    
    return TestResult(
        test_number=1,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        test_status=TestStatus.COMPLETED,
        detailed_scores=IELTSScores(
            fluency_coherence=6.5,
            lexical_resource=7.0,
            grammatical_accuracy=6.0,
            pronunciation=7.0
        ),
        band_score=6.5,
        answers={
            "part1": {
                "questions": ["Tell me about your hometown"],
                "responses": ["I'm from New York..."]
            },
            "part2": {
                "topic": "Describe a memorable trip",
                "response": "Last summer I went to Japan..."
            },
            "part3": {
                "questions": ["How has travel changed?"],
                "responses": ["Travel has become more accessible..."]
            }
        },
        feedback=TestFeedback(
            strengths=["Good vocabulary", "Clear pronunciation"],
            improvements=["Use more complex grammar", "Reduce hesitation"],
            detailed_feedback={
                "fluency_coherence": "Good flow but some hesitation",
                "lexical_resource": "Strong vocabulary range",
                "grammatical_accuracy": "Some complex structures needed",
                "pronunciation": "Clear and easy to understand"
            },
            examiner_notes="Overall good performance with room for improvement"
        )
    )


@pytest.fixture
def sample_test_result_dict():
    """Sample test result as dictionary for agent tools testing."""
    return {
        "answers": {
            "Part 1": {
                "questions": ["Tell me about your hometown"],
                "responses": ["I'm from New York..."]
            },
            "Part 2": {
                "topic": "Describe a memorable trip",
                "response": "Last summer I went to Japan..."
            },
            "Part 3": {
                "questions": ["How has travel changed?"],
                "responses": ["Travel has become more accessible..."]
            }
        },
        "detailed_scores": {
            "fluency_coherence": 6.5,
            "lexical_resource": 7.0,
            "grammatical_accuracy": 6.0,
            "pronunciation": 7.0
        },
        "band_score": 6.5,
        "feedback": {
            "strengths": ["Good vocabulary", "Clear pronunciation"],
            "improvements": ["Use more complex grammar", "Reduce hesitation"],
            "detailed_feedback": {
                "fluency_coherence": "Good flow but some hesitation",
                "lexical_resource": "Strong vocabulary range",
                "grammatical_accuracy": "Some complex structures needed",
                "pronunciation": "Clear and easy to understand"
            },
            "examiner_notes": "Overall good performance with room for improvement"
        },
        "test_status": "completed",
        "difficulty_level": "intermediate"
    }


@pytest.fixture
def sample_session_questions():
    """Sample session questions for agent testing."""
    return {
        "part1": "Tell me about your hometown.",
        "part2": "Describe a person who has influenced you. You should say: who this person is, how you know them, what they are like, and explain how they have influenced you.",
        "part3": "How do you think technology has changed the way people communicate?"
    }


@pytest.fixture
def test_container_with_mocks(
    clean_container,
    mock_student_repository,
    mock_user_repository,
    mock_profile_repository
):
    """Setup test container with mock dependencies."""
    from src.core.container import get_container
    
    container = get_container()
    
    # Override repositories with mocks
    container.override("student_repository", mock_student_repository)
    container.override("user_repository", mock_user_repository)
    container.override("profile_repository", mock_profile_repository)
    
    # Override test repositories with mocks too
    container.override("test_student_repository", mock_student_repository)
    container.override("test_user_repository", mock_user_repository)
    container.override("test_profile_repository", mock_profile_repository)
    
    yield container


@pytest.fixture
def integration_test_service():
    """Get a real service instance for integration tests."""
    test_db_available = bool(os.getenv("TEST_SUPABASE_CONNECTION_STRING"))
    
    if not test_db_available:
        pytest.skip("TEST_SUPABASE_CONNECTION_STRING not found - skipping integration test")
    
    from src.core.container import get_student_service
    
    # Use test database
    service = get_student_service(use_test_db=True)
    
    return service


@pytest.fixture
def unique_test_email():
    """Generate a unique test email for integration tests."""
    from datetime import datetime
    import uuid
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"test_user_{timestamp}_{unique_id}@test.example.com"


@pytest.fixture
def cleanup_integration_data():
    """Cleanup integration test data after tests."""
    emails_to_cleanup = []
    
    def register_email(email: str):
        """Register an email for cleanup."""
        emails_to_cleanup.append(email)
    
    yield register_email
    
    # Cleanup after test
    if emails_to_cleanup and os.getenv("TEST_SUPABASE_CONNECTION_STRING"):
        try:
            from src.repositories.student_repository import StudentRepository
            
            test_repo = StudentRepository(use_test_db=True)
            
            for email in emails_to_cleanup:
                try:
                    test_repo.delete_by_email(email)
                    print(f"Cleaned up test data for: {email}")
                except Exception as e:
                    print(f"Warning: Failed to cleanup {email}: {e}")
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Async test utilities
@pytest.fixture
def async_test():
    """Fixture to support async test functions."""
    def _async_test(coro):
        return asyncio.get_event_loop().run_until_complete(coro)
    
    return _async_test


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration_ms(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return None
    
    return PerformanceMonitor()


# Configuration for different test environments
@pytest.fixture(params=["unit", "integration"])
def test_mode(request):
    """Parametrized fixture to run tests in different modes."""
    return request.param 