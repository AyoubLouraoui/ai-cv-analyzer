SKILLS = [
    "python", "java", "javascript", "react", "node.js",
    "sql", "mysql", "postgresql", "mongodb",
    "docker", "kubernetes", "linux", "git",
    "machine learning", "deep learning", "data analysis",
    "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "streamlit", "fastapi", "flask",
    "power bi", "excel", "airflow", "kafka"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill.title())

    return sorted(list(set(found_skills)))