import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

class UserDB:
    def __init__(self):
        """Initialize UserDB with Supabase connection string from environment"""
        self.connection_string = os.environ.get("SUPABASE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("SUPABASE_CONNECTION_STRING environment variable is required")
    
    
    def get_user_name(self, email: str) -> Optional[str]:
        """
        Get the user's full name from Supabase database using their email
        
        Args:
            email: The email address of the user
            
        Returns:
            The user's full name or None if not found
        """
        try:
            print(f"[LOG] Fetching user name for email: {email}")
            
            # Connect to PostgreSQL database with timeout
            with psycopg2.connect(
                self.connection_string, 
                cursor_factory=RealDictCursor,
                connect_timeout=10
            ) as conn:
                with conn.cursor() as cursor:
                    # Execute query to get user name from profiles table
                    query = """
                    SELECT
                        COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') AS full_name
                    FROM profiles
                    WHERE email = %s
                    """
                    cursor.execute(query, (email,))
                    result = cursor.fetchone()
                    
                    if result and result.get('full_name'):
                        full_name = result['full_name']
                        print(f"[LOG] Found user name: {full_name}")
                        return full_name
                    else:
                        print(f"[LOG] No user found for email: {email}")
                        return None
                        
        except psycopg2.OperationalError as e:
            print(f"[ERROR] Database connection error: {e}")
            # Fallback: extract name from email
            return self._extract_name_from_email(email)
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            # Fallback: extract name from email
            return self._extract_name_from_email(email)