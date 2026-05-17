from urllib.parse import quote_plus


CAREER_DOMAINS = {
    "Data Analyst": "Data Analysis",
    "Data Engineer": "Data Engineering",
    "AI Engineer": "Artificial Intelligence",
    "Machine Learning Engineer": "Machine Learning",
    "BI Developer": "Business Intelligence",
    "Software Engineer": "Software Engineering",
    "Full Stack Developer": "Full Stack Development",
    "Backend Developer": "Backend Development",
    "Cloud Engineer": "Cloud Engineering",
    "Cybersecurity Engineer": "Cybersecurity",
    "Network Engineer": "Networking",
    "Civil Engineering": "Civil Engineering",
    "Structural Engineer": "Structural Engineering",
    "Industrial Engineering": "Industrial Engineering",
    "Process Engineer": "Process Engineering",
    "Electrical Engineering": "Electrical Engineering",
    "Automation Engineer": "Automation Engineering",
    "Mechanical Engineering": "Mechanical Engineering",
    "Maintenance Engineer": "Maintenance Engineering",
    "Telecommunications Engineer": "Telecommunications",
    "Business Analyst": "Business Analysis",
}


YOUTUBE_PLAYLISTS_BY_SKILL = {
    "Tableau": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Statistics": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Data Visualization": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Business Analysis": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "DAX": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Data Modeling": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Power Query": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "ETL": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Transformers": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "LLMs": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "RAG": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "LangChain": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "Vector Databases": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "MLflow": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "MLOps": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "Model Deployment": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "TypeScript": "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gUgr39Q_yD6v-bSyMwKPUI",
    "Next.js": "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gUgr39Q_yD6v-bSyMwKPUI",
    "Authentication": "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gUgr39Q_yD6v-bSyMwKPUI",
    "Docker": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
    "Kubernetes": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
    "Cloud Computing": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
    "CI/CD": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
    "Microservices": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
}


YOUTUBE_PLAYLISTS_BY_CAREER = {
    "Data Analyst": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "BI Developer": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "Business Analyst": "https://www.youtube.com/playlist?list=PLUaB-1hjhk8FE_XZ87vPPSfHqb6OcM0cF",
    "AI Engineer": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "Machine Learning Engineer": "https://www.youtube.com/playlist?list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi",
    "Full Stack Developer": "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gUgr39Q_yD6v-bSyMwKPUI",
    "Backend Developer": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
    "Cloud Engineer": "https://www.youtube.com/playlist?list=PLy7NrYWoggjwPggqtFsI_zMAwvG0SqYCb",
}


COURSERA_BY_SKILL = {
    "Tableau": "https://www.coursera.org/professional-certificates/google-data-analytics",
    "Statistics": "https://www.coursera.org/professional-certificates/google-data-analytics",
    "Data Visualization": "https://www.coursera.org/professional-certificates/google-data-analytics",
    "Business Analysis": "https://www.coursera.org/specializations/business-analytics",
    "Apache Spark": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
    "Hadoop": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
    "dbt": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
    "Cloud AWS": "https://www.coursera.org/professional-certificates/aws-cloud-solutions-architect",
    "Data Warehousing": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
    "Transformers": "https://www.coursera.org/specializations/machine-learning-introduction",
    "LLMs": "https://www.coursera.org/specializations/machine-learning-introduction",
    "RAG": "https://www.coursera.org/professional-certificates/ibm-ai-engineering",
    "LangChain": "https://www.coursera.org/professional-certificates/ibm-ai-engineering",
    "Vector Databases": "https://www.coursera.org/professional-certificates/ibm-ai-engineering",
    "MLflow": "https://www.coursera.org/professional-certificates/ibm-machine-learning",
    "MLOps": "https://www.coursera.org/professional-certificates/ibm-machine-learning",
    "FastAPI": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
    "Model Deployment": "https://www.coursera.org/professional-certificates/ibm-machine-learning",
    "Kubernetes": "https://www.coursera.org/professional-certificates/google-cloud-cloud-digital-leader-training",
    "DAX": "https://www.coursera.org/professional-certificates/google-business-intelligence",
    "Data Modeling": "https://www.coursera.org/professional-certificates/google-business-intelligence",
    "ETL": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
    "Power Query": "https://www.coursera.org/professional-certificates/google-business-intelligence",
    "System Design": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
    "Microservices": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
    "Clean Architecture": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
    "CI/CD": "https://www.coursera.org/professional-certificates/ibm-devops-and-software-engineering",
    "Next.js": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
    "TypeScript": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
    "Docker": "https://www.coursera.org/professional-certificates/ibm-devops-and-software-engineering",
    "Authentication": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
    "Azure": "https://www.coursera.org/professional-certificates/microsoft-azure-fundamentals-az-900",
    "GCP": "https://www.coursera.org/professional-certificates/google-cloud-cloud-digital-leader-training",
    "Cloud Computing": "https://www.coursera.org/professional-certificates/google-cloud-cloud-digital-leader-training",
    "Monitoring": "https://www.coursera.org/professional-certificates/ibm-devops-and-software-engineering",
    "Penetration Testing": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "SIEM": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "SOC": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "Malware Analysis": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "Project Management": "https://www.coursera.org/professional-certificates/google-project-management",
    "Scrum": "https://www.coursera.org/professional-certificates/google-project-management",
    "Agile": "https://www.coursera.org/professional-certificates/google-project-management",
    "Six Sigma": "https://www.coursera.org/specializations/six-sigma-fundamentals",
    "Lean Six Sigma": "https://www.coursera.org/specializations/six-sigma-fundamentals",
}


def coursera_search_url(skill):
    return f"https://www.coursera.org/search?query={quote_plus(skill + ' certificate')}"


def get_learning_resources(career, next_skills=None):
    next_skills = next_skills or []
    domain_label = CAREER_DOMAINS.get(career, career or "Career Development")
    fallback_youtube = YOUTUBE_PLAYLISTS_BY_CAREER.get(career)
    resources = []

    for skill in next_skills:
        youtube_url = YOUTUBE_PLAYLISTS_BY_SKILL.get(skill) or fallback_youtube
        coursera_url = COURSERA_BY_SKILL.get(skill) or coursera_search_url(skill)

        resources.append({
            "skill": skill,
            "youtube_url": youtube_url,
            "coursera_url": coursera_url,
            "youtube_title": f"Learn {skill} on YouTube",
            "coursera_title": f"{skill} Coursera certificate",
        })

    return {
        "domain": domain_label,
        "skill_resources": resources,
    }
