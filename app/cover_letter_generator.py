import re

def extract_name(cv_text):

    lines = cv_text.split("\n")

    for line in lines[:10]:

        line = line.strip()

        if len(line.split()) >= 2 and len(line.split()) <= 4:

            if not any(char.isdigit() for char in line):

                return line

    return "Candidate"

def generate_cover_letter(cv_text, cv_skills, best_career, job_description):

    candidate_name = extract_name(cv_text)

    skills_text = ", ".join(cv_skills[:8]) if cv_skills else "relevant technical skills"

    cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for this opportunity.

My background and technical skills strongly align with the requirements of this position, especially in the field of {best_career}.

I have experience working with technologies such as {skills_text}, and I am continuously improving my expertise through practical projects and real-world applications.

I am highly motivated, passionate about technology, and eager to contribute to your team while continuing to grow professionally.

Thank you for your time and consideration. I look forward to the opportunity to discuss my application further.

Best regards,

{candidate_name}
"""

    return cover_letter