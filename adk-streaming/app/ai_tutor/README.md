# AI Tutor - IELTS Student Screener

A comprehensive IELTS speaking assessment agent built with Google ADK that conducts professional-grade speaking tests, provides detailed feedback, and tracks student progress over time.

## 🎯 Overview

This AI Tutor agent is designed to:
- **Screen IELTS students** through professional speaking assessments
- **Conduct comprehensive 3-part IELTS speaking tests** following official guidelines
- **Assign accurate band scores** (1-9) based on IELTS criteria
- **Provide personalized improvement suggestions** for each student
- **Track progress over time** with persistent student records
- **Store all assessment data** with timestamps for future reference

## 🏗️ Architecture

### Agent Type
**Single Conversational Agent** with specialized tools for IELTS assessment and student management.

### Core Components
- **Main Agent**: Professional IELTS examiner persona with comprehensive assessment capabilities
- **Student Management Tools**: Registration, data storage, and progress tracking
- **Assessment Tools**: Speaking test evaluation, scoring, and feedback generation
- **Data Persistence**: JSON-based student records with detailed assessment history

## 🛠️ Features

### Student Management
- ✅ **Student Registration**: Collects and stores name, age, and generates unique student IDs
- ✅ **Progress Tracking**: Maintains comprehensive assessment history
- ✅ **Data Persistence**: Secure JSON file storage with timestamps
- ✅ **Student Lookup**: Retrieves previous assessment history for returning students

### IELTS Speaking Assessment
- ✅ **Part 1 - Introduction & Interview**: Personal questions about familiar topics
- ✅ **Part 2 - Long Turn**: Individual speaking with task cards and preparation time
- ✅ **Part 3 - Discussion**: Abstract discussions and analytical questions
- ✅ **Authentic IELTS Experience**: Follows official test structure and timing

### Scoring & Evaluation
- ✅ **4-Criteria Assessment**: Fluency, Lexical Resource, Grammar, Pronunciation
- ✅ **Band Score Calculation**: Accurate 1-9 scoring with 0.5 increments
- ✅ **Detailed Analysis**: Comprehensive breakdown of strengths and weaknesses
- ✅ **Personalized Feedback**: Specific improvement suggestions and study plans

### Task Management
- ✅ **Random Task Cards**: Varied Part 2 topics for authentic assessment
- ✅ **Discussion Questions**: Topic-linked Part 3 questions for deeper analysis
- ✅ **Assessment Flow**: Structured progression through all test parts

## 📊 Assessment Criteria

The agent evaluates students based on official IELTS speaking criteria:

### Fluency and Coherence (25%)
- Speech flow and hesitation patterns
- Linking words and coherence
- Self-correction and repetition analysis

### Lexical Resource (25%)
- Vocabulary range and flexibility
- Word choice accuracy
- Paraphrasing ability

### Grammatical Range and Accuracy (25%)
- Sentence structure complexity
- Grammar accuracy
- Tense and form consistency

### Pronunciation (25%)
- Intelligibility and clarity
- Word stress and rhythm
- Natural speech patterns

## 🚀 Usage

### Starting an Assessment
1. **Student Registration**: Agent asks for name and age
2. **Test Explanation**: Brief overview of the 3-part structure
3. **Part 1**: Personal interview questions (4-5 minutes)
4. **Part 2**: Task card presentation (3-4 minutes)
5. **Part 3**: Abstract discussion (4-5 minutes)
6. **Assessment**: Scoring and feedback generation
7. **Results**: Band scores and improvement suggestions

### Example Conversation Flow
```
Agent: "Hello! I'm your IELTS speaking examiner. May I have your full name and age?"
Student: "My name is Sarah Johnson and I'm 22 years old."
Agent: [Uses save_student_info tool]

Agent: "Thank you Sarah. Let's begin Part 1. Tell me about your hometown..."
Student: [Responds with details about hometown]
Agent: [Continues with Part 1 questions]

Agent: "Now for Part 2, here's your task card..." [Uses get_task_card tool]
Student: [Prepares and speaks for 1-2 minutes]
Agent: [Uses conduct_speaking_assessment tool]

Agent: "Finally, Part 3. Let's discuss..." [Uses get_discussion_questions tool]
Student: [Engages in abstract discussion]

Agent: [Uses calculate_band_score and generate_improvement_suggestions tools]
Agent: [Uses save_assessment_results tool]
```

