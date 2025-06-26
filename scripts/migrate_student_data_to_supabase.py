import os
import orjson
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "backend/data/student.json"
SUPABASE_CONNECTION_STRING = os.environ.get("SUPABASE_CONNECTION_STRING")

def migrate_data():
    if not SUPABASE_CONNECTION_STRING:
        print("Error: SUPABASE_CONNECTION_STRING environment variable not set.")
        return

    try:
        with open(DATA_PATH, 'rb') as f:
            content = f.read()
            if not content:
                student_data = {}
            else:
                student_data = orjson.loads(content)
    except FileNotFoundError:
        print(f"Error: {DATA_PATH} not found.")
        return
    except orjson.JSONDecodeError:
        print(f"Error: Could not decode JSON from {DATA_PATH}.")
        return

    if not student_data:
        print("No data to migrate from student.json.")
        return

    conn = None
    try:
        conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
        cur = conn.cursor()

        for email, data in student_data.items():
            name = data.get('name', 'Unknown')
            history = orjson.dumps(data.get('history', [])).decode('utf-8')

            # Check if student already exists
            cur.execute("SELECT email FROM public.students WHERE email = %s", (email,))
            if cur.fetchone():
                print(f"Updating existing student: {email}")
                cur.execute(
                    "UPDATE public.students SET name = %s, history = %s WHERE email = %s",
                    (name, history, email)
                )
            else:
                print(f"Inserting new student: {email}")
                cur.execute(
                    "INSERT INTO public.students (email, name, history) VALUES (%s, %s, %s)",
                    (email, name, history)
                )
        conn.commit()
        print("Data migration completed successfully.")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_data()
