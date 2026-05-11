from fpdf import FPDF
import tempfile


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "AI CV Analyzer Report", ln=True, align="C")
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 13)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def section_text(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, text)
        self.ln(3)


def create_pdf_report(score, cv_skills, job_skills, missing_skills, recommendations):
    pdf = PDFReport()
    pdf.add_page()

    pdf.section_title("ATS Match Score")
    pdf.section_text(f"{score}%")

    pdf.section_title("Skills Found in CV")
    pdf.section_text(", ".join(cv_skills) if cv_skills else "No skills detected.")

    pdf.section_title("Skills Required in Job")
    pdf.section_text(", ".join(job_skills) if job_skills else "No job skills detected.")

    pdf.section_title("Missing Skills")
    pdf.section_text(", ".join(missing_skills) if missing_skills else "No missing skills.")

    pdf.section_title("Recommendations")
    for rec in recommendations:
        pdf.section_text("- " + rec)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)

    return temp_file.name