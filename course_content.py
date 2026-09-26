"""
10-Week Recovery Course Content Structure
Evidence-based digital intervention for depression and anxiety
"""

COURSE_STRUCTURE = {
    "week_1": {
        "week_number": 1,
        "title": "Understanding Your Mind - Part 1",
        "pillar": "Psychoeducation",
        "description": "Learn what depression and anxiety really are, and why understanding them is the first step to recovery.",
        "objectives": [
            "Understand the biological and psychological nature of depression",
            "Recognize common symptoms and patterns",
            "Reduce self-stigma and build hope",
            "Learn the Cognitive Model basics"
        ],
        "modules": [
            {
                "id": "week1_module1",
                "title": "What is Depression?",
                "duration": "15 min",
                "type": "video_text",
                "content": {
                    "intro": "Depression is not a personal failure or weakness. It's a medical condition that affects how you think, feel, and function.",
                    "key_points": [
                        "Depression affects 1 in 5 people at some point in their lives",
                        "It's caused by a combination of biological, psychological, and social factors",
                        "It's treatable - recovery is possible",
                        "Understanding it is the first step to healing"
                    ],
                    "symptoms": [
                        "Persistent sad or empty mood",
                        "Loss of interest in activities",
                        "Changes in sleep or appetite",
                        "Fatigue and low energy",
                        "Difficulty concentrating",
                        "Feelings of worthlessness",
                        "Thoughts of death or suicide"
                    ]
                },
                "quiz": [
                    {
                        "question": "Depression is primarily caused by:",
                        "options": [
                            "Personal weakness",
                            "A combination of biological, psychological, and social factors",
                            "Bad luck",
                            "Lack of willpower"
                        ],
                        "correct": 1
                    }
                ]
            },
            {
                "id": "week1_module2",
                "title": "What is Anxiety?",
                "duration": "15 min",
                "type": "video_text",
                "content": {
                    "intro": "Anxiety is your body's natural alarm system. When it becomes too sensitive, it can interfere with daily life.",
                    "key_points": [
                        "Anxiety is the body's fight-or-flight response",
                        "It becomes a problem when it's excessive or persistent",
                        "Physical symptoms are real and can be managed",
                        "You can learn to calm your nervous system"
                    ],
                    "symptoms": [
                        "Excessive worry",
                        "Restlessness or feeling on edge",
                        "Rapid heartbeat",
                        "Shortness of breath",
                        "Muscle tension",
                        "Difficulty sleeping",
                        "Panic attacks"
                    ]
                }
            },
            {
                "id": "week1_module3",
                "title": "The Cognitive Model",
                "duration": "20 min",
                "type": "interactive",
                "content": {
                    "intro": "Your feelings are not caused by situations themselves, but by how you interpret them.",
                    "model": "Situation → Thought → Feeling → Behavior",
                    "example": {
                        "situation": "Friend doesn't call back",
                        "thought_negative": "They hate me",
                        "feeling_negative": "Sad, rejected",
                        "thought_balanced": "They might be busy",
                        "feeling_balanced": "Neutral, patient"
                    },
                    "key_insight": "By changing how we think, we can change how we feel."
                }
            }
        ],
        "homework": [
            "Complete PHQ-9 and GAD-7 assessments",
            "Write down 3 symptoms you experience most",
            "Identify one situation where your thoughts affected your mood"
        ]
    },
    
    "week_2": {
        "week_number": 2,
        "title": "Understanding Your Mind - Part 2",
        "pillar": "Psychoeducation",
        "description": "Deepen your understanding and build hope for recovery.",
        "objectives": [
            "Understand the cycle of depression and anxiety",
            "Learn about treatment options",
            "Build realistic hope for recovery",
            "Prepare for active treatment"
        ],
        "modules": [
            {
                "id": "week2_module1",
                "title": "The Downward Spiral",
                "duration": "15 min",
                "type": "video_text",
                "content": {
                    "intro": "Depression and anxiety create self-reinforcing cycles. Understanding these cycles helps you break them.",
                    "depression_cycle": "Low mood → Inactivity → More low mood → More inactivity",
                    "anxiety_cycle": "Worry → Avoidance → More worry → More avoidance",
                    "key_insight": "Breaking the cycle at any point can start an upward spiral."
                }
            },
            {
                "id": "week2_module2",
                "title": "Hope for Recovery",
                "duration": "15 min",
                "type": "video_text",
                "content": {
                    "intro": "Recovery is not only possible - it's probable with the right tools and support.",
                    "statistics": [
                        "70-80% of people respond well to treatment",
                        "Self-help tools can be as effective as therapy for mild-moderate cases",
                        "Most people see improvement within 6-12 weeks",
                        "Skills learned prevent future episodes"
                    ],
                    "success_stories": "Many people who complete this course report significant improvement in mood and functioning."
                }
            }
        ],
        "homework": [
            "Retake PHQ-9 and GAD-7 to track baseline",
            "Write a letter to your future self about why you want to recover",
            "List 3 things you used to enjoy that you want to do again"
        ]
    },
    
    "week_3": {
        "week_number": 3,
        "title": "Taking Action - Behavioral Activation Part 1",
        "pillar": "Behavioral Activation",
        "description": "Learn how action creates motivation, not the other way around.",
        "objectives": [
            "Understand the principle of 'motivation follows action'",
            "Start monitoring your daily activities",
            "Identify the link between activity and mood",
            "Begin breaking the inactivity cycle"
        ],
        "modules": [
            {
                "id": "week3_module1",
                "title": "Action as Medicine",
                "duration": "20 min",
                "type": "video_text",
                "content": {
                    "intro": "When depressed, we wait to feel motivated before acting. But it works the opposite way: action creates motivation.",
                    "key_principle": "Motivation follows action, not the other way around",
                    "science": "Activity releases dopamine and serotonin, improving mood naturally",
                    "examples": [
                        "Taking a 5-minute walk → Feeling slightly better → Walking more",
                        "Calling a friend → Feeling connected → Reaching out more",
                        "Cleaning one corner → Feeling accomplished → Cleaning more"
                    ]
                }
            },
            {
                "id": "week3_module2",
                "title": "Activity Monitoring",
                "duration": "30 min",
                "type": "interactive_tool",
                "content": {
                    "intro": "For one week, track what you do each hour and rate your mood 0-10.",
                    "instructions": [
                        "Record activities hourly (or as close as possible)",
                        "Rate mood 0-10 (0=worst, 10=best)",
                        "Note which activities improve or worsen mood",
                        "Look for patterns"
                    ],
                    "tool": "activity_tracker"
                }
            }
        ],
        "homework": [
            "Use Activity Tracker daily for 7 days",
            "Identify 3 activities that improve your mood",
            "Try one small activity you've been avoiding"
        ]
    },
    
    "week_4": {
        "week_number": 4,
        "title": "Building Momentum - Behavioral Activation Part 2",
        "pillar": "Behavioral Activation",
        "description": "Create your personalized activity plan and build upward spirals.",
        "objectives": [
            "Identify your core values",
            "Schedule meaningful activities",
            "Use graded task assignment",
            "Build sustainable routines"
        ],
        "modules": [
            {
                "id": "week4_module1",
                "title": "Values and Meaningful Activity",
                "duration": "25 min",
                "type": "interactive",
                "content": {
                    "intro": "Not all activities are equal. Activities aligned with your values are most powerful.",
                    "value_categories": [
                        "Relationships (family, friends, community)",
                        "Health (physical, mental, spiritual)",
                        "Work/Education (career, learning, growth)",
                        "Leisure (hobbies, creativity, fun)",
                        "Contribution (helping others, making a difference)"
                    ],
                    "exercise": "Identify your top 3 values and one activity for each"
                }
            },
            {
                "id": "week4_module2",
                "title": "Graded Task Assignment",
                "duration": "20 min",
                "type": "video_text",
                "content": {
                    "intro": "Break overwhelming tasks into tiny, manageable steps.",
                    "principle": "Start so small you can't fail",
                    "examples": [
                        {
                            "task": "Exercise",
                            "steps": ["Put on shoes", "Walk to door", "Walk 2 minutes", "Walk 5 minutes", "Walk 10 minutes"]
                        },
                        {
                            "task": "Social connection",
                            "steps": ["Send one text", "Have 5-min call", "Meet for coffee", "Attend group activity"]
                        }
                    ]
                }
            }
        ],
        "homework": [
            "Create activity schedule for next week",
            "Complete at least 3 scheduled activities",
            "Practice one graded task"
        ]
    }
}

