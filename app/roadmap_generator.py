ROADMAPS = {
    "Data Analyst": [
        "Learn Excel advanced functions",
        "Learn SQL queries and joins",
        "Learn Python basics",
        "Learn Pandas and NumPy",
        "Learn Power BI dashboards",
        "Build 2 data analysis projects"
    ],
    "Data Engineer": [
        "Learn advanced Python",
        "Master SQL and databases",
        "Learn ETL pipelines",
        "Learn Apache Airflow",
        "Learn Kafka basics",
        "Learn Docker",
        "Build a data pipeline project"
    ],
    "AI Engineer": [
        "Learn Python for AI",
        "Learn machine learning basics",
        "Learn deep learning",
        "Learn NLP",
        "Learn Transformers",
        "Learn RAG and vector databases",
        "Deploy an AI application"
    ],
    "Machine Learning Engineer": [
        "Learn scikit-learn",
        "Learn model evaluation",
        "Learn feature engineering",
        "Learn MLflow",
        "Learn FastAPI deployment",
        "Learn Docker",
        "Deploy ML model online"
    ],
    "BI Developer": [
        "Learn SQL",
        "Learn Power BI",
        "Learn DAX",
        "Learn Power Query",
        "Learn data modeling",
        "Build BI dashboards"
    ]
}


def generate_roadmap(best_career):
    return ROADMAPS.get(best_career, [
        "Improve your technical skills",
        "Build practical projects",
        "Create a strong GitHub portfolio",
        "Deploy your projects online"
    ])