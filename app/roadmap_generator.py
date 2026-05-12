ROADMAPS = {

    # =========================
    # AI & DATA
    # =========================

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
    ],

    # =========================
    # SOFTWARE
    # =========================

    "Software Engineer": [
        "Learn programming fundamentals",
        "Master algorithms and data structures",
        "Learn Git and GitHub",
        "Build backend and frontend projects",
        "Learn software architecture",
        "Deploy applications online"
    ],

    "Full Stack Developer": [
        "Learn HTML CSS JavaScript",
        "Learn React.js",
        "Learn Node.js and Express",
        "Learn MongoDB or PostgreSQL",
        "Build full stack applications",
        "Deploy projects online"
    ],

    "Backend Developer": [
        "Master Python or Node.js",
        "Learn FastAPI or Django",
        "Learn APIs and authentication",
        "Learn PostgreSQL",
        "Learn Docker",
        "Deploy backend services"
    ],

    # =========================
    # CLOUD & CYBER
    # =========================

    "Cloud Engineer": [
        "Learn Linux administration",
        "Learn AWS fundamentals",
        "Learn Docker and Kubernetes",
        "Learn Terraform",
        "Learn CI/CD pipelines",
        "Deploy cloud infrastructure"
    ],

    "Cybersecurity Engineer": [
        "Learn networking basics",
        "Learn Linux security",
        "Learn ethical hacking",
        "Learn SIEM tools",
        "Learn penetration testing",
        "Build cybersecurity labs"
    ],

    "Network Engineer": [
        "Learn TCP/IP fundamentals",
        "Learn Cisco routing and switching",
        "Learn VLAN and subnetting",
        "Learn firewall configuration",
        "Prepare for CCNA certification",
        "Build networking labs"
    ],

    # =========================
    # GENIE CIVIL
    # =========================

    "Civil Engineering": [
        "Learn AutoCAD",
        "Learn structural analysis",
        "Learn construction management",
        "Learn Revit and BIM",
        "Learn SAP2000 and ETABS",
        "Work on real construction projects"
    ],

    "Structural Engineer": [
        "Master structural analysis",
        "Learn SAP2000",
        "Learn ETABS",
        "Learn seismic design",
        "Learn BIM tools",
        "Design structural projects"
    ],

    # =========================
    # GENIE INDUSTRIEL
    # =========================

    "Industrial Engineering": [
        "Learn industrial process optimization",
        "Learn Lean Manufacturing",
        "Learn quality management",
        "Learn supply chain management",
        "Learn Six Sigma",
        "Work on industrial case studies"
    ],

    "Process Engineer": [
        "Learn process optimization",
        "Learn production systems",
        "Learn industrial automation",
        "Learn Lean Six Sigma",
        "Analyze industrial workflows",
        "Improve manufacturing processes"
    ],

    # =========================
    # GENIE ELECTRIQUE
    # =========================

    "Electrical Engineering": [
        "Learn electrical circuits",
        "Learn industrial automation",
        "Learn PLC programming",
        "Learn SCADA systems",
        "Learn embedded systems basics",
        "Build automation projects"
    ],

    "Automation Engineer": [
        "Learn PLC programming",
        "Learn SCADA systems",
        "Learn industrial communication",
        "Learn robotics basics",
        "Learn IoT systems",
        "Deploy automation systems"
    ],

    # =========================
    # GENIE MECANIQUE
    # =========================

    "Mechanical Engineering": [
        "Learn mechanical design",
        "Learn SolidWorks",
        "Learn AutoCAD",
        "Learn thermodynamics",
        "Learn industrial maintenance",
        "Build mechanical projects"
    ],

    "Maintenance Engineer": [
        "Learn industrial maintenance",
        "Learn diagnostics techniques",
        "Learn predictive maintenance",
        "Learn industrial systems",
        "Learn automation basics",
        "Work on maintenance projects"
    ],

    # =========================
    # TELECOM
    # =========================

    "Telecommunications Engineer": [
        "Learn networking fundamentals",
        "Learn RF systems",
        "Learn fiber optics",
        "Learn LTE and 5G",
        "Learn telecom infrastructure",
        "Work on telecom projects"
    ],

    # =========================
    # BUSINESS
    # =========================

    "Business Analyst": [
        "Learn business analysis",
        "Learn Excel advanced tools",
        "Learn SQL and reporting",
        "Learn Power BI",
        "Learn Agile and Scrum",
        "Build business dashboards"
    ]
}


def generate_roadmap(best_career):

    return ROADMAPS.get(best_career, [
        "Improve your technical skills",
        "Build practical projects",
        "Create a strong GitHub portfolio",
        "Deploy your projects online"
    ])