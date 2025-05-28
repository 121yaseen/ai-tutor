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

"""IELTS assessment tools for AI Tutor"""

import random
from typing import Dict, List, Tuple
from google.adk.tools import ToolContext


# IELTS Speaking Test Task Cards for Part 2
TASK_CARDS = [
    {
        "topic": "Describe a memorable journey you have taken",
        "points": [
            "Where you went",
            "Who you went with",
            "What you did there",
            "Why this journey was memorable for you"
        ]
    },
    {
        "topic": "Describe someone who has influenced you",
        "points": [
            "Who this person is",
            "How you know them",
            "What influence they have had on you",
            "Why you think they are a good influence"
        ]
    },
    {
        "topic": "Describe a skill you would like to learn",
        "points": [
            "What the skill is",
            "Why you want to learn it",
            "How you plan to learn it",
            "What difficulties you might face"
        ]
    },
    {
        "topic": "Describe a place you like to visit in your free time",
        "points": [
            "Where this place is",
            "How often you go there",
            "What you do when you are there",
            "Why you enjoy visiting this place"
        ]
    },
    {
        "topic": "Describe a book or movie that made an impression on you",
        "points": [
            "What the book/movie was about",
            "When you read/watched it",
            "What impression it made on you",
            "Why you would or wouldn't recommend it to others"
        ]
    }
]

# Part 3 Discussion Questions (linked to Part 2 topics)
DISCUSSION_QUESTIONS = {
    "journey": [
        "How has travel changed in recent years?",
        "Do you think travel is important for young people? Why?",
        "What are the benefits and drawbacks of traveling alone versus with others?",
        "How do you think technology has affected the way people travel?"
    ],
    "influence": [
        "What role do role models play in society?",
        "Do you think celebrities make good role models? Why or why not?",
        "How can parents be positive influences on their children?",
        "In what ways can friends influence each other?"
    ],
    "skill": [
        "Why is it important for people to continue learning throughout their lives?",
        "What skills do you think will be most important in the future?",
        "Do you think it's better to learn skills through formal education or practical experience?",
        "How has technology changed the way people learn new skills?"
    ],
    "place": [
        "How important are public spaces in a community?",
        "Do you think people today have enough free time? Why or why not?",
        "What are the differences between how older and younger generations spend their free time?",
        "How have leisure activities changed over the past few decades?"
    ],
    "media": [
        "How has the way people consume media changed in recent years?",
        "Do you think books will become obsolete in the digital age?",
        "What impact do movies and books have on society?",
        "Should there be restrictions on the content of books and movies?"
    ]
}

async def conduct_speaking_assessment(
    part: int,
    student_responses: str,
    tool_context: ToolContext
) -> str:
    """
    Analyze student responses for a specific part of the IELTS speaking test.
    
    Args:
        part (int): IELTS speaking test part (1, 2, or 3)
        student_responses (str): Student's responses during this part
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Analysis of the student's performance for this part
    """
    try:
        # Store the responses in session state
        if "assessment_data" not in tool_context.state:
            tool_context.state["assessment_data"] = {}
        
        tool_context.state["assessment_data"][f"part_{part}"] = student_responses
        
        # Analyze responses based on IELTS criteria
        analysis = _analyze_speaking_performance(student_responses, part)
        
        return f"Part {part} Assessment Complete:\n\n{analysis}"
        
    except Exception as e:
        return f"Error conducting assessment: {str(e)}"


async def calculate_band_score(tool_context: ToolContext) -> str:
    """
    Calculate overall IELTS band score based on all speaking test parts.
    
    Args:
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Detailed band score breakdown and overall score
    """
    try:
        if "assessment_data" not in tool_context.state:
            return "Error: No assessment data found. Please conduct the speaking test first."
        
        assessment_data = tool_context.state["assessment_data"]
        
        # Analyze all parts and calculate scores
        fluency_scores = []
        lexical_scores = []
        grammar_scores = []
        pronunciation_scores = []
        
        for part_num in [1, 2, 3]:
            part_key = f"part_{part_num}"
            if part_key in assessment_data:
                response = assessment_data[part_key]
                scores = _calculate_part_scores(response, part_num)
                fluency_scores.append(scores["fluency"])
                lexical_scores.append(scores["lexical"])
                grammar_scores.append(scores["grammar"])
                pronunciation_scores.append(scores["pronunciation"])
        
        # Calculate average scores for each criterion
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_lexical = sum(lexical_scores) / len(lexical_scores) if lexical_scores else 0
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0
        avg_pronunciation = sum(pronunciation_scores) / len(pronunciation_scores) if pronunciation_scores else 0
        
        # Calculate overall band score (average of four criteria)
        overall_band = (avg_fluency + avg_lexical + avg_grammar + avg_pronunciation) / 4
        overall_band = round(overall_band * 2) / 2  # Round to nearest 0.5
        
        # Store scores in session state
        tool_context.state["band_scores"] = {
            "fluency_coherence": round(avg_fluency * 2) / 2,
            "lexical_resource": round(avg_lexical * 2) / 2,
            "grammatical_range_accuracy": round(avg_grammar * 2) / 2,
            "pronunciation": round(avg_pronunciation * 2) / 2,
            "overall_band": overall_band
        }
        
        result = f"IELTS Speaking Band Score Assessment:\n\n"
        result += f"📊 Detailed Scores:\n"
        result += f"• Fluency and Coherence: {tool_context.state['band_scores']['fluency_coherence']}/9.0\n"
        result += f"• Lexical Resource: {tool_context.state['band_scores']['lexical_resource']}/9.0\n"
        result += f"• Grammatical Range and Accuracy: {tool_context.state['band_scores']['grammatical_range_accuracy']}/9.0\n"
        result += f"• Pronunciation: {tool_context.state['band_scores']['pronunciation']}/9.0\n\n"
        result += f"🎯 Overall Band Score: {overall_band}/9.0\n"
        
        return result
        
    except Exception as e:
        return f"Error calculating band score: {str(e)}"


