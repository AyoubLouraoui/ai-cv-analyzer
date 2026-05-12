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
from job_api import search_real_jobs

st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="🤖",
    layout="wide"
)

# =======================
# CSS
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

</style>
""", unsafe_allow_html=True)

# =======================
# HEADER
# =======================

st.markdown(
    "<div class='main-title'>🤖 AI CV Analyzer</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Analyze your CV, discover your best career path, get job recommendations and professional reports.</div>",
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
    st.write("✅ Real Jobs API")

# =======================
# INPUT
# =======================

st.markdown("<div class='card'>", unsafe_allow_html=True)

st.markdown(
    "<div class='section-title'>📥 Upload & Analyze</div>",
    unsafe_allow_html=True
)

col_upload, col_job = st.columns([1, 1])

with col_upload:

    uploaded_file = st.file_uploader(
        "📄 Upload your CV PDF",
        type=["pdf"]
    )

with col_job:

    job_description = st.text_area(
        "💼 Paste Job Description Optional",
        height=180
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
        real_jobs = []

        if job_description.strip():

            job_skills = extract_skills(job_description)

            score = calculate_match_score(
                cv_text,
                job_description
            )

            missing_skills, recommendations = generate_recommendations(
                cv_skills,
                job_skills,
                score
            )

        if career_predictions:

            best_career_data = career_predictions[0]

            learning_roadmap = generate_roadmap(
                best_career_data["career"]
            )

            real_jobs = search_real_jobs(
                best_career_data["career"]
            )

            cover_letter = generate_cover_letter(
                cv_text,
                cv_skills,
                best_career_data["career"],
                job_description,
                score
            )

    # =======================
    # OVERVIEW
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>📊 Global Overview</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Skills", len(cv_skills))
    c2.metric("Jobs", len(job_recommendations))
    c3.metric("Career Paths", len(career_predictions))
    c4.metric("ATS Score", f"{score}%")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # SKILLS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>✅ Skills Detected</div>",
        unsafe_allow_html=True
    )

    if cv_skills:

        skills_html = ""

        for skill in cv_skills:

            skills_html += f"<span class='good-badge'>{skill}</span>"

        st.markdown(skills_html, unsafe_allow_html=True)

        skills_df = pd.DataFrame({
            "Skill": cv_skills,
            "Value": [1] * len(cv_skills)
        })

        fig = px.pie(
            skills_df,
            names="Skill",
            values="Value",
            hole=0.45
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # CAREER PATH
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🧭 Career Path Prediction</div>",
        unsafe_allow_html=True
    )

    if career_predictions:

        best_career = career_predictions[0]

        st.markdown(
            f"## 🚀 {best_career['career']}"
        )

        st.progress(int(best_career["score"]) / 100)

        st.metric(
            "Career Match Score",
            f"{best_career['score']}%"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write("### ✅ Matched Skills")

            for skill in best_career["matched_skills"]:
                st.success(skill)

        with col2:

            st.write("### 📚 Next Skills")

            for skill in best_career["next_skills"]:
                st.warning(skill)

        st.write("### 🗺️ Learning Roadmap")

        for i, step in enumerate(learning_roadmap, start=1):

            st.info(f"Step {i}: {step}")

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # INTERVIEW QUESTIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🎤 Interview Questions</div>",
        unsafe_allow_html=True
    )

    for skill, questions in interview_questions.items():

        with st.expander(f"Questions for {skill}"):

            for q in questions:

                st.write("• " + q)

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # JOB RECOMMENDATIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>💼 Recommended Jobs</div>",
        unsafe_allow_html=True
    )

    chart_data = pd.DataFrame({
        "Job": [item["job"] for item in job_recommendations[:5]],
        "Score": [item["score"] for item in job_recommendations[:5]]
    })

    fig = px.bar(
        chart_data,
        x="Job",
        y="Score",
        text="Score"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # ATS
    # =======================

    if job_description.strip():

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown(
            "<div class='section-title'>🎯 ATS Match Analysis</div>",
            unsafe_allow_html=True
        )

        st.progress(int(score) / 100)

        st.metric("ATS Score", f"{score}%")

        if score < 40:
            st.error("Weak Match")

        elif score < 70:
            st.warning("Medium Match")

        else:
            st.success("Strong Match")

        st.write("### ❌ Missing Skills")

        for skill in missing_skills:
            st.error(skill)

        st.write("### 💡 Recommendations")

        for rec in recommendations:
            st.warning(rec)

        pdf_path = create_pdf_report(
            score,
            cv_skills,
            job_skills,
            missing_skills,
            recommendations
        )

        with open(pdf_path, "rb") as pdf_file:

            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_file,
                file_name="cv_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # COVER LETTER
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>✉️ AI Cover Letter Generator</div>",
        unsafe_allow_html=True
    )

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

    st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # REAL JOBS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🌍 Real Job Opportunities</div>",
        unsafe_allow_html=True
    )

    if real_jobs:

        for job in real_jobs:

            st.markdown(f"### 💼 {job['title']}")

            st.write(f"🏢 Company: {job['company']}")
            st.write(f"📍 Location: {job['location']}")

            st.link_button(
                "🔗 Apply Now",
                job["url"],
                use_container_width=True
            )

            st.markdown("---")

    else:

        st.warning("No real jobs found.")

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
        <p>Upload your CV PDF to begin.</p>
    </div>
    """, unsafe_allow_html=True)