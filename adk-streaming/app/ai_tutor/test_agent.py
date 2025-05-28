#!/usr/bin/env python3
"""
Simple test script for AI Tutor IELTS Screener Agent
Run this to verify the agent is properly configured and functional.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the agent
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from ai_tutor import root_agent
    print("✅ Successfully imported AI Tutor agent")
except ImportError as e:
    print(f"❌ Failed to import AI Tutor agent: {e}")
    sys.exit(1)

async def test_agent_basic():
    """Test basic agent functionality"""
    print("\n🧪 Testing AI Tutor Agent...")
    
    # Test 1: Agent object creation
    try:
        assert root_agent is not None
        assert root_agent.name == "ai_tutor_ielts_screener"
        print("✅ Agent object created successfully")
    except Exception as e:
        print(f"❌ Agent object test failed: {e}")
        return False
    
    # Test 2: Tools are properly loaded
    try:
        tools = root_agent.tools
        expected_tool_count = 9  # We expect 9 tools
        
        print(f"🔍 Found {len(tools)} tools")
        
        if len(tools) != expected_tool_count:
            print(f"❌ Expected {expected_tool_count} tools, found {len(tools)}")
            return False
        
        # Check that tools are either functions or FunctionTool objects
        from google.adk.tools.function_tool import FunctionTool
        for i, tool in enumerate(tools):
            if not (callable(tool) or isinstance(tool, FunctionTool)):
                print(f"❌ Tool {i} is neither a function nor FunctionTool: {type(tool)}")
                return False
        
        print(f"✅ All {expected_tool_count} tools loaded successfully")
    except Exception as e:
        print(f"❌ Tools test failed: {str(e)}")
        return False
    
    # Test 3: Agent has proper instruction
    try:
        assert root_agent.instruction is not None
        assert "IELTS" in root_agent.instruction
        assert "speaking" in root_agent.instruction.lower()
        print("✅ Agent instruction is properly configured")
    except Exception as e:
        print(f"❌ Instruction test failed: {e}")
        return False
    
    return True

async def test_tools_import():
    """Test that all tools can be imported and have proper docstrings"""
    print("\n🔧 Testing tool imports...")
    
    try:
        from ai_tutor.tools.student_management import (
            save_student_info, get_student_info, save_assessment_results, load_student_history
        )
        from ai_tutor.tools.ielts_assessment import (
            conduct_speaking_assessment, calculate_band_score, generate_improvement_suggestions,
            get_task_card, get_discussion_questions
        )
        
        # Check that all tools have proper docstrings
        tools_to_check = [
            save_student_info, get_student_info, save_assessment_results, load_student_history,
            conduct_speaking_assessment, calculate_band_score, generate_improvement_suggestions,
            get_task_card, get_discussion_questions
        ]
        
        for tool in tools_to_check:
            if not tool.__doc__ or len(tool.__doc__.strip()) < 20:
                print(f"⚠️  Tool {tool.__name__} has insufficient documentation")
            else:
                print(f"✅ Tool {tool.__name__} properly documented")
        
        print("✅ All tools imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Tool import failed: {e}")
        return False

async def test_data_directory():
    """Test that data directory can be created"""
    print("\n📁 Testing data directory creation...")
    
    try:
        import tempfile
        import json
        from datetime import datetime
        
        # Test creating student data directory
        test_dir = os.path.join(os.path.dirname(__file__), "test_student_data")
        os.makedirs(test_dir, exist_ok=True)
        
        # Test creating a sample student file
        test_data = {
            "personal_info": {
                "name": "Test Student",
                "age": 25,
                "registration_date": datetime.now().isoformat(),
                "student_id": "test_student_123"
            },
            "assessments": [],
            "progress_history": []
        }
        
        test_file = os.path.join(test_dir, "test_student.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        # Verify file was created and can be read
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            assert loaded_data["personal_info"]["name"] == "Test Student"
        
        # Clean up
        os.remove(test_file)
        os.rmdir(test_dir)
        
        print("✅ Data directory and file operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Data directory test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 AI Tutor IELTS Screener Agent - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Agent Setup", test_agent_basic),
        ("Tool Imports", test_tools_import), 
        ("Data Directory", test_data_directory)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Tutor agent is ready to use.")
        print("\n🚀 To run the agent:")
        print("1. Set your GOOGLE_API_KEY environment variable")
        print("2. Use `adk run .` or `adk web .` from the ai_tutor directory")
        print("3. Start an IELTS assessment session!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 