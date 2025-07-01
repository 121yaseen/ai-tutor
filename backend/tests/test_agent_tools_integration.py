import pytest
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from src.tools.agent_tools import save_test_result_to_json, set_database
from src.database.student_db import StudentDB
from src.models.student_models import StudentPerformance

# Load environment variables
load_dotenv()

class TestSaveTestResultToJsonIntegration:
    """Integration tests for save_test_result_to_json function using real Supabase test database"""
    
    @pytest.fixture(scope="class")
    def test_db(self):
        """Create a real database connection for integration tests"""
        # Check if test database connection string is available
        test_connection_string = os.getenv("TEST_SUPABASE_CONNECTION_STRING")
        if not test_connection_string:
            pytest.skip("TEST_SUPABASE_CONNECTION_STRING not found in environment - skipping integration tests")
        
        # Temporarily override the connection string for testing
        original_connection = os.environ.get("SUPABASE_CONNECTION_STRING")
        os.environ["SUPABASE_CONNECTION_STRING"] = test_connection_string
        
        try:
            db = StudentDB()
            set_database(db)
            yield db
        finally:
            # Restore original connection string
            if original_connection:
                os.environ["SUPABASE_CONNECTION_STRING"] = original_connection
            elif "SUPABASE_CONNECTION_STRING" in os.environ:
                del os.environ["SUPABASE_CONNECTION_STRING"]
    
    @pytest.fixture
    def test_email(self):
        """Generate a unique test email for each test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"test_user_{timestamp}@test.example.com"
    
    @pytest.fixture
    def cleanup_test_data(self, test_db):
        """Clean up test data after each test"""
        emails_to_cleanup = []
        
        def register_cleanup(email):
            emails_to_cleanup.append(email)
        
        yield register_cleanup
        
        # Cleanup after test
        for email in emails_to_cleanup:
            try:
                # Delete test data - you might want to implement a cleanup method
                # For now, we'll let the test data remain as it's a test database
                print(f"[CLEANUP] Test data for {email} left in test database")
            except Exception as e:
                print(f"[CLEANUP ERROR] Failed to cleanup {email}: {e}")
    
    @pytest.fixture
    def sample_test_result(self):
        """Sample test result data for integration testing"""
        return {
            "answers": {
                "Part 1": {
                    "questions": ["Tell me about your hometown", "Do you work or study?"],
                    "responses": ["I'm from New York, a vibrant city with great opportunities.", "I work as a software developer at a tech company."]
                },
                "Part 2": {
                    "topic": "Describe a memorable trip you have taken",
                    "response": "Last summer I went to Japan and it was an incredible experience. The culture was fascinating and the food was amazing. I visited Tokyo and Kyoto, experiencing both modern and traditional aspects of Japanese life."
                },
                "Part 3": {
                    "questions": ["How has travel changed with technology?"],
                    "responses": ["Travel has become much more accessible with technology. We can book flights and hotels online, use GPS for navigation, and translate languages instantly."]
                }
            },
            "feedback": {
                "fluency": "Good flow with natural pauses and clear progression of ideas.",
                "grammar": "Generally accurate with some complex structures. Minor errors in advanced constructions.", 
                "vocabulary": "Strong vocabulary range with appropriate word choice and some less common expressions.",
                "pronunciation": "Clear and easy to understand with good intonation patterns."
            },
            "strengths": ["Excellent vocabulary range", "Clear pronunciation", "Natural conversation flow"],
            "band_score": 7.0,
            "improvements": ["Use more complex grammatical structures", "Expand on ideas with more detail"],
            "detailed_scores": {
                "fluency": 7,
                "grammar": 6,
                "vocabulary": 8,
                "pronunciation": 7
            }
        }
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_save_new_student_to_real_database(self, test_db, test_email, cleanup_test_data, sample_test_result):
        """Test saving a test result for a new student to real database"""
        cleanup_test_data(test_email)
        
        # Verify student doesn't exist initially
        initial_data = test_db.get_student(test_email)
        assert initial_data is None, "Student should not exist initially"
        
        # Save test result
        result = await save_test_result_to_json(test_email, sample_test_result)
        
        # Verify success message
        assert "SUCCESS" in result
        assert "Test #1" in result
        assert "band score: 7.0" in result
        
        # Verify data was actually saved to database
        saved_data = test_db.get_student(test_email)
        assert saved_data is not None, "Student data should be saved"
        assert len(saved_data["history"]) == 1, "Should have one test result"
        
        saved_test = saved_data["history"][0]
        assert saved_test["band_score"] == 7.0
        assert saved_test["test_number"] == 1
        assert "test_date" in saved_test
        assert saved_test["answers"] == sample_test_result["answers"]
        assert saved_test["feedback"] == sample_test_result["feedback"]
        
        print(f"✅ Successfully saved test result to database for {test_email}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration 
    async def test_save_multiple_tests_for_existing_student(self, test_db, test_email, cleanup_test_data, sample_test_result):
        """Test saving multiple test results for the same student"""
        cleanup_test_data(test_email)
        
        # Save first test result
        result1 = await save_test_result_to_json(test_email, sample_test_result)
        assert "SUCCESS" in result1
        assert "Test #1" in result1
        
        # Modify sample data for second test
        second_test_result = sample_test_result.copy()
        second_test_result["band_score"] = 7.5
        second_test_result["detailed_scores"]["fluency"] = 8
        
        # Save second test result
        result2 = await save_test_result_to_json(test_email, second_test_result)
        assert "SUCCESS" in result2
        assert "Test #2" in result2
        assert "band score: 7.5" in result2
        assert "Total tests taken: 2" in result2
        
        # Verify both tests are saved
        saved_data = test_db.get_student(test_email)
        assert len(saved_data["history"]) == 2, "Should have two test results"
        
        # Verify test numbering
        assert saved_data["history"][0]["test_number"] == 1
        assert saved_data["history"][1]["test_number"] == 2
        
        # Verify different scores
        assert saved_data["history"][0]["band_score"] == 7.0
        assert saved_data["history"][1]["band_score"] == 7.5
        
        print(f"✅ Successfully saved multiple test results for {test_email}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_save_complex_real_world_data(self, test_db, test_email, cleanup_test_data):
        """Test saving complex real-world IELTS test data to database"""
        cleanup_test_data(test_email)
        
        # Use the complex sample data from the user's example
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
                    "response": "One of the tricks I actually learned during my study time is the Pomodoro Technique. It helped me focus more and do my time management effectively, helping me get things done. I learned it from an online blog written by a student. Earlier, I used to struggle a lot because when I think of studies, I think it as a single chunk, and it used to stress me out. So, when I actually structured it in 25-minute chunks, and I thought of executing just 25 minutes at a time, it has really helped me."
                },
                "Part 3": {
                    "questions": [
                        "What are some new skills that people are learning these days?",
                        "Why do you think learning how to use AI is so important now?",
                        "Do you think it's important for everyone to learn about AI, or just people in certain professions?"
                    ],
                    "responses": [
                        "I think working with AI is a skill that people are learning these days, like how to make use of the AI advancements that are happening.",
                        "Because AI has a lot of capabilities, ranging from like reading, writing to like doing important tasks or like complex tasks independently. So, and it's better than most human beings as well currently, so it's like a very good skill to have at this point.",
                        "I think everyone should learn about AI because AI covers not only professionals but like people from everyday life. For example, if I want to cook anything, then I can just ask the AI to give me the instructions."
                    ]
                }
            },
            "feedback": {
                "fluency": "You maintained good flow throughout the test, especially in Part 1 and 3. There were still some instances of hesitation, particularly when structuring more complex ideas.",
                "grammar": "You used a mix of simple and complex sentence structures. While there were clear attempts to use more complex grammar, some errors occurred in these instances.",
                "vocabulary": "Your vocabulary range is strong and appropriate for various topics. You used some less common vocabulary naturally.",
                "pronunciation": "Your pronunciation is clear and easy to understand. Word and sentence stress were generally accurate."
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
                "Fluency with Complexity: While your general fluency is good, work on reducing hesitation when forming more elaborate or abstract thoughts."
            ],
            "detailed_scores": {
                "fluency": 6.5,
                "grammar": 6,
                "vocabulary": 7,
                "pronunciation": 7
            }
        }
        
        # Save to database
        result = await save_test_result_to_json(test_email, complex_test_result)
        
        # Verify success
        assert "SUCCESS" in result
        assert "band score: 6.5" in result
        
        # Verify data persistence in database
        saved_data = test_db.get_student(test_email)
        assert saved_data is not None
        
        saved_test = saved_data["history"][0]
        
        # Verify complex data structure is preserved
        assert len(saved_test["answers"]["Part 1"]["questions"]) == 4
        assert len(saved_test["answers"]["Part 1"]["responses"]) == 4
        assert saved_test["detailed_scores"]["fluency"] == 6.5
        assert len(saved_test["strengths"]) == 4
        assert len(saved_test["improvements"]) == 2
        assert saved_test["band_score"] == 6.5
        
        # Verify metadata was added
        assert "test_date" in saved_test
        assert saved_test["test_number"] == 1
        
        print(f"✅ Successfully saved complex real-world test data for {test_email}")
        print(f"📊 Data verification: {len(saved_test['answers']['Part 1']['questions'])} Part 1 questions saved")
        print(f"📊 Band score: {saved_test['band_score']}, Test #{saved_test['test_number']}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_connection_and_permissions(self, test_db):
        """Test that we can actually connect to the test database and have proper permissions"""
        try:
            # Try a simple database operation
            test_email = "connection_test@example.com"
            
            # This should work if we have proper connection and permissions
            result = test_db.get_student(test_email)
            
            # Should return None for non-existent user without throwing an error
            assert result is None or isinstance(result, dict)
            
            print("✅ Database connection and permissions verified")
            
        except Exception as e:
            pytest.fail(f"Database connection failed: {str(e)}")


@pytest.mark.integration
class TestDatabaseErrorHandling:
    """Test error handling with real database scenarios"""
    
    @pytest.fixture(scope="class") 
    def test_db(self):
        """Create database connection for error testing"""
        test_connection_string = os.getenv("TEST_SUPABASE_CONNECTION_STRING")
        if not test_connection_string:
            pytest.skip("TEST_SUPABASE_CONNECTION_STRING not found - skipping integration tests")
        
        original_connection = os.environ.get("SUPABASE_CONNECTION_STRING") 
        os.environ["SUPABASE_CONNECTION_STRING"] = test_connection_string
        
        try:
            db = StudentDB()
            set_database(db)
            yield db
        finally:
            if original_connection:
                os.environ["SUPABASE_CONNECTION_STRING"] = original_connection
            elif "SUPABASE_CONNECTION_STRING" in os.environ:
                del os.environ["SUPABASE_CONNECTION_STRING"]
    
    @pytest.mark.asyncio
    async def test_invalid_data_handling_with_real_db(self, test_db):
        """Test how the function handles invalid data with real database"""
        
        # Test with missing required fields
        invalid_test_result = {
            "answers": {"Part 1": {"questions": [], "responses": []}},
            # Missing band_score and feedback
        }
        
        result = await save_test_result_to_json("test@example.com", invalid_test_result)
        
        # Should return error message
        assert "ERROR: Test result missing required fields:" in result
        assert "band_score" in result
        assert "feedback" in result
        
        print("✅ Invalid data properly rejected by database integration")


if __name__ == "__main__":
    # Run integration tests only
    pytest.main([__file__, "-v", "-m", "integration"]) 