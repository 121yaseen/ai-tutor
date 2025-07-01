# Integration Tests Setup Guide

## Overview

The integration tests connect to a **real Supabase PostgreSQL database** to test the `save_test_result_to_json` function with actual data persistence. This ensures the function works correctly with real database operations.

## 🔧 Prerequisites

### 1. Test Supabase Database

You need a **separate test database** (don't use your production database):

- Create a new Supabase project for testing
- Or create a separate database in your existing project
- Ensure the `students` table exists with the correct schema

### 2. Database Schema

The test database should have the `students` table:

```sql
-- Create students table (if not exists)
CREATE TABLE IF NOT EXISTS public.students (
    email text PRIMARY KEY,
    name text,
    history jsonb DEFAULT '[]'::jsonb NOT NULL
);

-- Enable Row Level Security
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;

-- Create policies (optional for test database)
CREATE POLICY "Enable read access for authenticated users based on email"
  ON public.students FOR SELECT
  TO authenticated
  USING (auth.email() = email);

CREATE POLICY "Enable insert for authenticated users"
  ON public.students FOR INSERT
  TO authenticated
  WITH CHECK (auth.email() = email);

CREATE POLICY "Enable update for authenticated users"
  ON public.students FOR UPDATE
  TO authenticated
  USING (auth.email() = email);
```

## 🚀 Setup Steps

### Step 1: Get Your Test Database Connection String

1. **Go to your Supabase test project dashboard**
2. **Navigate to Settings → Database**
3. **Copy the connection string** from "Connection parameters"
4. **Format**: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

### Step 2: Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your test database connection
nano .env
```

Add this line to your `.env` file:
```bash
TEST_SUPABASE_CONNECTION_STRING=postgresql://postgres:your_password@db.your-project-ref.supabase.co:5432/postgres
```

### Step 3: Install Dependencies

```bash
# Activate virtual environment
source ../venv/bin/activate

# Install required packages
pip install python-dotenv psycopg2
```

## 🧪 Running Integration Tests

### Option 1: Interactive Script

```bash
python run_integration_tests.py
```

Choose:
- `1` - Integration tests (real database)
- `2` - Unit tests only (mocks) 
- `3` - Both unit and integration tests

### Option 2: Direct pytest Commands

```bash
# Run all integration tests
pytest tests/test_agent_tools_integration.py -v -m integration

# Run specific integration test
pytest tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_save_complex_real_world_data -v

# Run with output to see database operations
pytest tests/test_agent_tools_integration.py -v -s -m integration
```

### Option 3: Run Both Unit and Integration Tests

```bash
# Run all tests (unit + integration)
pytest tests/ -v

# Run only unit tests (fast)
pytest tests/test_agent_tools.py -v

# Run only integration tests (slower)
pytest tests/test_agent_tools_integration.py -v -m integration
```

## 📊 What the Integration Tests Do

### 1. **Real Database Connection** 
- ✅ Connects to actual Supabase PostgreSQL
- ✅ Tests database permissions and access
- ✅ Verifies schema compatibility

### 2. **Data Persistence Testing**
- ✅ Saves test results to real database
- ✅ Verifies data integrity after save
- ✅ Tests complex IELTS data structures
- ✅ Validates JSON serialization

### 3. **Multiple Test Scenarios**
- ✅ New student creation
- ✅ Multiple tests for same student 
- ✅ Complex real-world IELTS data
- ✅ Error handling with database

### 4. **Data Verification**
- ✅ Confirms data was actually written
- ✅ Validates all fields are preserved
- ✅ Tests timestamp and metadata generation
- ✅ Verifies test numbering sequence

## 🔍 Sample Test Output

```bash
🧪 AI IELTS Examiner - Integration Tests
==================================================

✅ Test database connection string found

🗄️  Running integration tests with real Supabase database...
⚠️  These tests will write actual data to the test database

tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_save_new_student_to_real_database PASSED
tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_save_multiple_tests_for_existing_student PASSED
tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_save_complex_real_world_data PASSED
tests/test_agent_tools_integration.py::TestSaveTestResultToJsonIntegration::test_database_connection_and_permissions PASSED

✅ All integration tests passed!

🎯 Integration Test Coverage:
   ✓ Real database connection and permissions
   ✓ Actual data persistence to Supabase
   ✓ Multiple test results for same user
   ✓ Complex real-world IELTS data handling
   ✓ Database error handling
   ✓ Data integrity verification
```

## 🛠️ Troubleshooting

### Connection Issues
- **Check connection string format**
- **Verify database password**
- **Ensure network access to Supabase**
- **Check database permissions**

### Schema Issues
- **Verify `students` table exists**
- **Check column types (text, jsonb)**
- **Ensure RLS policies don't block inserts**

### Permission Issues
- **Use service role key for tests**
- **Or disable RLS for test database**
- **Check database user permissions**

## 🔒 Security Notes

- **Never use production database for tests**
- **Use a separate test project/database**
- **Test data will persist in the database**
- **Consider periodic cleanup of test data**

## 📝 Example Test Data

The integration tests will create real entries like:

```json
{
  "email": "test_user_20241225_143022_123456@test.example.com",
  "history": [
    {
      "band_score": 6.5,
      "test_number": 1,
      "test_date": "2024-12-25T14:30:22.123456",
      "answers": {
        "Part 1": {"questions": [...], "responses": [...]},
        "Part 2": {"topic": "...", "response": "..."},
        "Part 3": {"questions": [...], "responses": [...]}
      },
      "feedback": {...},
      "strengths": [...],
      "improvements": [...]
    }
  ]
}
```

This data will be **actually written to your test database** and can be viewed in the Supabase dashboard! 