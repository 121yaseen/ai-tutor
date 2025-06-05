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
from typing import Dict, Optional, Any
from google.adk.tools import ToolContext
from firestore_client import get_async_firestore_client
from google.cloud.firestore import SERVER_TIMESTAMP
import uuid
from google.cloud import firestore
from google.cloud.firestore_v1 import Query as FirestoreQuery

# Development/Debug log toggle
ENABLE_DEV_LOGS = True

def _log_dev(message: str):
    if ENABLE_DEV_LOGS:
        print(message)

async def save_student_info(name: str, age: int, tool_context: ToolContext) -> str:
    """
    Save student's basic information to Firestore using their email (from tool_context._invocation_context.session.user_id) as document ID.
    
    Args:
        name (str): Student's full name
        age (int): Student's age
        tool_context (ToolContext): The tool context for accessing session state and user_id (email)
        
    Returns:
        str: Confirmation message about saving student information
    """
    print(f"[DIAG save_student_info] tool_context type: {type(tool_context)}")
    print(f"[DIAG save_student_info] tool_context dir: {dir(tool_context)}")
    try:
        print(f"[DIAG save_student_info] tool_context vars: {vars(tool_context)}")
    except TypeError:
        print(f"[DIAG save_student_info] tool_context vars: Not available (vars() failed, possibly due to slots)")
    email = tool_context._invocation_context.session.user_id
    _log_dev(f"[DEV LOG save_student_info] Attempting to save student info for email: {email}. Name: {name}, Age: {age}")
    
    if not email:
        _log_dev("[DEV LOG save_student_info] Error: Email (user_id) not found in tool_context.")
        return "Error: Could not save student information because user email was not found in the session."

    try:
        db = get_async_firestore_client()
        student_ref = db.collection('students').document(email)
        student_data = {
            'name': name,
            'age': age,
            'email': email, # Storing email in the document as well
            'created_at': SERVER_TIMESTAMP 
        }
        await student_ref.set(student_data)
        _log_dev(f"[DEV LOG save_student_info] Student info saved for {email}: {student_data}")
        return f"Student information for {name} (email: {email}) has been saved."
    except Exception as e:
        _log_dev(f"[DEV LOG save_student_info] Error saving student info for {email}: {e}")
        print(f"Error in save_student_info: {e}") # Keep for more prominent error logging
        return f"Error saving student information: {str(e)}"

async def get_student_info(tool_context: ToolContext) -> dict:
    """
    Get student's basic information from Firestore using their email (from tool_context._invocation_context.session.user_id) as document ID.
    
    Args:
        tool_context (ToolContext): The tool context for accessing session state and user_id (email)
        
    Returns:
        dict: {"found": bool, "data": student_info_dict or None}
    """
    print(f"[DIAG get_student_info] tool_context type: {type(tool_context)}")
    print(f"[DIAG get_student_info] tool_context dir: {dir(tool_context)}")
    try:
        print(f"[DIAG get_student_info] tool_context vars: {vars(tool_context)}")
    except TypeError:
        print(f"[DIAG get_student_info] tool_context vars: Not available (vars() failed, possibly due to slots)")
    
    email = tool_context._invocation_context.session.user_id
    _log_dev(f"[DEV LOG get_student_info] Attempting to get student info for email: {email}")
    
    if not email:
        _log_dev("[DEV LOG get_student_info] Error: Email (user_id) not found in tool_context.")
        return {"found": False, "data": "Error: User email not found in session."}

    try:
        db = get_async_firestore_client()
        student_ref = db.collection('students').document(email)
        student_doc = await student_ref.get()

        if student_doc.exists:
            student_data = student_doc.to_dict()
            _log_dev(f"[DEV LOG get_student_info] Student info found for {email}: {student_data}")
            return {"found": True, "data": student_data}
        else:
            _log_dev(f"[DEV LOG get_student_info] No student info found for {email}.")
            return {"found": False, "data": "No student record found for this email."}
    except Exception as e:
        _log_dev(f"[DEV LOG get_student_info] Error getting student info for {email}: {e}")
        print(f"Error in get_student_info: {e}") # Keep for more prominent error logging
        return {"found": False, "data": f"Error accessing database: {str(e)}"}

