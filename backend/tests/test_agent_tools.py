import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.tools.agent_tools import save_test_result_to_json, set_database
from src.models.student_models import StudentPerformance


class TestSaveTestResultToJson:
    """Test suite for save_test_result_to_json function"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database instance"""
        mock_db = Mock()
        set_database(mock_db)
        return mock_db
    
    @pytest.fixture
    def sample_test_result(self):
        """Sample test result data based on the provided example"""
        return {
            "answers": {
                "Part 1": {
                    "questions": ["Tell me about your hometown", "Do you work or study?"],
                    "responses": ["I'm from New York...", "I work as a software developer..."]
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
            "feedback": {
                "fluency": "Good flow but some hesitation",
                "grammar": "Some complex structures needed", 
                "vocabulary": "Strong vocabulary range",
                "pronunciation": "Clear and easy to understand"
            },
            "strengths": ["Good vocabulary", "Clear pronunciation"],
            "band_score": 6.5,
            "improvements": ["Use more complex grammar", "Reduce hesitation"],
            "detailed_scores": {
                "fluency": 6,
                "grammar": 6,
                "vocabulary": 7,
                "pronunciation": 7
            }
        }
    
    @pytest.fixture
    def existing_student_data(self):
        """Sample existing student data as returned by the database"""
        return {
            "history": [
                {
                    "band_score": 6.0,
                    "test_date": "2024-01-01T10:00:00",
                    "test_number": 1
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_save_test_result_success_existing_student(self, mock_db, sample_test_result, existing_student_data):
        """Test successful save for existing student"""
        # Setup
        email = "test@example.com"
        mock_db.get_student.return_value = existing_student_data
        mock_db.upsert_student.return_value = None
        
        # Execute
        result = await save_test_result_to_json(email, sample_test_result)
        
        # Verify
        assert "SUCCESS" in result
        assert "Test #2" in result  # Should be second test
        assert "band score: 6.5" in result
        assert "Total tests taken: 2" in result
        
        # Verify database calls
        mock_db.get_student.assert_called_once_with(email)
        mock_db.upsert_student.assert_called_once()
        
        # Verify that test_date and test_number were added
        call_args = mock_db.upsert_student.call_args[0][0]
        assert len(call_args.history) == 2
        assert "test_date" in call_args.history[-1]
        assert call_args.history[-1]["test_number"] == 2
    
    @pytest.mark.asyncio
    async def test_save_test_result_success_new_student(self, mock_db, sample_test_result):
        """Test successful save for new student (creates student record)"""
        # Setup
        email = "newuser@example.com"
        call_count = 0
        
        def get_student_side_effect(email_param):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return None  # First call: student doesn't exist
            else:
                return {"history": []}  # Second call: student exists with empty history
        
        mock_db.get_student.side_effect = get_student_side_effect
        mock_db.upsert_student.return_value = None
        
        # Execute  
        result = await save_test_result_to_json(email, sample_test_result)
        
        # Verify
        assert "SUCCESS" in result
        assert "Test #1" in result  # Should be first test
        assert "band score: 6.5" in result
        
        # Verify database calls - should create student then save result
        assert mock_db.upsert_student.call_count == 2  # Once to create, once to save
    
    @pytest.mark.asyncio
    async def test_save_test_result_missing_email(self, mock_db, sample_test_result):
        """Test error handling when email is missing"""
        result = await save_test_result_to_json("", sample_test_result)
        
        assert "ERROR: Email parameter is required." in result
        mock_db.get_student.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_test_result_missing_test_result(self, mock_db):
        """Test error handling when test_result is missing"""
        email = "test@example.com"
        
        result = await save_test_result_to_json(email, None)
        
        assert "ERROR: Test result data is required." in result
        mock_db.get_student.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_test_result_missing_required_fields(self, mock_db, existing_student_data):
        """Test error handling when test_result is missing required fields"""
        # Setup
        email = "test@example.com" 
        incomplete_test_result = {
            "answers": {"Part 1": {"questions": [], "responses": []}},
            # Missing 'band_score' and 'feedback'
        }
        
        mock_db.get_student.return_value = existing_student_data
        
        # Execute
        result = await save_test_result_to_json(email, incomplete_test_result)
        
        # Verify
        assert "ERROR: Test result missing required fields:" in result
        assert "band_score" in result
        assert "feedback" in result
        mock_db.upsert_student.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_test_result_with_timestamp_and_test_number(self, mock_db, sample_test_result, existing_student_data):
        """Test that timestamp and test_number are properly added"""
        # Setup
        email = "test@example.com"
        mock_db.get_student.return_value = existing_student_data
        mock_db.upsert_student.return_value = None
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-12-25T10:30:00"
            
            # Execute
            result = await save_test_result_to_json(email, sample_test_result)
            
            # Verify timestamp was added
            call_args = mock_db.upsert_student.call_args[0][0]
            saved_test = call_args.history[-1]
            assert saved_test["test_date"] == "2024-12-25T10:30:00"
            assert saved_test["test_number"] == 2  # Second test for existing student
    
    @pytest.mark.asyncio 
    async def test_save_test_result_preserves_original_data(self, mock_db, sample_test_result, existing_student_data):
        """Test that all original test result data is preserved"""
        # Setup
        email = "test@example.com"
        mock_db.get_student.return_value = existing_student_data
        mock_db.upsert_student.return_value = None
        
        # Execute
        await save_test_result_to_json(email, sample_test_result)
        
        # Verify all original data is preserved
        call_args = mock_db.upsert_student.call_args[0][0]
        saved_test = call_args.history[-1]
        
        assert saved_test["band_score"] == 6.5
        assert saved_test["answers"] == sample_test_result["answers"]
        assert saved_test["feedback"] == sample_test_result["feedback"]
        assert saved_test["strengths"] == sample_test_result["strengths"]
        assert saved_test["improvements"] == sample_test_result["improvements"]
        assert saved_test["detailed_scores"] == sample_test_result["detailed_scores"]
    
    @pytest.mark.asyncio
    async def test_save_test_result_complex_sample_data(self, mock_db):
        """Test with the complex sample data provided by the user"""
        # Setup with the exact sample data structure provided
        complex_test_result = {
            "answers": {
                "Part 1": {
                    "questions": [
                        "Can you tell me a little bit about your hometown?",
                        "Do you work or are you a student?",
                        "As a software developer, what do you find most interesting about your job?",
                        "What are your main responsibilities in your current role as a software developer?"
                    ],
                    "responses": [
                        "I'm from Aluva, in Thrissur.",
                        "I'm working as a software developer.",
                        "The thing I find most interesting about my job is the fact that I can create anything from very basic from scratch.",
                        "My main responsibilities include creating new features or new additions for my module and bug fixes."
                    ]
                },
                "Part 2": {
                    "topic": "Describe a skill that you learned that helped you in your studies.",
                    "response": "One of the tricks I actually learned during my study time is the Pomodoro Technique. It helped me focus more and do my time management effectively..."
                },
                "Part 3": {
                    "questions": [
                        "What are some new skills that people are learning these days?",
                        "Why do you think learning how to use AI is so important now?"
                    ],
                    "responses": [
                        "I think working with AI is a skill that people are learning these days...",
                        "Because AI has a lot of capabilities, ranging from like reading, writing to like doing important tasks..."
                    ]
                }
            },
            "feedback": {
                "fluency": "You maintained good flow throughout the test, especially in Part 1 and 3.",
                "grammar": "You used a mix of simple and complex sentence structures.",
                "vocabulary": "Your vocabulary range is strong and appropriate for various topics.",
                "pronunciation": "Your pronunciation is clear and easy to understand."
            },
            "strengths": [
                "Clear and generally well-paced speech.",
                "Good range of vocabulary.",
                "Effective use of cohesive devices to link ideas.",
                "Pronunciation is very clear."
            ],
            "band_score": 6.5,
            "improvements": [
                "Grammatical Accuracy: Focus on improving accuracy with complex grammatical structures.",
                "Fluency with Complexity: While your general fluency is good, work on reducing hesitation..."
            ],
            "detailed_scores": {
                "fluency": 6.5,
                "grammar": 6,
                "vocabulary": 7,
                "pronunciation": 7
            }
        }
        
        email = "complex@example.com"
        existing_data = {"history": []}
        
        mock_db.get_student.return_value = existing_data
        mock_db.upsert_student.return_value = None
        
        # Execute
        result = await save_test_result_to_json(email, complex_test_result)
        
        # Verify
        assert "SUCCESS" in result
        assert "band score: 6.5" in result
        
        # Verify complex data structure is preserved
        call_args = mock_db.upsert_student.call_args[0][0]
        saved_test = call_args.history[-1]
        
        assert len(saved_test["answers"]["Part 1"]["questions"]) == 4
        assert len(saved_test["answers"]["Part 1"]["responses"]) == 4
        assert saved_test["detailed_scores"]["fluency"] == 6.5
        assert len(saved_test["strengths"]) == 4
        assert len(saved_test["improvements"]) == 2


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"]) 