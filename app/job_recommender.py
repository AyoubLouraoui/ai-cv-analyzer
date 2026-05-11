JOBS = {
    "Data Analyst": [
        "python", "sql", "excel", "power bi", "pandas", "data analysis"
    ],
    "Data Scientist": [
        "python", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn"
    ],
    "Data Engineer": [
        "python", "sql", "airflow", "kafka", "docker", "postgresql"
    ],
    "AI Engineer": [
        "python", "machine learning", "deep learning", "pytorch", "tensorflow", "nlp"
    ],
    "Business Intelligence Analyst": [
        "sql", "excel", "power bi", "data analysis", "dashboard"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "scikit-learn", "pytorch", "docker"
    ],
    "Python Developer": [
        "python", "fastapi", "flask", "sql", "git"
    ],
    "Cloud / DevOps Junior": [
        "docker", "kubernetes", "linux", "git", "ci/cd"
    ]
}

def recommend_jobs(cv_skills):
    results = []

    cv_skills_lower = [skill.lower() for skill in cv_skills]

    for job, required_skills in JOBS.items():
        matched = []
        missing = []

        for skill in required_skills:
            if skill in cv_skills_lower:
                matched.append(skill)
            else:
                missing.append(skill)

        score = round((len(matched) / len(required_skills)) * 100, 2)

        results.append({
            "job": job,
            "score": score,
            "matched_skills": matched,
            "missing_skills": missing
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results