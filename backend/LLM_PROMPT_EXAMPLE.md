# IELTS Test Result JSON Structure for LLM Models

## Overview
This document provides the exact JSON structure that should be used when generating IELTS Speaking test results. This format is critical for data consistency and integration with the AI IELTS Examiner system.

## Required JSON Structure

```json
{
  "answers": {
    "Part 1": {
      "questions": ["question1", "question2", "question3", "question4"],
      "responses": ["response1", "response2", "response3", "response4"]
    },
    "Part 2": {
      "topic": "Describe [specific topic prompt]",
      "response": "[Extended 1-2 minute response]"
    },
    "Part 3": {
      "questions": ["abstract_question1", "analytical_question2", "opinion_question3"],
      "responses": ["analytical_response1", "detailed_response2", "opinion_response3"]
    }
  },
  "feedback": {
    "fluency": "[Detailed assessment of speech flow and delivery]",
    "grammar": "[Assessment of grammatical accuracy and complexity]", 
    "vocabulary": "[Evaluation of word choice and range]",
    "pronunciation": "[Assessment of clarity and intelligibility]"
  },
  "strengths": [
    "[Specific strength 1]",
    "[Specific strength 2]",
    "[Specific strength 3]"
  ],
  "band_score": 6.5,
  "improvements": [
    "[Actionable improvement 1]",
    "[Actionable improvement 2]"
  ],
  "detailed_scores": {
    "fluency": 6,
    "grammar": 6,
    "vocabulary": 7,
    "pronunciation": 7
  }
}
```

## Field Requirements

### Required Fields (Must be present)
- `answers` (object)
- `feedback` (object) 
- `band_score` (number, 0-9 scale, increments of 0.5)

### Strongly Recommended Fields
- `strengths` (array of strings)
- `improvements` (array of strings)
- `detailed_scores` (object with numerical scores)

### Field Specifications

#### `answers.Part 1`
- **questions**: Array of 4-7 general questions about familiar topics
- **responses**: Array of corresponding responses (should match questions length)

#### `answers.Part 2`  
- **topic**: String describing the 2-minute talk prompt
- **response**: String containing the extended response (1-2 minutes worth of speech)

#### `answers.Part 3`
- **questions**: Array of 3-5 abstract/analytical questions related to Part 2 topic
- **responses**: Array of corresponding detailed responses

#### `feedback`
- **fluency**: String describing speech flow, pace, hesitation patterns
- **grammar**: String evaluating grammatical accuracy and complexity
- **vocabulary**: String assessing word choice, range, and appropriateness  
- **pronunciation**: String evaluating clarity, intonation, and intelligibility

#### `band_score`
- Number between 0-9 (IELTS scale)
- Use increments of 0.5 (e.g., 5.5, 6.0, 6.5, 7.0)
- Should reflect overall speaking proficiency

#### `detailed_scores`
- **fluency**: Integer score 0-9 for fluency and coherence
- **grammar**: Integer score 0-9 for grammatical range and accuracy
- **vocabulary**: Integer score 0-9 for lexical resource
- **pronunciation**: Integer score 0-9 for pronunciation

#### `strengths`
- Array of 2-4 specific positive aspects
- Should be actionable and specific
- Examples: "Clear pronunciation", "Good vocabulary range", "Natural conversation flow"

#### `improvements`
- Array of 1-3 specific areas for development
- Should include actionable advice
- Examples: "Use more complex sentence structures", "Reduce hesitation in responses"

## Data Type Validation

```javascript
{
  answers: {
    "Part 1": {
      questions: string[],    // Array of strings
      responses: string[]     // Array of strings, same length as questions
    },
    "Part 2": {
      topic: string,          // Single string
      response: string        // Single string
    },
    "Part 3": {
      questions: string[],    // Array of strings  
      responses: string[]     // Array of strings, same length as questions
    }
  },
  feedback: {
    fluency: string,          // Descriptive text
    grammar: string,          // Descriptive text
    vocabulary: string,       // Descriptive text
    pronunciation: string     // Descriptive text
  },
  strengths: string[],        // Array of strings
  band_score: number,         // Float 0-9, increments of 0.5
  improvements: string[],     // Array of strings
  detailed_scores: {
    fluency: number,          // Integer 0-9
    grammar: number,          // Integer 0-9
    vocabulary: number,       // Integer 0-9
    pronunciation: number     // Integer 0-9
  }
}
```

## LLM Prompt Example

```
You are an IELTS Speaking examiner. Based on the student's responses, generate a comprehensive assessment in the following JSON format:

[Include the complete JSON structure here]

Requirements:
1. Provide detailed, constructive feedback in each category
2. Ensure band_score reflects the detailed_scores average
3. Give 2-4 specific strengths and 1-3 actionable improvements
4. Use professional, encouraging language
5. Follow IELTS Speaking assessment criteria strictly

Student responses: [insert actual responses here]
```

## Common Mistakes to Avoid

1. **Missing required fields**: Always include answers, feedback, and band_score
2. **Inconsistent array lengths**: questions and responses arrays must match
3. **Invalid band scores**: Use only 0-9 scale with 0.5 increments
4. **Generic feedback**: Provide specific, actionable comments
5. **Mismatched scores**: detailed_scores should align with overall band_score

## Integration Notes

- This JSON will be processed by `save_test_result_to_json()` function
- Additional metadata (test_date, test_number) will be added automatically
- Ensure all strings are properly escaped for JSON validity
- Test data will be stored in Supabase PostgreSQL database 