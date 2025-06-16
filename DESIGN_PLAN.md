# Implementation Plan: User Authentication & Profiles

This document outlines the low-level design and step-by-step implementation plan for adding user authentication, profiles, and persistent data storage to the AI IELTS Examiner application.

## 1. Overview & Goals

The primary goal is to transform the application from a single-session demo into a multi-user platform where users can:
- Sign up for an account.
- Log in and log out securely.
- Have their test history saved and associated with their profile.
- View their profile and past test results.

We will achieve this by replacing the current `student.json` file with a robust database and authentication service.

## 2. Technology Stack

- **Authentication & Database:** **Supabase**
  - **Reasoning:** Supabase provides an integrated solution with a PostgreSQL database, secure user authentication, and auto-generated APIs. This simplifies development, enhances security, and provides a clear path for future scalability. Its client libraries for both Python and JavaScript are well-supported.

## 3. Database Schema (Low-Level Design)

We will create two primary tables in our Supabase PostgreSQL database.

### Table 1: `profiles`

This table will store public user data that is safe to be read by the user and the agent. It is linked one-to-one with the `auth.users` table provided by Supabase.

| Column Name | Data Type     | Constraints & Notes                                |
|-------------|---------------|----------------------------------------------------|
| `id`        | `uuid`        | **Primary Key**, Foreign Key to `auth.users.id`.   |
| `full_name` | `text`        | User's full name.                                  |
| `age`       | `smallint`    | User's age.                                        |
| `created_at`| `timestamptz` | Defaults to `now()`.                               |
| `updated_at`| `timestamptz` | Defaults to `now()`, auto-updates on change.       |

### Table 2: `test_history`

This table will store the results of each IELTS test a user completes.

| Column Name | Data Type     | Constraints & Notes                                |
|-------------|---------------|----------------------------------------------------|
| `id`        | `bigint`      | **Primary Key**, auto-incrementing.                |
| `user_id`   | `uuid`        | Foreign Key to `profiles.id`, indexed.             |
| `band_score`| `float4`      | The final band score for the test (e.g., 7.5).     |
| `feedback`  | `jsonb`       | Detailed feedback (vocabulary, grammar, etc.).     |
| `q_and_a`   | `jsonb`       | A JSON object containing all questions and answers.|
| `created_at`| `timestamptz` | Defaults to `now()`. Marks when the test was taken.|

## 4. Backend Implementation Plan (`agent.py`)

**Objective:** Refactor the agent to use Supabase for data operations instead of a local JSON file.

1.  **Install Dependencies:**
    -   Add `supabase-py` to the Python environment.
    ```bash
    pip install supabase
    ```
    -   Update `requirements.txt`.

2.  **Environment Variables:**
    -   Add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to the `.env` file. The service key is required for backend operations that bypass Row Level Security (RLS).

3.  **Remove `StudentDB`:**
    -   Delete the `StudentDB` class and the `student.json` file logic entirely from `agent.py`.

4.  **Create `DatabaseService`:**
    -   Implement a new class, `DatabaseService`, to encapsulate all interactions with Supabase.
    -   Initialize the Supabase client in its constructor.
    -   **Methods:**
        -   `get_profile(user_id: str) -> dict`: Fetches a user's profile by their ID.
        -   `get_test_history(user_id: str) -> list`: Fetches all past test results for a user.
        -   `create_profile(user_id: str, name: str, age: int) -> dict`: Creates a new user profile. This will be triggered after a user signs up on the frontend.
        -   `save_test_result(user_id: str, result: dict)`: Saves a completed test to the `test_history` table.

5.  **Update Agent `entrypoint`:**
    -   Modify the `entrypoint` function in `agent.py`. When the agent starts a session, it needs to know which user it's talking to.
    -   The `user_id` will be passed in the LiveKit token's `participantIdentity`. The agent will extract this identity upon connection.
    -   This `user_id` will then be passed to the agent's tools.

6.  **Refactor Agent Tools (`@function_tool`):**
    -   `get_student` -> `get_user_profile_and_history(user_id: str)`: This tool will now use the `DatabaseService` to fetch the user's profile and their past test results. It will return a summary to the LLM.
    -   `create_student` -> (Handled by frontend signup flow, but a tool can be kept for administrative purposes if needed).
    -   `add_test_result` -> `save_test_result(user_id: str, result: dict)`: This tool will take the `user_id` and the final test analysis from the LLM and use the `DatabaseService` to persist it.

## 5. Frontend Implementation Plan (`frontend/`)

**Objective:** Implement a full authentication flow, user profile page, and connect it to the LiveKit session.

1.  **Install Dependencies:**
    ```bash
    pnpm install @supabase/auth-helpers-nextjs @supabase/supabase-js @supabase/auth-ui-react @supabase/auth-ui-shared
    ```

2.  **Environment Variables:**
    -   Create a `.env.local` file in the `frontend` directory.
    -   Add `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

3.  **Setup Supabase Client:**
    -   Create a utility file (`frontend/lib/supabase-client.ts`) to initialize and export the Supabase client for use across the application. Use `createPagesBrowserClient` for client-side usage.

4.  **Create Authentication UI:**
    -   Create a new route `frontend/app/login/page.tsx`.
    -   Use the `@supabase/auth-ui-react` `Auth` component to quickly build a beautiful and secure login/signup form. This component handles password resets, social logins (optional), and magic links out-of-the-box.

5.  **Implement Protected Routes:**
    -   The main voice assistant page (`frontend/app/page.tsx`) must become a protected route.
    -   Use Supabase's auth helpers to check for an active session. If no session exists, redirect the user to `/login`.
    -   A user should only be able to see and interact with the voice assistant after they have logged in.

6.  **Create Profile Page:**
    -   Create a new route `frontend/app/profile/page.tsx`.
    -   This page will be protected.
    -   It will fetch the logged-in user's profile information and their test history from the Supabase database.
    -   Display the information in a clean, user-friendly layout. Include a "Log Out" button.

7.  **Integrate Auth with LiveKit Connection:**
    -   This is the most critical step.
    -   Modify `frontend/app/api/connection-details/route.ts`.
    -   Before generating a LiveKit token, this endpoint **must** verify the user's Supabase session from the incoming request.
    -   If the user is authenticated, retrieve their Supabase `user.id`.
    -   When creating the `AccessToken` for LiveKit, set `identity` to the user's Supabase ID:
        ```typescript
        const accessToken = new AccessToken(apiKey, apiSecret, {
          identity: user.id, // <-- Use Supabase user ID here
        });
        ```

## 6. Authentication Flow (User Journey)

1.  **New User:** A new user visits the site and is redirected to the `/login` page.
2.  **Signup:** The user enters their email/password to sign up. Supabase handles the confirmation email.
3.  **First Login:** After confirming, the user logs in. A new entry is created in `auth.users`, and a trigger creates a corresponding entry in our public `profiles` table.
4.  **Redirect to App:** The user is redirected to the main application page (`/`).
5.  **Start Test:** The user clicks "Start the test".
    -   The frontend calls `/api/connection-details`.
    -   The API endpoint verifies the Supabase session, gets the user's ID, and generates a LiveKit token with the user's ID as the `participantIdentity`.
    -   The frontend connects to the LiveKit room.
6.  **Agent Interaction:**
    -   The backend agent joins the room, sees the participant with the specific ID, and knows which user it is.
    -   The agent can now use its tools, passing the `user_id` to fetch history or save new results.
7.  **Profile Viewing:** At any time, the user can navigate to `/profile` to see their details and past test scores. 