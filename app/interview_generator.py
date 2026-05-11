QUESTIONS_BANK = {
    "Python": [
        "What are Python lists and tuples?",
        "Explain the difference between a function and a method in Python.",
        "How do you handle errors in Python?"
    ],
    "Sql": [
        "What is the difference between WHERE and HAVING?",
        "Explain INNER JOIN and LEFT JOIN.",
        "What is a primary key?"
    ],
    "Docker": [
        "What is Docker?",
        "What is the difference between an image and a container?",
        "Why do we use Docker in deployment?"
    ],
    "Machine Learning": [
        "What is supervised learning?",
        "What is overfitting?",
        "Explain train/test split."
    ],
    "Data Analysis": [
        "How do you clean missing data?",
        "What is data visualization?",
        "How do you detect outliers?"
    ],
    "Power Bi": [
        "What is Power BI?",
        "What is DAX?",
        "How do you create a dashboard?"
    ],
    "Fastapi": [
        "What is FastAPI?",
        "How do you create an API endpoint?",
        "What is Swagger documentation?"
    ],
    "Git": [
        "What is Git?",
        "What is the difference between git pull and git fetch?",
        "How do you resolve merge conflicts?"
    ]
}


def generate_interview_questions(cv_skills):
    questions = {}

    for skill in cv_skills:
        if skill in QUESTIONS_BANK:
            questions[skill] = QUESTIONS_BANK[skill]

    return questions