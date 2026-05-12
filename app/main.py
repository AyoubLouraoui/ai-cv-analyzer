import streamlit as st
import plotly.express as px
import pandas as pd
import re

from auth_system import register_user, login_user
from pdf_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from matcher import calculate_match_score
from recommendations import generate_recommendations
from job_recommender import recommend_jobs
from pdf_report import create_pdf_report
from career_path import predict_career_path
from interview_generator import generate_interview_questions
from roadmap_generator import generate_roadmap
from cover_letter_generator import generate_cover_letter
from job_api import search_morocco_jobs, search_international_jobs
from job_query_builder import build_job_queries
from cv_improver import improve_cv


def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email.strip()) is not None


st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="🤖",
    layout="wide"
)


# =======================
# GLOBAL CSS
# =======================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
    color: white;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 54px;
    font-weight: 900;
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
    background: rgba(15, 23, 42, 0.88);
    padding: 25px;
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 0 15px 35px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 18px;
    color: #f8fafc;
}

.good-badge {
    display: inline-block;
    padding: 10px 16px;
    margin: 6px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(74, 222, 128, 0.35);
    color: #bbf7d0;
    font-weight: 600;
}

.login-card {
    max-width: 540px;
    margin: 40px auto 25px auto;
    padding: 35px;
    border-radius: 28px;
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid rgba(96, 165, 250, 0.35);
    box-shadow: 0 25px 70px rgba(0,0,0,0.55);
    text-align: center;
}