async def generate_improvement_suggestions(tool_context: ToolContext) -> str:
    """
    Generate personalized improvement suggestions based on assessment results.
    
    Args:
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Detailed improvement suggestions and study recommendations
    """
    try:
        if "band_scores" not in tool_context.state:
            return "Error: No band scores found. Please calculate band scores first."
        
        scores = tool_context.state["band_scores"]
        
        # Identify strengths and weaknesses
        criteria = {
            "Fluency and Coherence": scores["fluency_coherence"],
            "Lexical Resource": scores["lexical_resource"],
            "Grammatical Range and Accuracy": scores["grammatical_range_accuracy"],
            "Pronunciation": scores["pronunciation"]
        }
        
        strongest_area = max(criteria, key=criteria.get)
        weakest_area = min(criteria, key=criteria.get)
        
        suggestions = f"🎯 Personalized Improvement Plan:\n\n"
        
        # Strengths
        suggestions += f"✅ Your Strengths:\n"
        suggestions += f"• {strongest_area}: {criteria[strongest_area]}/9.0 - Keep up the excellent work!\n"
        for area, score in criteria.items():
            if score >= 6.0 and area != strongest_area:
                suggestions += f"• {area}: {score}/9.0 - Good foundation to build upon\n"
        
        suggestions += f"\n🎯 Priority Areas for Improvement:\n"
        
        # Specific suggestions based on weakest areas
        if criteria["Fluency and Coherence"] < 6.0:
            suggestions += f"• Fluency and Coherence ({criteria['Fluency and Coherence']}/9.0):\n"
            suggestions += "  - Practice speaking for 2-3 minutes without stopping\n"
            suggestions += "  - Use linking words (however, therefore, furthermore)\n"
            suggestions += "  - Record yourself and listen for hesitations\n"
            suggestions += "  - Practice with a timer to build confidence\n\n"
        
        if criteria["Lexical Resource"] < 6.0:
            suggestions += f"• Lexical Resource ({criteria['Lexical Resource']}/9.0):\n"
            suggestions += "  - Learn 10 new vocabulary words daily\n"
            suggestions += "  - Practice using synonyms and paraphrasing\n"
            suggestions += "  - Read diverse materials (news, articles, books)\n"
            suggestions += "  - Use vocabulary in context, not just memorization\n\n"
        
        if criteria["Grammatical Range and Accuracy"] < 6.0:
            suggestions += f"• Grammar ({criteria['Grammatical Range and Accuracy']}/9.0):\n"
            suggestions += "  - Focus on complex sentence structures\n"
            suggestions += "  - Practice conditional sentences (if/when clauses)\n"
            suggestions += "  - Review tense consistency in narratives\n"
            suggestions += "  - Use grammar apps for daily practice\n\n"
        
        if criteria["Pronunciation"] < 6.0:
            suggestions += f"• Pronunciation ({criteria['Pronunciation']}/9.0):\n"
            suggestions += "  - Practice with phonetic transcriptions\n"
            suggestions += "  - Focus on word stress and sentence rhythm\n"
            suggestions += "  - Listen to native speakers and shadow their speech\n"
            suggestions += "  - Record yourself to identify pronunciation patterns\n\n"
        
        # General study plan
        suggestions += f"📚 Recommended Study Plan:\n"
        suggestions += "• Daily: 30 minutes speaking practice\n"
        suggestions += "• Weekly: Take 2-3 practice IELTS speaking tests\n"
        suggestions += "• Monthly: Review progress and adjust focus areas\n"
        suggestions += "• Resources: IELTS preparation books, online practice tests, conversation partners\n\n"
        
        # Next steps based on current band score
        overall_band = scores["overall_band"]
        if overall_band < 5.0:
            suggestions += "🎯 Your next goal: Reach Band 5.0 by focusing on basic fluency and accuracy\n"
        elif overall_band < 6.0:
            suggestions += "🎯 Your next goal: Reach Band 6.0 by expanding vocabulary and reducing errors\n"
        elif overall_band < 7.0:
            suggestions += "🎯 Your next goal: Reach Band 7.0 by using more complex language structures\n"
        else:
            suggestions += "🎯 Excellent! Focus on consistency and natural expression for higher bands\n"
        
        return suggestions
        
    except Exception as e:
        return f"Error generating improvement suggestions: {str(e)}"


