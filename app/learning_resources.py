from urllib.parse import quote_plus


RESOURCE_TOPICS = {
    "Data Analyst": {
        "label": "Data Analysis",
        "queries": ["data analysis", "sql", "power bi", "python pandas"],
    },
    "Data Engineer": {
        "label": "Data Engineering",
        "queries": ["data engineering", "etl pipelines", "apache airflow", "spark"],
    },
    "AI Engineer": {
        "label": "Artificial Intelligence",
        "queries": ["artificial intelligence", "machine learning", "deep learning", "llm rag"],
    },
    "Machine Learning Engineer": {
        "label": "Machine Learning",
        "queries": ["machine learning", "scikit learn", "mlops", "model deployment"],
    },
    "BI Developer": {
        "label": "Business Intelligence",
        "queries": ["business intelligence", "power bi", "dax", "data modeling"],
    },
    "Software Engineer": {
        "label": "Software Engineering",
        "queries": ["software engineering", "data structures algorithms", "git github", "system design"],
    },
    "Full Stack Developer": {
        "label": "Full Stack Development",
        "queries": ["full stack web development", "react js", "node js", "mongodb postgresql"],
    },
    "Backend Developer": {
        "label": "Backend Development",
        "queries": ["backend development", "fastapi", "django", "api authentication"],
    },
    "Cloud Engineer": {
        "label": "Cloud Engineering",
        "queries": ["cloud computing", "aws", "docker kubernetes", "terraform"],
    },
    "Cybersecurity Engineer": {
        "label": "Cybersecurity",
        "queries": ["cybersecurity", "ethical hacking", "penetration testing", "soc siem"],
    },
    "Network Engineer": {
        "label": "Networking",
        "queries": ["networking", "ccna", "routing switching", "firewall"],
    },
    "Civil Engineering": {
        "label": "Civil Engineering",
        "queries": ["civil engineering", "autocad civil", "revit bim", "construction management"],
    },
    "Structural Engineer": {
        "label": "Structural Engineering",
        "queries": ["structural engineering", "sap2000", "etabs", "seismic design"],
    },
    "Industrial Engineering": {
        "label": "Industrial Engineering",
        "queries": ["industrial engineering", "lean manufacturing", "six sigma", "supply chain"],
    },
    "Process Engineer": {
        "label": "Process Engineering",
        "queries": ["process engineering", "process optimization", "lean six sigma", "manufacturing"],
    },
    "Electrical Engineering": {
        "label": "Electrical Engineering",
        "queries": ["electrical engineering", "plc", "scada", "embedded systems"],
    },
    "Automation Engineer": {
        "label": "Automation Engineering",
        "queries": ["automation engineering", "plc programming", "scada", "industrial automation"],
    },
    "Mechanical Engineering": {
        "label": "Mechanical Engineering",
        "queries": ["mechanical engineering", "solidworks", "autocad mechanical", "industrial maintenance"],
    },
    "Maintenance Engineer": {
        "label": "Maintenance Engineering",
        "queries": ["maintenance engineering", "industrial maintenance", "predictive maintenance", "automation"],
    },
    "Telecommunications Engineer": {
        "label": "Telecommunications",
        "queries": ["telecommunications", "fiber optics", "5g networks", "rf engineering"],
    },
    "Business Analyst": {
        "label": "Business Analysis",
        "queries": ["business analysis", "excel advanced", "power bi", "agile scrum"],
    },
}


def youtube_search_url(query):
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def coursera_search_url(query):
    return f"https://www.coursera.org/search?query={quote_plus(query + ' certificate')}"


def get_learning_resources(career, skills=None):
    skills = skills or []
    resource_topic = RESOURCE_TOPICS.get(career)

    if resource_topic:
        domain_label = resource_topic["label"]
        queries = resource_topic["queries"]
    else:
        domain_label = career or "General Career Development"
        queries = skills[:4] or [domain_label]

    main_query = queries[0]

    youtube_playlists = [
        {
            "language": "Francais",
            "title": f"{domain_label} playlist en francais",
            "url": youtube_search_url(f"{main_query} playlist cours complet francais"),
        },
        {
            "language": "English",
            "title": f"{domain_label} full course playlist",
            "url": youtube_search_url(f"{main_query} full course playlist english"),
        },
    ]

    coursera_certificates = [
        {
            "title": f"{domain_label} certificates",
            "url": coursera_search_url(main_query),
        }
    ]

    for query in queries[1:4]:
        coursera_certificates.append({
            "title": f"{query.title()} certificates",
            "url": coursera_search_url(query),
        })

    return {
        "domain": domain_label,
        "youtube_playlists": youtube_playlists,
        "coursera_certificates": coursera_certificates,
    }