.login-title {
    font-size: 44px;
    font-weight: 900;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.login-subtitle {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 12px;
}

</style>
""", unsafe_allow_html=True)


# =======================
# AUTH SESSION
# =======================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "auth_message" not in st.session_state:
    st.session_state.auth_message = ""


# =======================
# LOGIN / REGISTER
# =======================

if not st.session_state.logged_in:

    st.markdown("""
    <div class="login-card">
        <div class="login-title">🤖 AI CV Analyzer</div>
        <p class="login-subtitle">
            AI-Powered Career Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    if st.session_state.auth_message:
        st.success(st.session_state.auth_message)

    with login_tab:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            if login_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.auth_message = ""
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with register_tab:
        new_username = st.text_input("Username", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Create Account", use_container_width=True):
            if not new_username or not new_email or not new_password:
                st.error("❌ Please fill all fields")
            elif not is_valid_email(new_email):
                st.error("Please enter a valid email address.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                try:
                    register_user(new_username, new_email, new_password)
                    st.session_state.auth_message = "Account created successfully. You can login now."
                    st.rerun()
                    st.success("✅ Account created successfully. You can login now.")
                except Exception:
                    st.error("❌ Username or email already exists")

    st.stop()


# =======================
# SIDEBAR
# =======================

with st.sidebar:
    st.success(f"👋 Welcome, {st.session_state.username}")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("⚙️ Dashboard")
    st.markdown("---")
    st.write("### 🚀 Features")
    st.write("✅ CV Skills Extraction")
    st.write("✅ ATS Match Analysis")
    st.write("✅ AI Career Prediction")
    st.write("✅ Learning Roadmaps")
    st.write("✅ AI Interview Questions")
    st.write("✅ Real Jobs API")
    st.write("✅ Morocco & International Jobs")
    st.write("✅ Cover Letter Generator")
    st.write("✅ AI CV Improvements")


# =======================
# HEADER
# =======================

st.markdown("<div class='main-title'>🤖 AI CV Analyzer</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='subtitle'>Analyze your CV with AI and discover the best career opportunities.</div>",
    unsafe_allow_html=True
)


# =======================
# INPUT SECTION
# =======================

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📥 Upload & Analyze</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📄 Upload your CV PDF",
        type=["pdf"]
    )

with col2:
    job_description = st.text_area(
        "💼 Paste Job Description Optional",
        height=180
    )

st.markdown("</div>", unsafe_allow_html=True)


# =======================
# MAIN ANALYSIS
# =======================

if uploaded_file is not None:

    with st.spinner("🚀 AI is analyzing your CV..."):

        cv_text = extract_text_from_pdf(uploaded_file)
        cv_skills = extract_skills(cv_text)

        job_recommendations = recommend_jobs(cv_skills)
        career_predictions = predict_career_path(cv_skills)
        interview_questions = generate_interview_questions(cv_skills)
        cv_improvements = improve_cv(cv_text, cv_skills)

        score = 0
        job_skills = []
        missing_skills = []
        recommendations = []
        learning_roadmap = []
        cover_letter = ""
        job_search_queries = []
        morocco_jobs = []
        international_jobs = []

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

            job_search_queries = build_job_queries(
                cv_skills,
                best_career_data["career"]
            )

            morocco_jobs = search_morocco_jobs(job_search_queries)
            international_jobs = search_international_jobs(job_search_queries)

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
    st.markdown("<div class='section-title'>📊 Overview</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Skills", len(cv_skills))
    c2.metric("Jobs", len(job_recommendations))
    c3.metric("Career Paths", len(career_predictions))
    c4.metric("ATS Score", f"{score}%" if job_description.strip() else "Optional")

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # SKILLS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>✅ Skills Detected</div>", unsafe_allow_html=True)

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

    else:
        st.warning("No skills detected.")

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # CAREER PATH
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧭 Career Path Prediction</div>", unsafe_allow_html=True)

    if career_predictions:
        best_career = career_predictions[0]

        st.markdown(f"## 🚀 {best_career['career']}")
        st.progress(int(best_career["score"]) / 100)
        st.metric("Career Match Score", f"{best_career['score']}%")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### ✅ Matched Skills")
            if best_career["matched_skills"]:
                for skill in best_career["matched_skills"]:
                    st.success(skill)
            else:
                st.info("No matched skills.")

        with col2:
            st.write("### 📚 Next Skills")
            for skill in best_career["next_skills"]:
                st.warning(skill)

        st.write("### 🗺️ Learning Roadmap")

        for i, step in enumerate(learning_roadmap, start=1):
            st.info(f"Step {i}: {step}")
    else:
        st.warning(
            "No matching career path found. Add more relevant skills to your CV "
            "or upload a CV related to one of the supported domains."
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # CV IMPROVER
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🚀 AI CV Improvement Suggestions</div>", unsafe_allow_html=True)

    if cv_improvements:
        for suggestion in cv_improvements:
            st.warning(suggestion)
    else:
        st.success("Your CV looks strong.")

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # JOB RECOMMENDATIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💼 Recommended Jobs</div>", unsafe_allow_html=True)

    if job_recommendations:
        for job in job_recommendations[:5]:
            st.markdown(f"### {job['job']}")
            st.progress(int(job["score"]) / 100)
            st.metric("Job Match Score", f"{job['score']}%")

            if job["matched_skills"]:
                st.write("Matched skills: " + ", ".join(job["matched_skills"]))

            st.markdown("---")
    else:
        st.warning(
            "No matching jobs found from your CV skills. Make sure your CV includes "
            "clear technical skills, tools, or domain keywords."
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # REAL JOBS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🌍 Real Job Opportunities</div>", unsafe_allow_html=True)

    if job_search_queries:
        st.info("🔎 Search keywords used: " + ", ".join(job_search_queries))
    else:
        st.info("🔎 No search keywords generated.")

    st.subheader("🇲🇦 Jobs in Morocco")

    if morocco_jobs:
        for job in morocco_jobs:
            st.markdown(f"### 💼 {job['title']}")
            st.write(f"🏢 Company: {job['company']}")
            st.write(f"📍 Location: {job['location']}")

            st.write(f"Source: {job.get('source', 'API')}")

            st.link_button(
                "🔗 Apply Now",
                job["url"],
                use_container_width=True
            )

            st.markdown("---")
    else:
        st.warning("No Morocco jobs found.")

    st.subheader("🌐 International Jobs")

    if international_jobs:
        for job in international_jobs:
            country = job.get("country", "INT")

            st.markdown(f"### 💼 {job['title']} — {country}")
            st.write(f"🏢 Company: {job['company']}")
            st.write(f"📍 Location: {job['location']}")

            st.link_button(
                "🔗 Apply Now",
                job["url"],
                use_container_width=True
            )

            st.markdown("---")
    else:
        st.warning("No international jobs found.")

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # INTERVIEW QUESTIONS
    # =======================

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🎤 AI Interview Questions</div>", unsafe_allow_html=True)

    if interview_questions:
        for skill, questions in interview_questions.items():
            with st.expander(f"Questions for {skill}"):
                for q in questions:
                    st.write("• " + q)
    else:
        st.info("No interview questions generated.")

    st.markdown("</div>", unsafe_allow_html=True)


    # =======================
    # ATS
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

        st.write("### ❌ Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.error(skill)
        else:
            st.success("No missing skills detected.")

        st.write("### 💡 Recommendations")

        if recommendations:
            for rec in recommendations:
                st.warning(rec)
        else:
            st.info("No recommendations generated.")

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
    # RAW CV
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