def _analyze_speaking_performance(response: str, part: int) -> str:
    """Analyze speaking performance for a specific part"""
    
    # Basic analysis based on response length and content
    word_count = len(response.split())
    
    analysis = f"Response Analysis for Part {part}:\n"
    analysis += f"• Word count: {word_count} words\n"
    
    if part == 1:
        if word_count < 50:
            analysis += "• Response length: Too brief for Part 1. Aim for more detailed answers.\n"
        elif word_count > 150:
            analysis += "• Response length: Good detail level for Part 1.\n"
        else:
            analysis += "• Response length: Appropriate for Part 1.\n"
    
    elif part == 2:
        if word_count < 150:
            analysis += "• Response length: Too brief for Part 2. Should speak for 1-2 minutes.\n"
        elif word_count > 300:
            analysis += "• Response length: Excellent detail for Part 2.\n"
        else:
            analysis += "• Response length: Good for Part 2.\n"
    
    elif part == 3:
        if word_count < 100:
            analysis += "• Response length: Too brief for Part 3. Provide more developed answers.\n"
        else:
            analysis += "• Response length: Appropriate depth for Part 3 discussion.\n"
    
    return analysis


def _calculate_part_scores(response: str, part: int) -> Dict[str, float]:
    """Calculate estimated scores for each IELTS criterion"""
    
    word_count = len(response.split())
    sentence_count = response.count('.') + response.count('!') + response.count('?')
    
    # Basic scoring algorithm (simplified for demonstration)
    # In real implementation, this would use more sophisticated NLP analysis
    
    # Fluency score based on length and flow
    if word_count < 50:
        fluency = 4.0
    elif word_count < 100:
        fluency = 5.0
    elif word_count < 150:
        fluency = 6.0
    elif word_count < 200:
        fluency = 7.0
    else:
        fluency = 8.0
    
    # Lexical score based on vocabulary variety (simplified)
    unique_words = len(set(response.lower().split()))
    lexical_ratio = unique_words / word_count if word_count > 0 else 0
    
    if lexical_ratio < 0.4:
        lexical = 4.0
    elif lexical_ratio < 0.5:
        lexical = 5.0
    elif lexical_ratio < 0.6:
        lexical = 6.0
    elif lexical_ratio < 0.7:
        lexical = 7.0
    else:
        lexical = 8.0
    
    # Grammar score based on sentence complexity
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    if avg_sentence_length < 8:
        grammar = 4.0
    elif avg_sentence_length < 12:
        grammar = 5.0
    elif avg_sentence_length < 16:
        grammar = 6.0
    elif avg_sentence_length < 20:
        grammar = 7.0
    else:
        grammar = 8.0
    
    # Pronunciation score (would need audio analysis in real implementation)
    # For text-based assessment, use average of other scores with slight variation
    pronunciation = (fluency + lexical + grammar) / 3 + random.uniform(-0.5, 0.5)
    pronunciation = max(1.0, min(9.0, pronunciation))
    
    return {
        "fluency": fluency,
        "lexical": lexical,
        "grammar": grammar,
        "pronunciation": pronunciation
    }


async def get_task_card(tool_context: ToolContext) -> str:
    """
    Get a random task card for IELTS Speaking Part 2.
    
    Args:
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: A formatted task card with topic and bullet points
    """
    try:
        task_card = random.choice(TASK_CARDS)
        
        # Store the task card in session state
        tool_context.state["current_task_card"] = task_card
        
        card_text = f"📋 IELTS Speaking Part 2 - Task Card\n\n"
        card_text += f"Topic: {task_card['topic']}\n\n"
        card_text += "You should say:\n"
        for point in task_card['points']:
            card_text += f"• {point}\n"
        card_text += "\nYou have 1 minute to prepare and should speak for 1-2 minutes.\n"
        
        return card_text
        
    except Exception as e:
        return f"Error getting task card: {str(e)}"


async def get_discussion_questions(topic_type: str, tool_context: ToolContext) -> str:
    """
    Get discussion questions for IELTS Speaking Part 3 based on the Part 2 topic.
    
    Args:
        topic_type (str): Type of topic (journey, influence, skill, place, media)
        tool_context (ToolContext): The tool context for accessing session state
        
    Returns:
        str: Formatted discussion questions for Part 3
    """
    try:
        if topic_type not in DISCUSSION_QUESTIONS:
            topic_type = "journey"  # Default fallback
        
        questions = DISCUSSION_QUESTIONS[topic_type]
        selected_questions = random.sample(questions, min(3, len(questions)))
        
        # Store questions in session state
        tool_context.state["part3_questions"] = selected_questions
        
        questions_text = f"🗣️ IELTS Speaking Part 3 - Discussion Questions\n\n"
        for i, question in enumerate(selected_questions, 1):
            questions_text += f"{i}. {question}\n\n"
        
        return questions_text
        
    except Exception as e:
        return f"Error getting discussion questions: {str(e)}" 