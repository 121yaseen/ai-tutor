"""
Pytest configuration and shared fixtures for backend tests.
"""

import pytest
import os
import sys
from unittest.mock import Mock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require real database)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (use mocks)"
    )

@pytest.fixture
def mock_student_db():
    """Create a mock StudentDB instance for unit tests."""
    mock_db = Mock()
    mock_db.get_student.return_value = None
    mock_db.upsert_student.return_value = None
    mock_db.create_student_if_not_exists.return_value = None
    return mock_db

@pytest.fixture
def sample_email():
    """Sample email for testing."""
    return "test@example.com"

@pytest.fixture
def sample_student_data():
    """Sample student data structure."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "history": []
    }

@pytest.fixture(scope="session", autouse=True)
def check_test_environment():
    """Check if we're in a test environment and log database info"""
    test_db_available = bool(os.getenv("TEST_SUPABASE_CONNECTION_STRING"))
    
    if test_db_available:
        print(f"\n🗄️  Test database connection available - integration tests will run")
    else:
        print(f"\n⚠️  TEST_SUPABASE_CONNECTION_STRING not found - integration tests will be skipped")
    
    return test_db_available 