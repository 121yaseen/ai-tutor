# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Student management tools for AI Tutor IELTS Screener"""

import json
import os
from datetime import datetime
from typing import Dict, Optional
from google.adk.tools import ToolContext


async def save_student_info(name: str, age: int, tool_context: ToolContext) -> str:
    """
    Save student's basic information to a file and session context.
    
    Args:
        name (str): Student's full name
        age (int): Student's age
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Confirmation message about saving student information
    """
    try:
        # Create student data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), "..", "student_data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create unique filename based on name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        
        # Prepare student data
        student_data = {
            "personal_info": {
                "name": name,
                "age": age,
                "registration_date": datetime.now().isoformat(),
                "student_id": f"{safe_name}_{timestamp}"
            },
            "assessments": [],
            "progress_history": []
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, indent=2, ensure_ascii=False)
        
        # Store in session context for current session
        tool_context.state["student_info"] = student_data["personal_info"]
        tool_context.state["student_filepath"] = filepath
        
        return f"Successfully registered student: {name} (Age: {age}). Student ID: {student_data['personal_info']['student_id']}"
        
    except Exception as e:
        return f"Error saving student information: {str(e)}"


async def get_student_info(tool_context: ToolContext) -> str:
    """
    Retrieve current student's information from session context.
    
    Args:
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Student information or error message
    """
    try:
        if "student_info" in tool_context.state:
            student_info = tool_context.state["student_info"]
            return f"Current student: {student_info['name']} (Age: {student_info['age']}, ID: {student_info['student_id']})"
        else:
            return "No student information found. Please register the student first."
            
    except Exception as e:
        return f"Error retrieving student information: {str(e)}"


async def save_assessment_results(
    band_score: float,
    fluency_score: float,
    lexical_score: float,
    grammar_score: float,
    pronunciation_score: float,
    strengths: str,
    weaknesses: str,
    improvement_suggestions: str,
    detailed_feedback: str,
    tool_context: ToolContext
) -> str:
    """
    Save complete IELTS assessment results to the student's file.
    
    Args:
        band_score (float): Overall IELTS band score (1-9)
        fluency_score (float): Fluency and coherence score
        lexical_score (float): Lexical resource score
        grammar_score (float): Grammatical range and accuracy score
        pronunciation_score (float): Pronunciation score
        strengths (str): Student's strengths identified during assessment
        weaknesses (str): Areas needing improvement
        improvement_suggestions (str): Specific suggestions for improvement
        detailed_feedback (str): Comprehensive feedback on performance
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Confirmation message about saving assessment results
    """
    try:
        # Check if student is registered
        if "student_filepath" not in tool_context.state:
            return "Error: No student registered. Please register student first."
        
        filepath = tool_context.state["student_filepath"]
        
        # Load existing student data
        with open(filepath, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        
        # Create assessment record
        assessment_record = {
            "assessment_date": datetime.now().isoformat(),
            "assessment_type": "IELTS Speaking Test",
            "scores": {
                "overall_band": band_score,
                "fluency_coherence": fluency_score,
                "lexical_resource": lexical_score,
                "grammatical_range_accuracy": grammar_score,
                "pronunciation": pronunciation_score
            },
            "evaluation": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "improvement_suggestions": improvement_suggestions,
                "detailed_feedback": detailed_feedback
            },
            "examiner": "AI Tutor IELTS Screener",
            "test_duration_minutes": 15
        }
        
        # Add assessment to student record
        student_data["assessments"].append(assessment_record)
        
        # Update progress history
        progress_entry = {
            "date": datetime.now().isoformat(),
            "band_score": band_score,
            "key_areas_improved": strengths,
            "areas_to_focus": weaknesses
        }
        student_data["progress_history"].append(progress_entry)
        
        # Save updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, indent=2, ensure_ascii=False)
        
        # Update session context
        tool_context.state["latest_assessment"] = assessment_record
        
        return f"Assessment results saved successfully! Overall band score: {band_score}/9.0"
        
    except Exception as e:
        return f"Error saving assessment results: {str(e)}"


async def load_student_history(student_name: str, tool_context: ToolContext) -> str:
    """
    Load previous assessment history for a returning student.
    
    Args:
        student_name (str): Student's name to search for
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Student's assessment history or message if not found
    """
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "student_data")
        
        if not os.path.exists(data_dir):
            return "No student records found."
        
        # Search for student files
        safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        matching_files = []
        for filename in os.listdir(data_dir):
            if filename.lower().startswith(safe_name.lower()) and filename.endswith('.json'):
                matching_files.append(filename)
        
        if not matching_files:
            return f"No previous records found for student: {student_name}"
        
        # Load the most recent file
        latest_file = sorted(matching_files)[-1]
        filepath = os.path.join(data_dir, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        
        # Prepare history summary
        history_summary = f"Student: {student_data['personal_info']['name']}\n"
        history_summary += f"Age: {student_data['personal_info']['age']}\n"
        history_summary += f"Registered: {student_data['personal_info']['registration_date']}\n\n"
        
        if student_data['assessments']:
            history_summary += "Previous Assessments:\n"
            for i, assessment in enumerate(student_data['assessments'], 1):
                history_summary += f"{i}. Date: {assessment['assessment_date'][:10]}\n"
                history_summary += f"   Band Score: {assessment['scores']['overall_band']}/9.0\n"
                history_summary += f"   Strengths: {assessment['evaluation']['strengths'][:100]}...\n\n"
        else:
            history_summary += "No previous assessments on record.\n"
        
        return history_summary
        
    except Exception as e:
        return f"Error loading student history: {str(e)}" 