async def save_assessment_results(
    assessment_details: dict, 
    band_score: float, 
    improvement_suggestions: list[str], 
    tool_context: ToolContext
) -> str:
    """
    Save student's assessment results to Firestore, linked to their email (tool_context._invocation_context.session.user_id).
    Results are stored in a subcollection 'assessments' under the student's document.
    
    Args:
        assessment_details (dict): Details of the assessment conducted.
        band_score (float): Overall band score.
        improvement_suggestions (list[str]): List of suggestions for improvement.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: Confirmation message.
    """
    print(f"[DIAG save_assessment_results] tool_context type: {type(tool_context)}")
    print(f"[DIAG save_assessment_results] tool_context dir: {dir(tool_context)}")
    try:
        print(f"[DIAG save_assessment_results] tool_context vars: {vars(tool_context)}")
    except TypeError:
        print(f"[DIAG save_assessment_results] tool_context vars: Not available (vars() failed, possibly due to slots)")

    email = tool_context._invocation_context.session.user_id
    _log_dev(f"[DEV LOG save_assessment_results] Attempting to save assessment for email: {email}")

    if not email:
        _log_dev("[DEV LOG save_assessment_results] Error: Email (user_id) not found in tool_context.")
        return "Error: Could not save assessment results because user email was not found in the session."

    try:
        db = get_async_firestore_client()
        # Ensure student document exists or create a placeholder if desired (optional)
        student_doc_ref = db.collection('students').document(email)
        
        # Create a new document in the 'assessments' subcollection
        assessment_data = {
            'assessment_details': assessment_details,
            'band_score': band_score,
            'improvement_suggestions': improvement_suggestions,
            'assessment_date': SERVER_TIMESTAMP 
        }
        
        # Add to subcollection. Firestore automatically generates an ID for the assessment document.
        await student_doc_ref.collection('assessments').add(assessment_data)
        
        _log_dev(f"[DEV LOG save_assessment_results] Assessment results saved for {email}.")
        return "Assessment results have been successfully saved."
    except Exception as e:
        _log_dev(f"[DEV LOG save_assessment_results] Error saving assessment for {email}: {e}")
        print(f"Error in save_assessment_results: {e}") 
        return f"Error saving assessment results: {str(e)}"

async def load_student_history(tool_context: ToolContext) -> dict:
    """
    Load student's past assessment history from Firestore using their email (tool_context._invocation_context.session.user_id).
    
    Args:
        tool_context (ToolContext): The tool context.
        
    Returns:
        dict: {"history_found": bool, "assessments": list_of_assessment_data or "Error message"}
    """
    print(f"[DIAG load_student_history] tool_context type: {type(tool_context)}")
    print(f"[DIAG load_student_history] tool_context dir: {dir(tool_context)}")
    try:
        print(f"[DIAG load_student_history] tool_context vars: {vars(tool_context)}")
    except TypeError:
        print(f"[DIAG load_student_history] tool_context vars: Not available (vars() failed, possibly due to slots)")

    email = tool_context._invocation_context.session.user_id
    _log_dev(f"[DEV LOG load_student_history] Attempting to load history for email: {email}")
    
    if not email:
        _log_dev("[DEV LOG load_student_history] Error: Email (user_id) not found in tool_context.")
        return {"history_found": False, "assessments": "Error: User email not found in session."}

    try:
        db = get_async_firestore_client()
        assessments_ref = db.collection('students').document(email).collection('assessments').order_by('assessment_date', direction='DESCENDING')
        assessment_docs = assessments_ref.stream() # REMOVED await
        
        history = []
        async for doc in assessment_docs: # Iterate asynchronously
            assessment_data = doc.to_dict()
            # Convert Firestore timestamp to a string or epoch for easier handling if needed,
            # or ensure your agent can handle the Timestamp object.
            # For simplicity, we'll keep it as Timestamp for now.
            assessment_data['id'] = doc.id # Add document ID if needed
            history.append(assessment_data)

        if history:
            _log_dev(f"[DEV LOG load_student_history] Found {len(history)} assessment(s) for {email}.")
            # Storing in tool_context.state as per prompt instructions, though returning is also fine.
            tool_context.state["student_assessment_history"] = history 
            return {"history_found": True, "assessments": history}
        else:
            _log_dev(f"[DEV LOG load_student_history] No assessment history found for {email}.")
            tool_context.state["student_assessment_history"] = []
            return {"history_found": False, "assessments": []}
            
    except Exception as e:
        _log_dev(f"[DEV LOG load_student_history] Error loading history for {email}: {e}")
        print(f"Error in load_student_history: {e}")
        return {"history_found": False, "assessments": f"Error accessing database: {str(e)}"} 