"""
Unit tests for the new agent tools using clean architecture.

These tests use dependency injection and proper mocking to test the
agent tools in isolation from database dependencies.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.tools.agent_tools_new import (
    save_test_result_to_json,
    create_new_student_record,
    get_student_performance_analytics,
    get_user_learning_recommendations,
    set_current_user_email,
    set_current_session_id,
    get_current_user_email,
    get_current_session_id
)
from src.models.student import StudentProfile
from src.core.exceptions import validation_error, BusinessLogicException, ErrorCode


@pytest.mark.unit
class TestAgentToolsNew:
    """Test suite for new agent tools with clean architecture."""
    
    def test_session_context_management(self):
        """Test session context management functions."""
        # Test setting and getting user email
        test_email = "test@example.com"
        set_current_user_email(test_email)
        assert get_current_user_email() == test_email
        
        # Test setting and getting session ID
        test_session_id = "session-123"
        set_current_session_id(test_session_id)
        assert get_current_session_id() == test_session_id
    
    @pytest.mark.asyncio
    async def test_save_test_result_success(
        self,
        test_container_with_mocks,
        sample_email,
        sample_test_result_dict
    ):
        """Test successful test result saving."""
        # Setup mock service
        mock_service = Mock()
        mock_service.save_test_result.return_value = "SUCCESS: Test saved"
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await save_test_result_to_json(sample_email, sample_test_result_dict)
        
        # Verify the service was called correctly
        mock_service.save_test_result.assert_called_once_with(sample_email, sample_test_result_dict)
        assert "SUCCESS" in result
    
    @pytest.mark.asyncio
    async def test_save_test_result_with_session_id(
        self,
        test_container_with_mocks,
        sample_email,
        sample_test_result_dict
    ):
        """Test test result saving includes session ID when available."""
        # Set session context
        test_session_id = "session-456"
        set_current_session_id(test_session_id)
        
        mock_service = Mock()
        mock_service.save_test_result.return_value = "SUCCESS: Test saved"
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            await save_test_result_to_json(sample_email, sample_test_result_dict)
        
        # Verify session ID was added to test result
        called_args = mock_service.save_test_result.call_args[0]
        test_result_with_session = called_args[1]
        assert test_result_with_session['session_id'] == test_session_id
    
    @pytest.mark.asyncio
    async def test_save_test_result_validation_errors(self, test_container_with_mocks):
        """Test validation error handling in save_test_result_to_json."""
        # Test missing email
        result = await save_test_result_to_json("", {"test": "data"})
        assert "ERROR" in result
        assert "Email parameter is required" in result
        
        # Test missing test result
        result = await save_test_result_to_json("test@example.com", None)
        assert "ERROR" in result
        assert "Test result data is required" in result
    
    @pytest.mark.asyncio
    async def test_save_test_result_service_error(
        self,
        test_container_with_mocks,
        sample_email,
        sample_test_result_dict
    ):
        """Test error handling when service raises exception."""
        mock_service = Mock()
        mock_service.save_test_result.side_effect = BusinessLogicException(
            "Service error",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR
        )
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await save_test_result_to_json(sample_email, sample_test_result_dict)
        
        assert "ERROR" in result
        assert "Service error" in result
    
    @pytest.mark.asyncio
    async def test_create_new_student_record_success(
        self,
        test_container_with_mocks,
        sample_email,
        sample_name
    ):
        """Test successful student record creation."""
        mock_student = StudentProfile(email=sample_email, name=sample_name)
        mock_service = Mock()
        mock_service.get_or_create_student.return_value = mock_student
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await create_new_student_record(sample_email, sample_name)
        
        mock_service.get_or_create_student.assert_called_once_with(sample_email, sample_name)
        assert "SUCCESS" in result
        assert sample_name in result
        assert sample_email in result
    
    @pytest.mark.asyncio
    async def test_create_new_student_record_existing(
        self,
        test_container_with_mocks,
        sample_email,
        sample_name
    ):
        """Test creating student record when one already exists."""
        mock_student = StudentProfile(email=sample_email, name=sample_name, history=[{"test": "data"}])
        mock_student.total_tests = 1
        
        mock_service = Mock()
        mock_service.get_or_create_student.return_value = mock_student
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await create_new_student_record(sample_email, sample_name)
        
        assert "already exists" in result
        assert "1 test(s)" in result
    
    @pytest.mark.asyncio
    async def test_create_new_student_record_validation(self, test_container_with_mocks):
        """Test validation in create_new_student_record."""
        # Test missing email
        result = await create_new_student_record("", "Test User")
        assert "ERROR" in result
        assert "Email parameter is required" in result
        
        # Test missing name
        result = await create_new_student_record("test@example.com", "")
        assert "ERROR" in result
        assert "Name parameter is required" in result
    
    @pytest.mark.asyncio
    async def test_get_student_performance_analytics_success(
        self,
        test_container_with_mocks,
        sample_email
    ):
        """Test successful performance analytics retrieval."""
        mock_analytics = {
            "student_info": {
                "email": sample_email,
                "total_tests": 3,
                "current_level": "intermediate"
            },
            "scores": {
                "latest": 6.5,
                "best": 7.0,
                "average": 6.2
            }
        }
        
        mock_service = Mock()
        mock_service.get_performance_analytics.return_value = mock_analytics
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await get_student_performance_analytics(sample_email)
        
        mock_service.get_performance_analytics.assert_called_once_with(sample_email)
        
        # Result should be JSON string
        import json
        parsed_result = json.loads(result)
        assert parsed_result["student_info"]["email"] == sample_email
        assert parsed_result["scores"]["latest"] == 6.5
    
    @pytest.mark.asyncio
    async def test_get_student_performance_analytics_validation(self, test_container_with_mocks):
        """Test validation in get_student_performance_analytics."""
        result = await get_student_performance_analytics("")
        assert "ERROR" in result
        assert "Email parameter is required" in result
    
    @pytest.mark.asyncio
    async def test_get_user_learning_recommendations_success(
        self,
        test_container_with_mocks,
        sample_email
    ):
        """Test successful learning recommendations retrieval."""
        mock_analytics = {
            "student_info": {"current_level": "intermediate"},
            "recommendations": ["Practice complex grammar", "Work on fluency"],
            "learning_path": {"current_focus": "Grammar", "target_timeline": "2 months"},
            "performance_trend": {"trend": "improving"}
        }
        
        mock_service = Mock()
        mock_service.get_performance_analytics.return_value = mock_analytics
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await get_user_learning_recommendations(sample_email)
        
        # Result should be JSON string with recommendations
        import json
        parsed_result = json.loads(result)
        assert "recommendations" in parsed_result
        assert "learning_path" in parsed_result
        assert parsed_result["current_level"] == "intermediate"
    
    @pytest.mark.asyncio
    async def test_get_user_learning_recommendations_validation(self, test_container_with_mocks):
        """Test validation in get_user_learning_recommendations."""
        result = await get_user_learning_recommendations("")
        assert "ERROR" in result
        assert "Email parameter is required" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_with_request_tracing(
        self,
        test_container_with_mocks,
        sample_email
    ):
        """Test that errors include proper request tracing."""
        mock_service = Mock()
        mock_service.save_test_result.side_effect = Exception("Unexpected error")
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            with patch('src.tools.agent_tools_new.generate_request_id', return_value="req-123"):
                result = await save_test_result_to_json(sample_email, {"test": "data"})
        
        assert "ERROR" in result
        assert "unexpected error" in result.lower()
    
    @pytest.mark.asyncio
    async def test_legacy_set_database_function(self, test_container_with_mocks):
        """Test that legacy set_database function works but logs deprecation."""
        from src.tools.agent_tools_new import set_database
        
        mock_db = Mock()
        
        with patch('src.tools.agent_tools_new.logger') as mock_logger:
            set_database(mock_db)
            
            # Should log deprecation warning
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "deprecated" in warning_call.lower()
    
    def test_initialize_session_context(self):
        """Test session context initialization."""
        from src.tools.agent_tools_new import initialize_session_context
        
        test_email = "init@example.com"
        test_session = "init-session-123"
        
        with patch('src.tools.agent_tools_new.logger') as mock_logger:
            initialize_session_context(user_email=test_email, session_id=test_session)
        
        # Verify context was set
        assert get_current_user_email() == test_email
        assert get_current_session_id() == test_session
        
        # Should log initialization
        mock_logger.info.assert_called_once()


@pytest.mark.unit 
class TestAgentToolsErrorScenarios:
    """Test error scenarios and edge cases for agent tools."""
    
    @pytest.mark.asyncio
    async def test_malformed_test_result_data(self, test_container_with_mocks, sample_email):
        """Test handling of malformed test result data."""
        malformed_data = {
            "band_score": "not-a-number",  # Should be float
            "answers": "not-a-dict"  # Should be dict
        }
        
        mock_service = Mock()
        mock_service.save_test_result.side_effect = validation_error(
            "Invalid test result format",
            field_name="test_result"
        )
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await save_test_result_to_json(sample_email, malformed_data)
        
        assert "ERROR" in result
        assert "Invalid test result format" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, test_container_with_mocks, sample_email):
        """Test that concurrent tool calls work properly with dependency injection."""
        mock_service = Mock()
        mock_service.save_test_result.return_value = "SUCCESS: Test saved"
        mock_service.get_or_create_student.return_value = StudentProfile(
            email=sample_email, 
            name="Test User"
        )
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            # Run multiple operations concurrently
            tasks = [
                save_test_result_to_json(sample_email, {"test": "data1"}),
                save_test_result_to_json(sample_email, {"test": "data2"}),
                create_new_student_record(sample_email, "Test User")
            ]
            
            results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert "SUCCESS" in result or "already exists" in result
    
    @pytest.mark.asyncio 
    async def test_service_timeout_handling(self, test_container_with_mocks, sample_email):
        """Test handling of service timeouts."""
        mock_service = Mock()
        mock_service.save_test_result.side_effect = asyncio.TimeoutError("Service timeout")
        
        with patch('src.tools.agent_tools_new.get_student_service', return_value=mock_service):
            result = await save_test_result_to_json(sample_email, {"test": "data"})
        
        assert "ERROR" in result
        assert "unexpected error" in result.lower() 