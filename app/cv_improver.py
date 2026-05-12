from skill_extractor import normalize_text


def improve_cv(cv_text, cv_skills):
    suggestions = []

    text = normalize_text(cv_text)
    skills_lower = [skill.lower() for skill in cv_skills]

    if "github" not in text:
        suggestions.append("Add your GitHub portfolio link.")

    if "linkedin" not in text:
        suggestions.append("Add your LinkedIn profile.")

    if "project" not in text and "projet" not in text:
        suggestions.append("Add technical projects related to your target field.")

    if "certification" not in text and "certificate" not in text and "certificat" not in text:
        suggestions.append("Add certifications to strengthen your CV.")

    important_skills = ["python", "sql", "excel", "power bi", "docker", "git"]
    missing = [skill for skill in important_skills if skill not in skills_lower]

    if missing:
        suggestions.append("Consider adding or learning: " + ", ".join(missing[:5]))

    if "experience" not in text and "stage" not in text:
        suggestions.append("Add professional experience, internships, or practical work.")

    return suggestions
