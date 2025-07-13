import json
from pathlib import Path

def load_questions():
    file_path = Path(__file__).parent / "agent_data/ielts_questions.json"
    with open(file_path, 'r') as f:
        return json.load(f)

IELTS_QUESTIONS = load_questions()

# Band score to difficulty mapping for adaptive questioning
DIFFICULTY_MAPPING = {
    "beginner": {"range": [0, 4.5], "questions": "basic"},
    "intermediate": {"range": [5.0, 6.5], "questions": "intermediate"},  
    "advanced": {"range": [7.0, 9.0], "questions": "advanced"}
}

 