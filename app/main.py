import streamlit as st
import plotly.express as px
import pandas as pd

from pdf_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from matcher import calculate_match_score
from recommendations import generate_recommendations
from report_generator import generate_report
from job_recommender import recommend_jobs
from pdf_report import create_pdf_report
from career_path import predict_career_path
from interview_generator import generate_interview_questions
from roadmap_generator import generate_roadmap
from cover_letter_generator import generate_cover_letter

st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="🤖",
    layout="wide"
)

# =======================
# CSS PRO DESIGN
# =======================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #020617 100%);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 35px;
}

.card {
    background: rgba(15, 23, 42, 0.85);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 15px;
    color: #f8fafc;
}

.good-badge {
    display: inline-block;
    padding: 8px 14px;
    margin: 5px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(74, 222, 128, 0.35);
    color: #bbf7d0;
    font-weight: 600;
}

hr {
    border: none;
    height: 1px;
    background: rgba(148, 163, 184, 0.25);
    margin: 25px 0;
}
</style>
""", unsafe_allow_html=True)

# =======================
# HEADER
# =======================

st.markdown("<div class='main-title'>🤖 AI CV Analyzer</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Analyze your CV, discover your best career path, get job recommendations, interview questions, cover letter and a professional report.</div>",
    unsafe_allow_html=True
)

# =======================
# SIDEBAR
# =======================

with st.sidebar:
    st.title("⚙️ Dashboard")
    st.write("Upload your CV and explore AI-powered analysis.")

    st.markdown("---")

    st.write("### Features")
    st.write("✅ CV Skills Extraction")
    st.write("✅ Job Recommendations")
    st.write("✅ Career Path Prediction")
    st.write("✅ Learning Roadmap")
    st.write("✅ Interview Questions")
    st.write("✅ ATS Score")
    st.write("✅ PDF Report")
    st.write("✅ Cover Letter Generator")

    st.markdown("---")
    st.info("Tip: Add a job description to activate ATS analysis and cover letter generation.")

# =======================
# INPUT CARD
# =======================

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📥 Upload & Analyze</div>", unsafe_allow_html=True)

col_upload, col_job = st.columns([1, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "📄 Upload your CV PDF",
        type=["pdf"]
    )

with col_job:
    job_description = st.text_area(
        "💼 Paste Job Description Optional",
        height=180,
        placeholder="Paste the job offer here to calculate ATS score..."
    )

st.markdown("</div>", unsafe_allow_html=True)

# =======================
# MAIN LOGIC
# =======================

if uploaded_file is not None:

    with st.spinner("Analyzing your CV with AI..."):

        cv_text = extract_text_from_pdf(uploaded_file)
        cv_skills = extract_skills(cv_text)

        job_recommendations = recommend_jobs(cv_skills)
        career_predictions = predict_career_path(cv_skills)
        interview_questions = generate_interview_questions(cv_skills)

        score = 0
        job_skills = []
        missing_skills = []
        recommendations = []
        learning_roadmap = []
        cover_letter = ""

        if career_predictions:
            best_career_data = career_predictions[0]
            learning_roadmap = generate_roadmap(best_career_data["career"])

            cover_letter = generate_cover_letter(
                cv_skills,
                best_career_data["career"],
                job_description
            )

        if job_description.strip():
            job_skills = extract_skills(job_description)
            score = calculate_match_score(cv_text, job_description)

            missing_skills, recommendations = generate_recommendations(
                cv_skills,
                job_skills,
                score
            )

    # =======================
    # TOP METRICS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Global Overview</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Skills Detected", len(cv_skills))
    m2.metric("Recommended Jobs", len(job_recommendations))
    m3.metric("Career Paths", len(career_predictions))
    m4.metric("ATS Score", f"{score}%" if job_description.strip() else "Optional")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # SKILLS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>✅ Skills Detected in Your CV</div>", unsafe_allow_html=True)

    if cv_skills:
        skills_html = ""
        for skill in cv_skills:
            skills_html += f"<span class='good-badge'>{skill}</span>"

        st.markdown(skills_html, unsafe_allow_html=True)

        skills_df = pd.DataFrame({
            "Skill": cv_skills,
            "Value": [1] * len(cv_skills)
        })

        pie_fig = px.pie(
            skills_df,
            names="Skill",
            values="Value",
            title="Detected Skills Distribution",
            hole=0.45
        )

        pie_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=450
        )

        st.plotly_chart(pie_fig, use_container_width=True)

    else:
        st.warning("No skills detected in this CV.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # CAREER PATH
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧭 AI Career Path Prediction</div>", unsafe_allow_html=True)

    if career_predictions:
        best_career = career_predictions[0]

        st.markdown(f"### 🚀 Best Career Path: {best_career['career']}")
        st.progress(int(best_career["score"]) / 100)
        st.metric("Career Match Score", f"{best_career['score']}%")

        c1, c2 = st.columns(2)

        with c1:
            st.write("### ✅ Matched Skills")
            if best_career["matched_skills"]:
                for skill in best_career["matched_skills"]:
                    st.success(skill)
            else:
                st.info("No matched skills detected.")

        with c2:
            st.write("### 📚 Next Skills To Learn")
            for skill in best_career["next_skills"]:
                st.warning(skill)

        st.write("### 🗺️ Learning Roadmap")

        for i, step in enumerate(learning_roadmap, start=1):
            st.info(f"Step {i}: {step}")

        with st.expander("🔎 Show all career paths"):
            for career in career_predictions:
                st.markdown(f"#### {career['career']} - {career['score']}%")
                st.progress(int(career["score"]) / 100)

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # INTERVIEW QUESTIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🎤 AI Interview Questions Generator</div>", unsafe_allow_html=True)

    if interview_questions:
        for skill, questions in interview_questions.items():
            with st.expander(f"Questions for {skill}"):
                for q in questions:
                    st.write("• " + q)
    else:
        st.info("No interview questions generated. Add more technical skills to your CV.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # JOB RECOMMENDATIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💼 Recommended Jobs Based on Your CV</div>", unsafe_allow_html=True)

    chart_data = pd.DataFrame({
        "Job": [item["job"] for item in job_recommendations[:5]],
        "Score": [item["score"] for item in job_recommendations[:5]]
    })

    fig = px.bar(
        chart_data,
        x="Job",
        y="Score",
        text="Score",
        title="AI Job Match Analysis"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    for item in job_recommendations[:5]:

        st.markdown(f"### 🚀 {item['job']}")
        st.progress(int(item["score"]) / 100)
        st.metric("Match Score", f"{item['score']}%")

        col1, col2 = st.columns(2)

        with col1:
            st.write("✅ Matched Skills")
            if item["matched_skills"]:
                for skill in item["matched_skills"]:
                    st.success(skill)
            else:
                st.info("No matched skills")

        with col2:
            st.write("❌ Missing Skills")
            if item["missing_skills"]:
                for skill in item["missing_skills"]:
                    st.error(skill)
            else:
                st.success("No missing skills")

        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # ATS ANALYSIS
    # =======================

    if job_description.strip():

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎯 ATS Match Analysis</div>", unsafe_allow_html=True)

        st.progress(int(score) / 100)
        st.metric("ATS Score", f"{score}%")

        if score < 40:
            st.error("Weak Match")
        elif score < 70:
            st.warning("Medium Match")
        else:
            st.success("Strong Match")

        a1, a2, a3 = st.columns(3)

        a1.metric("CV Skills", len(cv_skills))
        a2.metric("Job Skills", len(job_skills))
        a3.metric("Missing Skills", len(missing_skills))

        st.markdown("### ❌ Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.error(skill)
        else:
            st.success("No missing skills detected.")

        st.markdown("### 💡 AI Recommendations")

        if recommendations:
            for rec in recommendations:
                st.warning(rec)
        else:
            st.info("No recommendations generated.")

        report = generate_report(
            score,
            cv_skills,
            job_skills,
            missing_skills,
            recommendations
        )

        pdf_path = create_pdf_report(
            score,
            cv_skills,
            job_skills,
            missing_skills,
            recommendations
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Professional PDF Report",
                data=pdf_file,
                file_name="cv_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # COVER LETTER GENERATOR
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>✉️ AI Cover Letter Generator</div>", unsafe_allow_html=True)

    if cover_letter:
        st.text_area(
            "Generated Cover Letter",
            cover_letter,
            height=350
        )

        st.download_button(
            label="📥 Download Cover Letter",
            data=cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Cover letter will be generated after CV analysis.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # RAW CV TEXT
    # =======================

    with st.expander("📄 Show Extracted CV Text"):
        st.write(cv_text)

else:
    st.markdown("""
    <div class='card'>
        <h3>🚀 Start your AI analysis</h3>
        <p>Upload your CV PDF to generate skills, job recommendations, career path, roadmap, interview questions and cover letter.</p>
    </div>
    """, unsafe_allow_html=True)