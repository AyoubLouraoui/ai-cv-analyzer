CAREER_PATHS = {
    "Data Analyst": {
        "skills": ["python", "sql", "excel", "power bi", "pandas", "data analysis"],
        "next_skills": ["Tableau", "Statistics", "Data Visualization", "Business Analysis"]
    },
    "Data Engineer": {
        "skills": ["python", "sql", "docker", "airflow", "kafka", "postgresql"],
        "next_skills": ["Apache Spark", "Hadoop", "dbt", "Cloud AWS", "Data Warehousing"]
    },
    "AI Engineer": {
        "skills": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "nlp"],
        "next_skills": ["Transformers", "LLMs", "RAG", "LangChain", "Vector Databases"]
    },
    "Machine Learning Engineer": {
        "skills": ["python", "machine learning", "scikit-learn", "pandas", "numpy", "docker"],
        "next_skills": ["MLflow", "MLOps", "FastAPI", "Model Deployment", "Kubernetes"]
    },
    "BI Developer": {
        "skills": ["sql", "power bi", "excel", "dashboard", "data analysis"],
        "next_skills": ["DAX", "Data Modeling", "ETL", "Power Query"]
    }
}


def predict_career_path(cv_skills):
    cv_skills_lower = [skill.lower() for skill in cv_skills]

    results = []

    for career, data in CAREER_PATHS.items():
        matched = []

        for skill in data["skills"]:
            if skill in cv_skills_lower:
                matched.append(skill)

        score = round((len(matched) / len(data["skills"])) * 100, 2)

        results.append({
            "career": career,
            "score": score,
            "matched_skills": matched,
            "next_skills": data["next_skills"]
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results