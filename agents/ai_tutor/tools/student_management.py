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
from firestore_client import get_firestore_client
import uuid
from google.cloud import firestore


async def save_student_info(name: str, age: int, tool_context: ToolContext) -> str:
    """
    Save student's basic information to Firestore and session context.
    
    Args:
        name (str): Student's full name
        age (int): Student's age
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Confirmation message about saving student information
    """
    try:
        db = get_firestore_client()
        student_id = str(uuid.uuid4())
        student_data = {
                "name": name,
                "age": age,
                "registration_date": datetime.now().isoformat(),
            "student_id": student_id
        }
        db.collection("students").document(student_id).set(student_data)
        tool_context.state["student_info"] = student_data
        tool_context.state["student_id"] = student_id
        return f"Successfully registered student: {name} (Age: {age}). Student ID: {student_id}"
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
    Save complete IELTS assessment results to Firestore.
    
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
        db = get_firestore_client()
        student_id = tool_context.state.get("student_id")
        if not student_id:
            return "Error: No student registered. Please register student first."
        
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
        db.collection("students").document(student_id).collection("assessments").add(assessment_record)
        
        # Update progress history
        progress_entry = {
            "date": datetime.now().isoformat(),
            "band_score": band_score,
            "key_areas_improved": strengths,
            "areas_to_focus": weaknesses
        }
        db.collection("students").document(student_id).collection("progress_history").add(progress_entry)
        
        # Update session context
        tool_context.state["latest_assessment"] = assessment_record
        
        return f"Assessment results saved successfully! Overall band score: {band_score}/9.0"
    except Exception as e:
        return f"Error saving assessment results: {str(e)}"


async def load_student_history(student_name: str, tool_context: ToolContext) -> str:
    """
    Load previous assessment history for a returning student from Firestore.
    
    Args:
        student_name (str): Student's name to search for
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Student's assessment history or message if not found
    """
    try:
        db = get_firestore_client()
        # Search for student by name (latest registration)
        students_ref = db.collection("students").where("name", "==", student_name).order_by("registration_date", direction=firestore.Query.DESCENDING).limit(1)
        students = list(students_ref.stream())
        if not students:
            return f"No previous records found for student: {student_name}"
        student_doc = students[0]
        student_data = student_doc.to_dict()
        student_id = student_data["student_id"]
        # Get assessments
        assessments_ref = db.collection("students").document(student_id).collection("assessments").order_by("assessment_date")
        assessments = list(assessments_ref.stream())
        # Prepare history summary
        history_summary = f"Student: {student_data['name']}\n"
        history_summary += f"Age: {student_data['age']}\n"
        history_summary += f"Registered: {student_data['registration_date']}\n\n"
        if assessments:
            history_summary += "Previous Assessments:\n"
            for i, assessment in enumerate(assessments, 1):
                a = assessment.to_dict()
                history_summary += f"{i}. Date: {a['assessment_date'][:10]}\n"
                history_summary += f"   Band Score: {a['scores']['overall_band']}/9.0\n"
                history_summary += f"   Strengths: {a['evaluation']['strengths'][:100]}...\n\n"
        else:
            history_summary += "No previous assessments on record.\n"
        return history_summary
    except Exception as e:
        return f"Error loading student history: {str(e)}" 