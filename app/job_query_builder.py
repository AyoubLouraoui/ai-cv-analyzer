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

    if any(s in skills for s in ["javascript", "react", "node.js", "html", "css", "django", "fastapi"]):
        queries += [
            "Software Engineer",
            "Full Stack Developer",
            "Backend Developer"
        ]

    if any(s in skills for s in ["aws", "docker", "kubernetes", "linux", "terraform", "devops"]):
        queries += [
            "Cloud Engineer",
            "DevOps Engineer",
            "Cloud Infrastructure Engineer"
        ]

    if any(s in skills for s in ["networking", "security", "firewall", "siem", "penetration testing"]):
        queries += [
            "Cybersecurity Engineer",
            "Network Security Engineer",
            "SOC Analyst"
        ]

    if any(s in skills for s in ["cisco", "routing", "switching", "tcp/ip", "vlan"]):
        queries += [
            "Network Engineer",
            "System Network Engineer",
            "Cisco Network Engineer"
        ]

    if any(s in skills for s in ["civil engineering", "autocad", "revit", "bim", "structural analysis"]):
        queries += [
            "Civil Engineer",
            "Structural Engineer",
            "BIM Engineer"
        ]

    if any(s in skills for s in ["industrial engineering", "lean manufacturing", "quality management", "supply chain"]):
        queries += [
            "Industrial Engineer",
            "Process Engineer",
            "Quality Engineer"
        ]

    if any(s in skills for s in ["electrical engineering", "plc", "scada", "automation", "industrial automation"]):
        queries += [
            "Electrical Engineer",
            "Automation Engineer",
            "PLC Engineer"
        ]

    if any(s in skills for s in ["mechanical engineering", "solidworks", "mechanical design", "maintenance"]):
        queries += [
            "Mechanical Engineer",
            "Maintenance Engineer",
            "Mechanical Design Engineer"
        ]

    if any(s in skills for s in ["telecom", "fiber optics", "5g", "lte", "rf"]):
        queries += [
            "Telecommunications Engineer",
            "Telecom Engineer",
            "RF Engineer"
        ]

    if any(s in skills for s in ["business analysis", "reporting", "agile", "scrum"]):
        queries += [
            "Business Analyst",
            "Functional Analyst",
            "Project Analyst"
        ]

    if not queries:
        queries = [best_career]

    return list(dict.fromkeys(queries))
