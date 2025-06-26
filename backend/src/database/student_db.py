import os
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import orjson
from ..models.student_models import StudentPerformance

class StudentDB:
    def __init__(self):
        self.connection_string = os.environ.get("SUPABASE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("SUPABASE_CONNECTION_STRING environment variable is required for StudentDB")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string, connect_timeout=10)

    def get_student(self, email: str) -> Optional[str]:
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT email, name, history FROM public.students WHERE email = %s", (email,))
                    result = cursor.fetchone()
                    if result:
                        # Ensure history is a list of dicts, even if it's null or not a list
                        history_data = result.get('history', [])
                        if not isinstance(history_data, list):
                            history_data = [] # Default to empty list if not a list
                        
                        student_data = {
                            "history": history_data
                        }
                        return student_data
            return None
        except Exception as e:
            print(f"[ERROR] StudentDB get_student error: {e}")
            return None

    def upsert_student(self, student: StudentPerformance):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Convert history to JSONB string
                    history_json = orjson.dumps(student.history).decode('utf-8')
                    
                    cursor.execute(
                        "INSERT INTO public.students (email, name, history) VALUES (%s, %s, %s)"
                        " ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name, history = EXCLUDED.history",
                        (student.email, student.name, history_json)
                    )
                conn.commit()
                print(f"[LOG] Saved/Updated student: {student.email}")
        except Exception as e:
            print(f"[ERROR] StudentDB upsert_student error: {e}")

    def create_student_if_not_exists(self, email: str, name: str):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO public.students (email, name, history) VALUES (%s, %s, '[]'::jsonb)"
                        " ON CONFLICT (email) DO NOTHING",
                        (email, name)
                    )
                conn.commit()
                print(f"[LOG] Created student if not exists: {email}")
        except Exception as e:
            print(f"[ERROR] StudentDB create_student_if_not_exists error: {e}")