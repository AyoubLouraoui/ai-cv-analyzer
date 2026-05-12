def generate_cover_letter(cv_skills, best_career, job_description):

    skills_text = ", ".join(cv_skills[:8])

    cover_letter = f"""
Dear Manager,

I am excited to apply for this opportunity.

My background and technical skills strongly align with the requirements of this position, especially in the field of {best_career}.

I have experience working with technologies such as {skills_text} and I am continuously improving my expertise through practical projects and real-world applications.

I am highly motivated, passionate about technology, and eager to contribute to your team while continuing to grow professionally.

Thank you for your time and consideration. I look forward to the opportunity to discuss my application further.

Best regards,
Ayoub Louraoui
"""

    return cover_letter