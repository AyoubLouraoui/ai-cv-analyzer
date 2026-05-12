CAREER_PATHS = {

    # =========================
    # AI & DATA
    # =========================

    "Data Analyst": {
        "skills": [
            "python",
            "sql",
            "excel",
            "power bi",
            "pandas",
            "data analysis"
        ],
        "next_skills": [
            "Tableau",
            "Statistics",
            "Data Visualization",
            "Business Analysis"
        ]
    },

    "Data Engineer": {
        "skills": [
            "python",
            "sql",
            "docker",
            "airflow",
            "kafka",
            "postgresql"
        ],
        "next_skills": [
            "Apache Spark",
            "Hadoop",
            "dbt",
            "Cloud AWS",
            "Data Warehousing"
        ]
    },

    "AI Engineer": {
        "skills": [
            "python",
            "machine learning",
            "deep learning",
            "pytorch",
            "tensorflow",
            "nlp"
        ],
        "next_skills": [
            "Transformers",
            "LLMs",
            "RAG",
            "LangChain",
            "Vector Databases"
        ]
    },

    "Machine Learning Engineer": {
        "skills": [
            "python",
            "machine learning",
            "scikit-learn",
            "pandas",
            "numpy",
            "docker"
        ],
        "next_skills": [
            "MLflow",
            "MLOps",
            "FastAPI",
            "Model Deployment",
            "Kubernetes"
        ]
    },

    "BI Developer": {
        "skills": [
            "sql",
            "power bi",
            "excel",
            "dashboard",
            "data analysis"
        ],
        "next_skills": [
            "DAX",
            "Data Modeling",
            "ETL",
            "Power Query"
        ]
    },

    # =========================
    # SOFTWARE
    # =========================

    "Software Engineer": {
        "skills": [
            "java",
            "python",
            "c++",
            "oop",
            "git",
            "algorithms"
        ],
        "next_skills": [
            "System Design",
            "Microservices",
            "Clean Architecture",
            "CI/CD"
        ]
    },

    "Full Stack Developer": {
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "node.js",
            "mongodb"
        ],
        "next_skills": [
            "Next.js",
            "TypeScript",
            "Docker",
            "Authentication"
        ]
    },

    "Backend Developer": {
        "skills": [
            "python",
            "fastapi",
            "django",
            "sql",
            "api",
            "postgresql"
        ],
        "next_skills": [
            "Redis",
            "Microservices",
            "Kubernetes",
            "Cloud Computing"
        ]
    },

    # =========================
    # CLOUD & CYBER
    # =========================

    "Cloud Engineer": {
        "skills": [
            "aws",
            "docker",
            "linux",
            "kubernetes",
            "terraform",
            "devops"
        ],
        "next_skills": [
            "Azure",
            "GCP",
            "CI/CD",
            "Monitoring"
        ]
    },

    "Cybersecurity Engineer": {
        "skills": [
            "networking",
            "linux",
            "security",
            "firewall",
            "wireshark",
            "python"
        ],
        "next_skills": [
            "Penetration Testing",
            "SIEM",
            "SOC",
            "Malware Analysis"
        ]
    },

    "Network Engineer": {
        "skills": [
            "cisco",
            "routing",
            "switching",
            "tcp/ip",
            "vlan",
            "networking"
        ],
        "next_skills": [
            "CCNP",
            "SDN",
            "Network Automation",
            "Firewall Administration"
        ]
    },

    # =========================
    # GENIE CIVIL
    # =========================

    "Civil Engineering": {
        "skills": [
            "autocad",
            "construction",
            "civil engineering",
            "revit",
            "site management",
            "structural analysis"
        ],
        "next_skills": [
            "BIM",
            "Project Planning",
            "SAP2000",
            "ETABS"
        ]
    },

    "Structural Engineer": {
        "skills": [
            "sap2000",
            "etabs",
            "autocad",
            "structural analysis",
            "civil engineering"
        ],
        "next_skills": [
            "Advanced Structural Design",
            "BIM",
            "Seismic Analysis"
        ]
    },

    # =========================
    # GENIE INDUSTRIEL
    # =========================

    "Industrial Engineering": {
        "skills": [
            "lean manufacturing",
            "quality control",
            "production",
            "supply chain",
            "industrial engineering"
        ],
        "next_skills": [
            "Six Sigma",
            "ERP",
            "Project Management",
            "Operations Research"
        ]
    },

    "Process Engineer": {
        "skills": [
            "process optimization",
            "production",
            "quality",
            "industrial engineering"
        ],
        "next_skills": [
            "Lean Six Sigma",
            "Automation",
            "Data Analytics"
        ]
    },

    # =========================
    # GENIE ELECTRIQUE
    # =========================

    "Electrical Engineering": {
        "skills": [
            "electrical engineering",
            "automation",
            "plc",
            "electronics",
            "electrical circuits"
        ],
        "next_skills": [
            "SCADA",
            "Industrial Automation",
            "Embedded Systems"
        ]
    },

    "Automation Engineer": {
        "skills": [
            "plc",
            "scada",
            "automation",
            "industrial systems"
        ],
        "next_skills": [
            "IoT",
            "Robotics",
            "Industrial AI"
        ]
    },

    # =========================
    # GENIE MECANIQUE
    # =========================

    "Mechanical Engineering": {
        "skills": [
            "mechanical engineering",
            "solidworks",
            "autocad",
            "maintenance",
            "mechanics"
        ],
        "next_skills": [
            "CAE",
            "CFD",
            "Industrial Maintenance"
        ]
    },

    "Maintenance Engineer": {
        "skills": [
            "maintenance",
            "diagnostics",
            "mechanics",
            "industrial systems"
        ],
        "next_skills": [
            "Predictive Maintenance",
            "IoT",
            "Industrial Automation"
        ]
    },

    # =========================
    # TELECOM
    # =========================

    "Telecommunications Engineer": {
        "skills": [
            "telecom",
            "fiber optics",
            "5g",
            "networking",
            "rf"
        ],
        "next_skills": [
            "LTE",
            "Network Optimization",
            "Cloud Networking"
        ]
    },

    # =========================
    # BUSINESS
    # =========================

    "Business Analyst": {
        "skills": [
            "excel",
            "sql",
            "business analysis",
            "power bi",
            "reporting"
        ],
        "next_skills": [
            "Agile",
            "Scrum",
            "Project Management"
        ]
    }
}


def predict_career_path(cv_skills):

    cv_skills_lower = [skill.lower() for skill in cv_skills]

    results = []

    for career, data in CAREER_PATHS.items():

        matched = []

        for skill in data["skills"]:

            if skill.lower() in cv_skills_lower:
                matched.append(skill)

        score = round(
            (len(matched) / len(data["skills"])) * 100,
            2
        )

        results.append({
            "career": career,
            "score": score,
            "matched_skills": matched,
            "next_skills": data["next_skills"]
        })

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results