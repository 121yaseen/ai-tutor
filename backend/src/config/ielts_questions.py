IELTS_QUESTIONS = {
    "part1": {
        "basic": [
            "where are you from?",
            "Do you work or study?",
            "What do you like to do in your free time?",
            "Tell me about your hometown.",
            "What kind of music do you like?",
            "Do you prefer to stay at home or go out in the evening?",
        ],
        "intermediate": [
            "How has your hometown changed in recent years?",
            "What are the advantages and disadvantages of your job/studies?",
            "How do you think technology has changed the way people spend their free time?",
            "What role does music play in your culture?",
            "How do you think people's social habits have changed over the years?",
        ],
        "advanced": [
            "In what ways do you think your hometown could be improved?",
            "How do you think the job market will change in the future?",
            "Do you think people today have more or less free time than in the past? Why?",
            "How important is preserving traditional music in your country?",
            "What impact do you think social media has had on genuine human connections?",
        ]
    },
    "part2": {
        "basic": [
            "Describe a person who is important to you. You should say: who this person is, how you know them, what they are like, and explain why they are important to you.",
            "Describe a place you like to visit. You should say: where it is, when you go there, what you do there, and explain why you like this place.",
            "Describe something you bought recently. You should say: what it was, where you bought it, why you bought it, and explain how you felt about this purchase.",
        ],
        "intermediate": [
            "Describe a memorable journey you have taken. You should say: where you went, who you went with, what happened during the journey, and explain why it was memorable.",
            "Describe a skill you would like to learn. You should say: what the skill is, why you want to learn it, how you would learn it, and explain how this skill would benefit you.",
            "Describe an interesting tradition in your country. You should say: what the tradition is, when it happens, how people celebrate it, and explain why you find it interesting.",
        ],
        "advanced": [
            "Describe a time when you had to make a difficult decision. You should say: what the decision was, what options you had, how you made the decision, and explain what you learned from this experience.",
            "Describe a global issue that concerns you. You should say: what the issue is, how it affects people, what causes this issue, and explain what you think should be done about it.",
            "Describe a technological advancement that has changed people's lives. You should say: what the advancement is, how it has changed lives, what the positive and negative effects are, and explain your opinion about this change.",
        ]
    },
    "part3": {
        "basic": [
            "What are the benefits of having good friends?",
            "How do people in your country usually spend their weekends?",
            "What are some popular hobbies in your country?",
            "Do you think it's important for children to play sports? Why?",
        ],
        "intermediate": [
            "How do you think social relationships have changed with technology?",
            "What role should the government play in people's leisure activities?",
            "How do you think people's hobbies reflect their personality?",
            "What are the advantages and disadvantages of competitive sports?",
        ],
        "advanced": [
            "In what ways might artificial intelligence change human relationships in the future?",
            "Should governments invest more in sports facilities or cultural institutions? Why?",
            "How do you think the concept of work-life balance will evolve in the coming decades?",
            "What ethical considerations should be taken into account when developing new technologies?",
        ]
    }
}

# Band score to difficulty mapping for adaptive questioning
DIFFICULTY_MAPPING = {
    "beginner": {"range": [0, 4.5], "questions": "basic"},
    "intermediate": {"range": [5.0, 6.5], "questions": "intermediate"},  
    "advanced": {"range": [7.0, 9.0], "questions": "advanced"}
}

# Evaluation criteria and descriptors
BAND_DESCRIPTORS = {
    "fluency_coherence": {
        9: "Speaks fluently with only rare repetition or self-correction. Develops topics coherently and appropriately.",
        7: "Speaks at length without noticeable effort. May occasionally repeat, self-correct or hesitate. Uses connectives appropriately.",
        5: "Usually maintains flow of speech but uses repetition, self-correction and/or slow speech. Over-uses certain connectives and discourse markers.",
        3: "Speaks with long pauses. Limited ability to link simple sentences. Frequent repetition and self-correction."
    },
    "lexical_resource": {
        9: "Uses vocabulary with full flexibility and precise usage. Uses idiomatic language naturally and accurately.",
        7: "Uses vocabulary resource flexibly to discuss topics at length. Uses some less common and idiomatic items with awareness of style and collocation.",
        5: "Manages to talk about familiar and unfamiliar topics but uses vocabulary with limited flexibility. Attempts paraphrase but not always successfully.",
        3: "Uses simple vocabulary to convey personal information. Has insufficient vocabulary for less familiar topics."
    },
    "grammatical_accuracy": {
        9: "Uses a wide range of structures with full flexibility and accuracy. Rare minor errors occur only as 'slips'.",
        7: "Uses a range of complex structures with some flexibility. May make frequent mistakes with complex structures, though these rarely cause comprehension problems.",
        5: "Uses basic sentence forms with reasonable accuracy. Uses limited range of more complex structures, but these usually contain errors.",
        3: "Attempts basic sentence forms but with limited success, or relies on apparently memorized utterances. Makes numerous errors except in memorized expressions."
    },
    "pronunciation": {
        9: "Uses wide range of pronunciation features. Sustained flexible use of features with only occasional lapses. Easy to understand.",
        7: "Shows all positive features of Band 6 and some, but not all, positive features of Band 8. Generally easy to understand, with occasional mispronunciation.",
        5: "Shows positive features of Band 4 and some features of Band 6. Generally intelligible throughout, though mispronunciation reduces clarity at times.",
        3: "Shows some of the positive features of Band 2 and some features of Band 4. Frequently intelligible, though mispronunciation and inappropriate intonation sometimes impede understanding."
    }
} 