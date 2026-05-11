def generate_report(score, cv_skills, job_skills, missing_skills, recommendations):
    report = f"""
AI CV ANALYZER REPORT
=====================

ATS Match Score: {score}%

Skills found in CV:
{", ".join(cv_skills) if cv_skills else "No skills found"}

Skills required in Job:
{", ".join(job_skills) if job_skills else "No skills found"}

Missing Skills:
{", ".join(missing_skills) if missing_skills else "No missing skills"}

Recommendations:
"""

    for rec in recommendations:
        report += f"- {rec}\n"

    return report