## 📁 File Structure

```
ai_tutor/
├── agent.py                 # Main agent definition
├── prompt.py                # IELTS examiner instructions
├── __init__.py              # Package initialization
├── README.md                # This documentation
├── tools/                   # Assessment and management tools
│   ├── __init__.py
│   ├── student_management.py    # Registration, data storage
│   └── ielts_assessment.py      # Scoring, feedback tools
└── student_data/            # JSON files for student records
    └── [student_files].json # Individual student assessments
```

## 📋 Student Data Format

Each student record is stored as a JSON file containing:

```json
{
  "personal_info": {
    "name": "Student Name",
    "age": 22,
    "registration_date": "2025-01-XX",
    "student_id": "unique_identifier"
  },
  "assessments": [
    {
      "assessment_date": "2025-01-XX",
      "assessment_type": "IELTS Speaking Test",
      "scores": {
        "overall_band": 6.5,
        "fluency_coherence": 6.0,
        "lexical_resource": 7.0,
        "grammatical_range_accuracy": 6.5,
        "pronunciation": 6.5
      },
      "evaluation": {
        "strengths": "Strong vocabulary usage...",
        "weaknesses": "Some hesitation in complex topics...",
        "improvement_suggestions": "Practice linking words...",
        "detailed_feedback": "Comprehensive assessment details..."
      }
    }
  ],
  "progress_history": [
    {
      "date": "2025-01-XX",
      "band_score": 6.5,
      "key_areas_improved": "Vocabulary",
      "areas_to_focus": "Fluency"
    }
  ]
}
```

## 🔧 Tools Available

### Student Management
- `save_student_info(name, age)` - Register new students
- `get_student_info()` - Retrieve current student details
- `save_assessment_results(...)` - Store complete assessment data
- `load_student_history(name)` - Find previous student records

### IELTS Assessment
- `conduct_speaking_assessment(part, responses)` - Analyze speaking performance
- `calculate_band_score()` - Generate detailed scoring breakdown
- `generate_improvement_suggestions()` - Create personalized study plans
- `get_task_card()` - Provide random Part 2 topics
- `get_discussion_questions(topic_type)` - Generate Part 3 questions

## 🎯 Scoring Algorithm

The agent uses a sophisticated scoring system that analyzes:
- **Response length** and appropriateness for each part
- **Vocabulary diversity** and lexical resource usage
- **Sentence complexity** and grammatical structures
- **Estimated pronunciation** quality (text-based analysis)

*Note: In a production environment, this would integrate with speech recognition and phonetic analysis systems for more accurate pronunciation scoring.*

## 📈 Improvement Suggestions

The agent provides:
- **Immediate feedback** after each assessment
- **Specific study recommendations** based on weak areas
- **Goal-oriented targets** for the next band level
- **Resource suggestions** for continued learning
- **Progress tracking** across multiple sessions

## 🔒 Data Security

- Student data is stored locally in JSON format
- Files are named with sanitized student names and timestamps
- No sensitive personal information beyond name and age is collected
- Assessment data includes only language proficiency metrics

## 🚀 Next Steps for Enhancement

Future improvements could include:
- **Audio integration** for real pronunciation analysis
- **Multi-language support** for non-English speaking students
- **Integration with learning management systems**
- **Advanced NLP** for more sophisticated language analysis
- **Video assessment** capabilities for body language analysis
- **Automated scheduling** for follow-up assessments

## 📞 Support

This AI Tutor agent provides comprehensive IELTS speaking assessment with professional-grade evaluation and personalized feedback to help students achieve their English proficiency goals.

---

*Built with Google ADK following best practices for conversational AI agents and educational assessment tools.* 