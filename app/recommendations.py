def generate_recommendations(cv_skills, job_skills, score):
    missing_skills = []

    for skill in job_skills:
        if skill not in cv_skills:
            missing_skills.append(skill)

    recommendations = []

    if score < 40:
        recommendations.append("Your CV is weak for this job. Add more relevant skills and projects.")
    elif score < 70:
        recommendations.append("Your CV is acceptable, but it needs improvement to match this job better.")
    else:
        recommendations.append("Your CV has a strong match with this job description.")

    if missing_skills:
        recommendations.append(
            "Add these missing skills: " + ", ".join(missing_skills)
        )

    if len(cv_skills) < 6:
        recommendations.append("Add more technical skills to your CV.")

    if "Python" in job_skills and "Python" not in cv_skills:
        recommendations.append("Python is important for this offer. Add Python projects or experience.")

    if "Sql" in job_skills and "Sql" not in cv_skills:
        recommendations.append("SQL is required. Add database experience or SQL projects.")

    return missing_skills, recommendations