#!/usr/bin/env python3
"""
Simple script to run tests for the agent_tools module.
This script demonstrates how to run the save_test_result_to_json tests.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the agent_tools tests"""
    
    print("🚀 Running AI IELTS Examiner Backend Tests")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n📋 Running all agent_tools tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_agent_tools.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n🎯 Test Coverage:")
        print("   ✓ save_test_result_to_json() function")
        print("   ✓ Error handling for missing parameters")
        print("   ✓ Database interaction mocking")
        print("   ✓ Complex IELTS test data preservation")
        print("   ✓ Timestamp and test number generation")
        print("   ✓ Data validation and required fields")
    else:
        print("\n❌ Some tests failed!")
        return False
    
    print("\n🧪 To run specific tests:")
    print("   pytest tests/test_agent_tools.py::TestSaveTestResultToJson::test_save_test_result_complex_sample_data -v")
    print("\n📊 To run with coverage:")
    print("   pytest --cov=src --cov-report=html tests/test_agent_tools.py")
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 