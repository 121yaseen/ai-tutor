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

"""AI Tutor - IELTS Student Screener Agent"""

from google.adk.agents import Agent
from .prompt import AI_TUTOR_PROMPT
from .tools.student_management import (
    save_student_info, get_student_info, 
    save_assessment_results, load_student_history
)
from .tools.ielts_assessment import (
    conduct_speaking_assessment, calculate_band_score, 
    generate_improvement_suggestions, get_task_card, get_discussion_questions
)

root_agent = Agent(
    name="ai_tutor_ielts_screener",
    model="gemini-2.0-flash-live-001",  # Use live streaming model for web interface
    description="Professional IELTS speaking examiner providing comprehensive assessment and feedback",
    instruction=AI_TUTOR_PROMPT,
    tools=[
        save_student_info,
        get_student_info,
        save_assessment_results,
        load_student_history,
        conduct_speaking_assessment,
        calculate_band_score,
        generate_improvement_suggestions,
        get_task_card,
        get_discussion_questions
    ]
) 