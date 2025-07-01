# Backend Tests

This directory contains comprehensive test suites for the AI IELTS Examiner backend.

## Test Structure

- `test_agent_tools.py` - Tests for agent tool functions (save_test_result_to_json, etc.)
- `conftest.py` - Shared pytest fixtures and configuration
- `__init__.py` - Makes tests directory a Python package

## Running Tests

### Activate Virtual Environment
```bash
source ../venv/bin/activate
```

### Run All Tests
```bash
# From backend directory
pytest

# Or with more verbose output
pytest -v

# Run specific test file
pytest tests/test_agent_tools.py

# Run specific test
pytest tests/test_agent_tools.py::TestSaveTestResultToJson::test_save_test_result_success_existing_student
```

### Coverage Report
```bash
# Install coverage if not already installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Test Categories

### Unit Tests
- **test_agent_tools.py**: Tests for the agent tool functions including:
  - `save_test_result_to_json()` - Test result persistence
  - Error handling and validation
  - Database interaction mocking
  - Complex data structure preservation

### Test Data
Tests use realistic IELTS test result data structures that match the production format:
- Complete IELTS speaking test responses (Parts 1, 2, 3)
- Detailed scoring and feedback
- Performance analytics data

## Dependencies

Required packages for testing:
- `pytest` - Test framework
- `pytest-mock` - Mocking utilities  
- `pytest-asyncio` - Async test support (add to requirements.txt if needed)

## Writing New Tests

1. Follow the naming convention: `test_*.py`
2. Use descriptive test method names: `test_function_name_scenario`
3. Include docstrings explaining what each test validates
4. Use fixtures from `conftest.py` for common setup
5. Mock external dependencies (database, API calls, etc.)

Example test structure:
```python
@pytest.mark.asyncio
async def test_my_function_success_case(mock_db, sample_data):
    """Test that my_function works correctly with valid input"""
    # Setup
    mock_db.some_method.return_value = expected_value
    
    # Execute
    result = await my_function(sample_data)
    
    # Verify
    assert result == expected_result
    mock_db.some_method.assert_called_once_with(sample_data)
``` 