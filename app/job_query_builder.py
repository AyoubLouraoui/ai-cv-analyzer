def build_job_queries(cv_skills, best_career):
    skills = [s.lower() for s in cv_skills]

    queries = []

    if any(s in skills for s in ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp"]):
        queries += [
            "AI Engineer",
            "Machine Learning Engineer",
            "Data Scientist",
            "NLP Engineer"
        ]

    if any(s in skills for s in ["python", "sql", "pandas", "numpy", "data analysis", "power bi"]):
        queries += [
            "Data Analyst",
            "Data Scientist",
            "Business Intelligence Analyst"
        ]

    if any(s in skills for s in ["kafka", "airflow", "spark", "docker", "postgresql"]):
        queries += [
            "Data Engineer",
            "ETL Developer",
            "Big Data Engineer"
        ]

    if not queries:
        queries = [best_career]

    return list(dict.fromkeys(queries))