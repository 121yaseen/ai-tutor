#!/usr/bin/env python3
"""
Script to run integration tests that connect to real Supabase test database.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def check_environment():
    """Check if test environment is properly configured"""
    load_dotenv()
    
    test_db_connection = os.getenv("TEST_SUPABASE_CONNECTION_STRING")
    if not test_db_connection:
        print("❌ ERROR: TEST_SUPABASE_CONNECTION_STRING not found in .env file")
        print("\n🔧 Setup required:")
        print("1. Add TEST_SUPABASE_CONNECTION_STRING to your .env file")
        print("2. Ensure the test database exists and is accessible")
        print("3. Verify the connection string format: postgresql://user:pass@host:port/dbname")
        return False
    
    print("✅ Test database connection string found")
    return True

def run_integration_tests():
    """Run the integration tests with proper setup"""
    
    print("🧪 AI IELTS Examiner - Integration Tests")
    print("=" * 50)
    
    if not check_environment():
        return False
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n🗄️  Running integration tests with real Supabase database...")
    print("⚠️  These tests will write actual data to the test database")
    
    # Run integration tests
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_agent_tools_integration.py",
        "-v", 
        "--tb=short",
        "-m", "integration"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
    
    if result.returncode == 0:
        print("\n✅ All integration tests passed!")
        print("\n🎯 Integration Test Coverage:")
        print("   ✓ Real database connection and permissions")
        print("   ✓ Actual data persistence to Supabase")
        print("   ✓ Multiple test results for same user")
        print("   ✓ Complex real-world IELTS data handling")
        print("   ✓ Database error handling")
        print("   ✓ Data integrity verification")
    else:
        print("\n❌ Some integration tests failed!")
        print("\n🔍 Common issues:")
        print("   • Database connection string incorrect")
        print("   • Database permissions insufficient")
        print("   • Network connectivity issues")
        print("   • Database schema mismatches")
        return False
    
    print("\n📊 To run specific integration tests:")
    print("   pytest tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_save_complex_real_world_data -v")
    
    print("\n🔄 To run both unit and integration tests:")
    print("   pytest tests/ -v")
    
    return True

def run_unit_tests_only():
    """Run only unit tests (with mocks)"""
    print("\n🚀 Running unit tests (with mocks)...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_agent_tools.py",
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    return result.returncode == 0

if __name__ == "__main__":
    print("Choose test type:")
    print("1. Integration tests (real database)")
    print("2. Unit tests only (mocks)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    success = False
    
    if choice == "1":
        success = run_integration_tests()
    elif choice == "2":
        success = run_unit_tests_only()
    elif choice == "3":
        unit_success = run_unit_tests_only()
        integration_success = run_integration_tests()
        success = unit_success and integration_success
    else:
        print("Invalid choice. Running integration tests by default.")
        success = run_integration_tests()
    
    sys.exit(0 if success else 1) 