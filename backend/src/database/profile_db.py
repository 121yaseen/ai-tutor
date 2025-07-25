import os
import json
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

class ProfileDB:
    def __init__(self):
        self.connection_string = os.environ.get("SUPABASE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("SUPABASE_CONNECTION_STRING environment variable is required for ProfileDB")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string, connect_timeout=10)

    def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Query to get profile data directly from profiles table
                    query = """
                    SELECT
                        id,
                        email,
                        full_name,
                        first_name,
                        last_name,
                        phone_number,
                        preparing_for,
                        previously_attempted_exam,
                        previous_band_score,
                        exam_date,
                        target_band_score,
                        country,
                        native_language,
                        onboarding_completed,
                        onboarding_presented,
                        created_at,
                        updated_at
                    FROM
                        public.profiles
                    WHERE
                        email = %s
                    """
                    cursor.execute(query, (email,))
                    result = cursor.fetchone()
                    return result
        except Exception as e:
            print(f"[ERROR] ProfileDB get_profile_by_email error: {e}")
            return None

    def get_profile_for_instruction(self, email: str) -> Optional[str]:
        try:
            complete_profile = self.get_profile_by_email(email)
            if complete_profile:
                profile_json = {
                    "first_name": complete_profile["first_name"],
                    "last_name": complete_profile["last_name"],
                    "preparing_for": complete_profile["preparing_for"],
                    "previously_attempted_exam": complete_profile["previously_attempted_exam"],
                    "previous_band_score": complete_profile["previous_band_score"],
                    "exam_date": str(complete_profile["exam_date"]) if complete_profile["exam_date"] else None,
                    "target_band_score": complete_profile["target_band_score"],
                    "country": complete_profile["country"],
                    "native_language": complete_profile["native_language"],
                }
                return json.dumps(profile_json)
            return None
        except Exception as e:
            print(f"[ERROR] ProfileDB get_profile_for_instruction error: {e}")
            return None

# Driver code to test the ProfileDB class independently
if __name__ == "__main__":
    import sys
    
    # Check if email is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python profile_db.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    
    try:
        # Initialize the ProfileDB
        profile_db = ProfileDB()
        
        # Get profile by email
        profile = profile_db.get_profile_by_email(email)
        
        if profile:
            print("\n=== User Profile ===")
            for key, value in profile.items():
                print(f"{key}: {value}")
        else:
            print(f"No profile found for email: {email}")
    
    except Exception as e:
        print(f"Error: {e}")
