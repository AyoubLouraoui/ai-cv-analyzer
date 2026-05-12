import unicodedata


SKILL_ALIASES = {
    # AI & DATA
    "python": ["python"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node js"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "linux": ["linux"],
    "git": ["git"],
    "github": ["github", "git hub"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "data analysis": ["data analysis", "analyse de donnees", "data analytics"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "nlp": ["nlp", "natural language processing"],
    "streamlit": ["streamlit"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "power bi": ["power bi", "powerbi"],
    "excel": ["excel", "microsoft excel"],
    "airflow": ["airflow", "apache airflow"],
    "kafka": ["kafka", "apache kafka"],
    "dashboard": ["dashboard", "dashboards"],
    "dax": ["dax"],
    "power query": ["power query"],
    "data modeling": ["data modeling", "data modelling", "modelisation des donnees"],

    # SOFTWARE
    "html": ["html"],
    "css": ["css"],
    "django": ["django"],
    "api": ["api", "apis", "rest api", "restful api"],
    "authentication": ["authentication", "authentification"],
    "programming": ["programming", "programmation"],
    "algorithms": ["algorithms", "algorithmique"],
    "data structures": ["data structures", "structures de donnees"],
    "oop": ["oop", "object oriented programming", "poo"],
    "software architecture": ["software architecture", "architecture logicielle"],

    # CLOUD & CYBER
    "aws": ["aws", "amazon web services"],
    "terraform": ["terraform"],
    "ci/cd": ["ci/cd", "cicd", "ci cd"],
    "devops": ["devops", "dev ops"],
    "networking": ["networking", "reseaux", "network"],
    "security": ["security", "securite", "cybersecurity", "cyber security"],
    "ethical hacking": ["ethical hacking", "hacking ethique"],
    "siem": ["siem"],
    "penetration testing": ["penetration testing", "pentest", "test d'intrusion"],
    "firewall": ["firewall", "pare-feu"],
    "wireshark": ["wireshark"],
    "tcp/ip": ["tcp/ip", "tcp ip"],
    "cisco": ["cisco"],
    "routing": ["routing", "routage"],
    "switching": ["switching", "commutation"],
    "vlan": ["vlan"],
    "subnetting": ["subnetting", "subnet"],

    # CIVIL ENGINEERING
    "civil engineering": ["civil engineering", "genie civil", "ingenierie civile"],
    "autocad": ["autocad", "auto cad"],
    "structural analysis": ["structural analysis", "analyse structurelle"],
    "construction management": ["construction management", "gestion de chantier", "gestion de construction"],
    "construction": ["construction", "batiment", "btp"],
    "revit": ["revit"],
    "bim": ["bim", "building information modeling"],
    "sap2000": ["sap2000", "sap 2000"],
    "etabs": ["etabs"],
    "site management": ["site management", "chantier"],
    "seismic design": ["seismic design", "parasismique"],

    # INDUSTRIAL ENGINEERING
    "industrial engineering": ["industrial engineering", "genie industriel"],
    "process optimization": ["process optimization", "optimisation des processus"],
    "lean manufacturing": ["lean manufacturing", "lean"],
    "quality management": ["quality management", "management qualite"],
    "quality control": ["quality control", "controle qualite"],
    "supply chain": ["supply chain", "logistique"],
    "six sigma": ["six sigma", "6 sigma"],
    "lean six sigma": ["lean six sigma"],
    "production": ["production"],
    "production systems": ["production systems", "systemes de production"],
    "manufacturing": ["manufacturing", "fabrication"],

    # ELECTRICAL ENGINEERING
    "electrical engineering": ["electrical engineering", "genie electrique"],
    "electrical circuits": ["electrical circuits", "circuits electriques"],
    "industrial automation": ["industrial automation", "automatisme industriel"],
    "automation": ["automation", "automatisme"],
    "plc": ["plc", "automate programmable"],
    "scada": ["scada"],
    "embedded systems": ["embedded systems", "systemes embarques"],
    "electronics": ["electronics", "electronique"],
    "industrial communication": ["industrial communication", "communication industrielle"],
    "robotics": ["robotics", "robotique"],
    "iot": ["iot", "internet of things"],

    # MECHANICAL ENGINEERING
    "mechanical engineering": ["mechanical engineering", "genie mecanique"],
    "mechanical design": ["mechanical design", "conception mecanique"],
    "solidworks": ["solidworks", "solid works"],
    "thermodynamics": ["thermodynamics", "thermodynamique"],
    "industrial maintenance": ["industrial maintenance", "maintenance industrielle"],
    "maintenance": ["maintenance"],
    "mechanics": ["mechanics", "mecanique"],
    "diagnostics": ["diagnostics", "diagnostic"],
    "predictive maintenance": ["predictive maintenance", "maintenance predictive"],
    "industrial systems": ["industrial systems", "systemes industriels"],

    # TELECOM
    "telecom": ["telecom", "telecommunications", "telecommunication"],
    "telecom infrastructure": ["telecom infrastructure", "infrastructure telecom"],
    "fiber optics": ["fiber optics", "fibre optique", "optical fiber"],
    "5g": ["5g"],
    "lte": ["lte", "4g"],
    "rf": ["rf", "radio frequency", "radiofrequence"],

    # BUSINESS
    "business analysis": ["business analysis", "analyse business", "analyse metier"],
    "reporting": ["reporting"],
    "agile": ["agile"],
    "scrum": ["scrum"],
}


def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def extract_skills(text):
    text = normalize_text(text)
    found_skills = []

    for skill, aliases in SKILL_ALIASES.items():
        if any(alias in text for alias in aliases):
            found_skills.append(skill.title())

    return sorted(set(found_skills))
