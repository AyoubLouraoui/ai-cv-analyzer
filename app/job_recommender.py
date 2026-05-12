JOBS = {
    # =========================
    # AI & DATA
    # =========================

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
        "python", "artificial intelligence", "machine learning", "deep learning", "pytorch", "tensorflow", "nlp"
    ],
    "Business Intelligence Analyst": [
        "sql", "excel", "power bi", "data analysis", "dashboard"
    ],
    "BI Developer": [
        "sql", "power bi", "dax", "power query", "data modeling", "dashboard"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "scikit-learn", "pytorch", "docker"
    ],

    # =========================
    # SOFTWARE
    # =========================

    "Software Engineer": [
        "programming", "algorithms", "data structures", "git", "github", "software architecture"
    ],
    "Full Stack Developer": [
        "html", "css", "javascript", "react", "node.js", "mongodb", "postgresql"
    ],
    "Backend Developer": [
        "python", "node.js", "fastapi", "django", "api", "authentication", "postgresql", "docker"
    ],
    "Python Developer": [
        "python", "fastapi", "flask", "sql", "git"
    ],

    # =========================
    # CLOUD & CYBER
    # =========================

    "Cloud Engineer": [
        "linux", "aws", "docker", "kubernetes", "terraform", "ci/cd"
    ],
    "Cloud / DevOps Junior": [
        "docker", "kubernetes", "linux", "git", "ci/cd"
    ],
    "Cybersecurity Engineer": [
        "networking", "linux", "security", "ethical hacking", "siem", "penetration testing"
    ],
    "Network Engineer": [
        "tcp/ip", "cisco", "routing", "switching", "vlan", "subnetting", "firewall"
    ],

    # =========================
    # GENIE CIVIL
    # =========================

    "Civil Engineering": [
        "autocad", "structural analysis", "construction management", "revit", "bim", "sap2000", "etabs"
    ],
    "Structural Engineer": [
        "structural analysis", "sap2000", "etabs", "seismic design", "bim", "autocad"
    ],

    # =========================
    # GENIE INDUSTRIEL
    # =========================

    "Industrial Engineering": [
        "process optimization", "lean manufacturing", "quality management", "supply chain", "six sigma"
    ],
    "Process Engineer": [
        "process optimization", "production systems", "industrial automation", "lean six sigma", "manufacturing"
    ],

    # =========================
    # GENIE ELECTRIQUE
    # =========================

    "Electrical Engineering": [
        "electrical circuits", "industrial automation", "plc", "scada", "embedded systems", "electronics"
    ],
    "Automation Engineer": [
        "plc", "scada", "industrial communication", "robotics", "iot", "automation"
    ],

    # =========================
    # GENIE MECANIQUE
    # =========================

    "Mechanical Engineering": [
        "mechanical design", "solidworks", "autocad", "thermodynamics", "industrial maintenance", "mechanics"
    ],
    "Maintenance Engineer": [
        "industrial maintenance", "diagnostics", "predictive maintenance", "industrial systems", "automation"
    ],

    # =========================
    # TELECOM
    # =========================

    "Telecommunications Engineer": [
        "networking", "rf", "fiber optics", "lte", "5g", "telecom infrastructure"
    ],

    # =========================
    # BUSINESS
    # =========================

    "Business Analyst": [
        "business analysis", "excel", "sql", "reporting", "power bi", "agile", "scrum"
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

        if matched:
            results.append({
                "job": job,
                "score": score,
                "matched_skills": matched,
                "missing_skills": missing
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results