# Additional weeks 5-10 structure (abbreviated for space)
COURSE_STRUCTURE.update({
    "week_5": {
        "week_number": 5,
        "title": "Challenging Negative Thoughts - Part 1",
        "pillar": "Cognitive Restructuring",
        "description": "Learn to identify and challenge thought traps.",
        "modules": [
            {"id": "week5_module1", "title": "Identifying Cognitive Distortions", "duration": "20 min"},
            {"id": "week5_module2", "title": "The Thought Record", "duration": "30 min", "tool": "thought_record"}
        ]
    },
    "week_6": {
        "week_number": 6,
        "title": "Challenging Negative Thoughts - Part 2",
        "pillar": "Cognitive Restructuring",
        "description": "Develop balanced thinking patterns.",
        "modules": [
            {"id": "week6_module1", "title": "Evidence Gathering", "duration": "25 min"},
            {"id": "week6_module2", "title": "Core Beliefs", "duration": "20 min"}
        ]
    },
    "week_7": {
        "week_number": 7,
        "title": "Calming Your Body - Part 1",
        "pillar": "Somatic Regulation",
        "description": "Learn to activate your body's natural relaxation response.",
        "modules": [
            {"id": "week7_module1", "title": "Understanding Fight-or-Flight", "duration": "15 min"},
            {"id": "week7_module2", "title": "Breathing Techniques", "duration": "25 min", "tool": "breathing_exercises"}
        ]
    },
    "week_8": {
        "week_number": 8,
        "title": "Calming Your Body - Part 2",
        "pillar": "Somatic Regulation",
        "description": "Master mindfulness and body awareness.",
        "modules": [
            {"id": "week8_module1", "title": "Progressive Muscle Relaxation", "duration": "20 min"},
            {"id": "week8_module2", "title": "Mindfulness Body Scan", "duration": "25 min"}
        ]
    },
    "week_9": {
        "week_number": 9,
        "title": "Lifestyle as Medicine - Part 1",
        "pillar": "Lifestyle Medicine",
        "description": "Optimize sleep, nutrition, and exercise for mental health.",
        "modules": [
            {"id": "week9_module1", "title": "Sleep Hygiene", "duration": "20 min"},
            {"id": "week9_module2", "title": "Nutrition for Mental Health", "duration": "20 min"}
        ]
    },
    "week_10": {
        "week_number": 10,
        "title": "Lifestyle as Medicine - Part 2",
        "pillar": "Lifestyle Medicine",
        "description": "Build sustainable habits for long-term wellness.",
        "modules": [
            {"id": "week10_module1", "title": "Exercise as Medicine", "duration": "20 min"},
            {"id": "week10_module2", "title": "Relapse Prevention", "duration": "25 min"}
        ]
    }
})

# Pillar colors for UI
PILLAR_COLORS = {
    "Psychoeducation": {"bg": "purple", "text": "purple-900"},
    "Behavioral Activation": {"bg": "green", "text": "green-900"},
    "Cognitive Restructuring": {"bg": "blue", "text": "blue-900"},
    "Somatic Regulation": {"bg": "teal", "text": "teal-900"},
    "Lifestyle Medicine": {"bg": "orange", "text": "orange-900"}
}
