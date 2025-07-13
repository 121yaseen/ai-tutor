import json
import random
from pathlib import Path
from typing import Dict, Optional

def load_questions() -> Dict:
    """Loads the entire question pool from the JSON file."""
    file_path = Path(__file__).parent / "agent_data/ielts_questions.json"
    with open(file_path, 'r') as f:
        return json.load(f)

IELTS_QUESTIONS = load_questions()

DIFFICULTY_MAPPING = {
    "beginner": {"range": [0, 4.5], "key": "basic"},
    "intermediate": {"range": [5.0, 6.5], "key": "intermediate"},
    "advanced": {"range": [7.0, 9.0], "key": "advanced"}
}

def get_difficulty_level(score: Optional[float]) -> str:
    """Determines the difficulty level based on the user's last band score."""
    if score is None:
        print("[LOG] No previous score found. Defaulting to intermediate difficulty.")
        return "intermediate"

    for level, data in DIFFICULTY_MAPPING.items():
        if data["range"][0] <= score <= data["range"][1]:
            print(f"[LOG] Score {score} falls into '{data['key']}' difficulty level.")
            return data["key"]
            
    print(f"[LOG] Score {score} is outside defined ranges. Defaulting to intermediate difficulty.")
    return "intermediate"

def select_session_questions(difficulty: str) -> Dict[str, str]:
    """
    Randomly selects one question/topic for each part of the test based on difficulty.
    """
    if difficulty not in ["basic", "intermediate", "advanced"]:
        print(f"[LOG] Invalid difficulty '{difficulty}' provided. Defaulting to intermediate.")
        difficulty = "intermediate"

    print(f"[LOG] Selecting random questions for difficulty level: {difficulty}")
    part1_question = random.choice(IELTS_QUESTIONS["part1"][difficulty])
    part2_topic = random.choice(IELTS_QUESTIONS["part2"][difficulty])
    part3_question = random.choice(IELTS_QUESTIONS["part3"][difficulty])
    
    selected_questions = {
        "part1": part1_question,
        "part2": part2_topic,
        "part3": part3_question
    }
    
    print(f"[LOG] Selected Part 1 Question: {part1_question}")
    print(f"[LOG] Selected Part 2 Topic: {part2_topic}")
    print(f"[LOG] Selected Part 3 Question: {part3_question}")

    return selected_questions


 