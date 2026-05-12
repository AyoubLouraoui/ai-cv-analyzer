import streamlit as st
import plotly.express as px
import pandas as pd
import re
import json

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
from email_verification import generate_verification_code, send_verification_email
import database


def add_cv_upload_safe(username, filename, cv_text, skills, best_career, best_score):
    try:
        database.add_cv_upload(username, filename, cv_text, skills, best_career, best_score)
    except TypeError:
        database.add_cv_upload(username, filename, skills, best_career, best_score)
    except AttributeError:
        pass


def add_user_activity_safe(username, action, details=""):
    if hasattr(database, "add_user_activity"):
        database.add_user_activity(username, action, details)


def get_all_user_activity_safe():
    if hasattr(database, "get_all_user_activity"):
        return database.get_all_user_activity()

    return []


def get_all_users_safe():
    if hasattr(database, "get_all_users"):
        return database.get_all_users()

    return []


def get_all_cv_uploads_safe():
    if hasattr(database, "get_all_cv_uploads"):
        return database.get_all_cv_uploads()

    return []


def update_user_safe(user_id, username, email):
    if hasattr(database, "update_user"):
        database.update_user(user_id, username, email)


def delete_user_safe(user_id):
    if hasattr(database, "delete_user"):
        database.delete_user(user_id)


def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email.strip()) is not None


def get_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def is_admin_login(username, password):
    admin_username = get_secret("ADMIN_USERNAME", "admin")
    admin_password = get_secret("ADMIN_PASSWORD", "abc123")

    return username == admin_username and password == admin_password


def is_admin_user(username):
    admin_usernames = get_secret("ADMIN_USERNAMES", "admin,ayoub")

    if isinstance(admin_usernames, str):
        admin_usernames = [
            item.strip().lower()
            for item in admin_usernames.split(",")
            if item.strip()
        ]

    return username.strip().lower() in admin_usernames


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

* {
    box-sizing: border-box;
}

.stApp {
    background:
        radial-gradient(circle at 18% 12%, rgba(20, 184, 166, 0.16), transparent 30%),
        radial-gradient(circle at 82% 8%, rgba(245, 158, 11, 0.10), transparent 26%),
        linear-gradient(135deg, #07111f 0%, #0b1220 48%, #101827 100%);
    color: #f8fafc;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.block-container {
    max-width: 1240px;
    padding-top: 1.25rem;
    padding-bottom: 3.5rem;
}

.main-title {
    font-size: clamp(36px, 5vw, 64px);
    line-height: 1.02;
    font-weight: 900;
    text-align: center;
    letter-spacing: 0;
    background: linear-gradient(90deg, #f8fafc 0%, #67e8f9 42%, #fbbf24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 8px;
}

.subtitle {
    text-align: center;
    font-size: 17px;
    color: #b6c4d6;
    margin: 14px auto 32px auto;
    max-width: 720px;
}

.card {
    background: rgba(9, 18, 32, 0.82);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
    margin-bottom: 18px;
    backdrop-filter: blur(14px);
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    margin-bottom: 16px;
    color: #f8fafc;
    letter-spacing: 0;
}

.good-badge {
    display: inline-block;
    padding: 9px 13px;
    margin: 6px;
    border-radius: 12px;
    background: rgba(20, 184, 166, 0.14);
    border: 1px solid rgba(45, 212, 191, 0.34);
    color: #ccfbf1;
    font-weight: 700;
    font-size: 14px;
}

.login-card {
    max-width: 620px;
    margin: 42px auto 26px auto;
    padding: 34px;
    border-radius: 18px;
    background:
        linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.92));
    border: 1px solid rgba(125, 211, 252, 0.28);
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.48);
    text-align: center;
}

.login-title {
    font-size: clamp(34px, 5vw, 48px);
    line-height: 1.08;
    font-weight: 900;
    letter-spacing: 0;
    background: linear-gradient(90deg, #f8fafc, #67e8f9, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.login-subtitle {
    color: #b6c4d6;
    font-size: 16px;
    margin-top: 12px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08111f 0%, #0f172a 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #dbeafe;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f8fafc;
    letter-spacing: 0;
}

div[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 16px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.22);
}

div[data-testid="stMetric"] label {
    color: #93a4b8;
    font-weight: 700;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f8fafc;
    font-weight: 900;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    border-radius: 12px !important;
    border: 1px solid rgba(45, 212, 191, 0.42) !important;
    background: linear-gradient(135deg, #0f766e 0%, #0ea5e9 100%) !important;
    color: #f8fafc !important;
    font-weight: 800 !important;
    min-height: 42px;
    box-shadow: 0 12px 30px rgba(14, 165, 233, 0.18);
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    transform: translateY(-1px);
    border-color: rgba(251, 191, 36, 0.78) !important;
    box-shadow: 0 16px 36px rgba(20, 184, 166, 0.22);
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(2, 6, 23, 0.72) !important;
    border: 1px solid rgba(148, 163, 184, 0.28) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(45, 212, 191, 0.74) !important;
    box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.16) !important;
}

label, .stMarkdown p, .stMarkdown li {
    color: #dbe4ef;
}

[data-testid="stFileUploader"] section {
    background: rgba(2, 6, 23, 0.48);
    border: 1px dashed rgba(125, 211, 252, 0.44);
    border-radius: 16px;
}

[data-testid="stTabs"] button {
    border-radius: 12px 12px 0 0;
    color: #cbd5e1;
    font-weight: 800;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #f8fafc;
    border-bottom-color: #2dd4bf;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 14px;
}

.stAlert {
    border-radius: 14px;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #2dd4bf, #38bdf8, #fbbf24);
}

hr {
    border-color: rgba(148, 163, 184, 0.20);
}

h1, h2, h3 {
    letter-spacing: 0;
    color: #f8fafc;
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

if "verification_code" not in st.session_state:
    st.session_state.verification_code = ""

if "verification_email" not in st.session_state:
    st.session_state.verification_email = ""

if "email_verified" not in st.session_state:
    st.session_state.email_verified = False

if "saved_upload_key" not in st.session_state:
    st.session_state.saved_upload_key = ""

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "confirm_update_user_id" not in st.session_state:
    st.session_state.confirm_update_user_id = None

if "confirm_delete_user_id" not in st.session_state:
    st.session_state.confirm_delete_user_id = None


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
            if login_user(login_username, login_password) or is_admin_login(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.is_admin = is_admin_user(login_username)
                st.session_state.auth_message = ""
                add_user_activity_safe(login_username, "login", "User logged in")
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with register_tab:
        new_username = st.text_input("Username", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        verification_code = st.text_input("Email Verification Code", key="register_verification_code")

        if st.button("Send Verification Code", use_container_width=True):
            if not new_email:
                st.error("Please enter your email first.")
            elif not is_valid_email(new_email):
                st.error("Please enter a valid email address.")
            else:
                code = generate_verification_code()
                sent, message = send_verification_email(new_email, code)

                if sent:
                    st.session_state.verification_code = code
                    st.session_state.verification_email = new_email.strip().lower()
                    st.session_state.email_verified = False
                    st.success(message)
                else:
                    st.error(message)

        if st.button("Create Account", use_container_width=True):
            if not new_username or not new_email or not new_password:
                st.error("❌ Please fill all fields")
            elif not is_valid_email(new_email):
                st.error("Please enter a valid email address.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif (
                not st.session_state.verification_code
                or st.session_state.verification_email != new_email.strip().lower()
                or verification_code.strip() != st.session_state.verification_code
            ):
                st.error("Please verify your email with the code we sent you.")
            else:
                try:
                    register_user(new_username, new_email, new_password)
                    st.session_state.logged_in = True
                    st.session_state.username = new_username
                    st.session_state.is_admin = is_admin_user(new_username)
                    st.session_state.auth_message = ""
                    st.session_state.verification_code = ""
                    st.session_state.verification_email = ""
                    st.session_state.email_verified = False
                    add_user_activity_safe(new_username, "register", "Account created")
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
        add_user_activity_safe(st.session_state.username, "logout", "User logged out")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = False
        st.rerun()

    st.title("⚙️ Dashboard")
    st.markdown("---")
    is_admin = st.session_state.is_admin or is_admin_user(st.session_state.username)

    if is_admin:
        st.success("Admin mode")
        admin_page = st.radio(
            "Admin Menu",
            ["Admin Dashboard", "CV Analyzer"],
            key="admin_page"
        )
    else:
        admin_page = "CV Analyzer"
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
# ADMIN DASHBOARD
# =======================

if admin_page == "Admin Dashboard":
    st.markdown("<div class='main-title'>Admin Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Users, uploaded CVs, and analysis history.</div>",
        unsafe_allow_html=True
    )

    users = get_all_users_safe()
    uploads = get_all_cv_uploads_safe()
    activities = get_all_user_activity_safe()

    c1, c2, c3 = st.columns(3)
    c1.metric("Users", len(users))
    c2.metric("CV Uploads", len(uploads))
    c3.metric("Activities", len(activities))

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Users</div>", unsafe_allow_html=True)

    if users:
        users_df = pd.DataFrame(users, columns=["ID", "Username", "Email"])
        st.dataframe(users_df, use_container_width=True, hide_index=True)

        st.write("### Manage User")

        user_options = {
            f"{user[1]} ({user[2]})": user
            for user in users
        }
        selected_label = st.selectbox(
            "Select user",
            list(user_options.keys()),
            key="admin_selected_user"
        )
        selected_user = user_options[selected_label]

        edit_username = st.text_input(
            "Username",
            value=selected_user[1],
            key="admin_edit_username"
        )
        edit_email = st.text_input(
            "Email",
            value=selected_user[2],
            key="admin_edit_email"
        )

        col_edit, col_delete = st.columns(2)

        with col_edit:
            if st.button("Update User", use_container_width=True):
                st.session_state.confirm_update_user_id = selected_user[0]
                st.session_state.confirm_delete_user_id = None

        with col_delete:
            if st.button("Delete User", use_container_width=True):
                st.session_state.confirm_delete_user_id = selected_user[0]
                st.session_state.confirm_update_user_id = None

        if st.session_state.confirm_update_user_id == selected_user[0]:
            st.warning(
                f"Confirm update for user '{selected_user[1]}'?"
            )
            confirm_update, cancel_update = st.columns(2)

            with confirm_update:
                if st.button("Yes, update user", use_container_width=True):
                    if not edit_username or not edit_email:
                        st.error("Username and email are required.")
                    elif not is_valid_email(edit_email):
                        st.error("Please enter a valid email address.")
                    else:
                        try:
                            update_user_safe(selected_user[0], edit_username, edit_email)
                            st.session_state.confirm_update_user_id = None
                            st.success("User updated successfully.")
                            st.rerun()
                        except Exception:
                            st.error("Could not update user. Username or email may already exist.")

            with cancel_update:
                if st.button("Cancel update", use_container_width=True):
                    st.session_state.confirm_update_user_id = None
                    st.rerun()

        if st.session_state.confirm_delete_user_id == selected_user[0]:
            st.warning(
                f"Confirm delete for user '{selected_user[1]}'? This action cannot be undone."
            )
            confirm_delete, cancel_delete = st.columns(2)

            with confirm_delete:
                if st.button("Yes, delete user", use_container_width=True):
                    if selected_user[1] == st.session_state.username:
                        st.error("You cannot delete the account you are currently using.")
                    else:
                        try:
                            delete_user_safe(selected_user[0])
                            st.session_state.confirm_delete_user_id = None
                            st.success("User deleted successfully.")
                            st.rerun()
                        except Exception:
                            st.error("Could not delete user.")

            with cancel_delete:
                if st.button("Cancel delete", use_container_width=True):
                    st.session_state.confirm_delete_user_id = None
                    st.rerun()
    else:
        st.info("No users found.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>CV Uploads</div>", unsafe_allow_html=True)

    if uploads:
        uploads_df = pd.DataFrame(
            uploads,
            columns=[
                "ID",
                "Username",
                "Filename",
                "CV Text",
                "Skills",
                "Best Career",
                "Best Score",
                "Uploaded At"
            ]
        )
        uploads_df["CV Preview"] = uploads_df["CV Text"].apply(
            lambda value: value[:300] + "..." if value and len(value) > 300 else value
        )
        uploads_df["Skills"] = uploads_df["Skills"].apply(
            lambda value: ", ".join(json.loads(value)) if value else ""
        )
        st.dataframe(
            uploads_df[
                [
                    "ID",
                    "Username",
                    "Filename",
                    "Skills",
                    "Best Career",
                    "Best Score",
                    "Uploaded At",
                    "CV Preview"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.write("### View Uploaded CV")
        cv_options = {
            f"{row[1]} - {row[2]} - {row[7]}": row
            for row in uploads
        }
        selected_cv_label = st.selectbox(
            "Select CV",
            list(cv_options.keys()),
            key="admin_selected_cv"
        )
        selected_cv = cv_options[selected_cv_label]

        st.write(f"Username: {selected_cv[1]}")
        st.write(f"Filename: {selected_cv[2]}")
        st.write(f"Best Career: {selected_cv[5]} ({selected_cv[6]}%)")
        st.text_area(
            "CV Text",
            selected_cv[3] or "",
            height=350,
            key="admin_cv_text"
        )
        st.download_button(
            label="Download CV Text",
            data=selected_cv[3] or "",
            file_name=f"{selected_cv[1]}_{selected_cv[2]}_cv.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("No CV uploads found yet.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>User Activity</div>", unsafe_allow_html=True)

    if activities:
        activities_df = pd.DataFrame(
            activities,
            columns=["ID", "Username", "Action", "Details", "Created At"]
        )
        st.dataframe(activities_df, use_container_width=True, hide_index=True)
    else:
        st.info("No user activity found yet.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


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

        upload_key = f"{st.session_state.username}:{uploaded_file.name}:{len(cv_text)}"

        if st.session_state.saved_upload_key != upload_key:
            if career_predictions:
                saved_best_career = career_predictions[0]["career"]
                saved_best_score = career_predictions[0]["score"]
            else:
                saved_best_career = "No match"
                saved_best_score = 0

            add_cv_upload_safe(
                st.session_state.username,
                uploaded_file.name,
                cv_text,
                cv_skills,
                saved_best_career,
                saved_best_score
            )
            add_user_activity_safe(
                st.session_state.username,
                "cv_upload",
                f"Uploaded {uploaded_file.name}. Best career: {saved_best_career} ({saved_best_score}%)."
            )

            if job_description.strip():
                add_user_activity_safe(
                    st.session_state.username,
                    "ats_analysis",
                    f"ATS score: {score}% for {uploaded_file.name}."
                )

            if job_search_queries:
                add_user_activity_safe(
                    st.session_state.username,
                    "job_search",
                    "Search queries: " + ", ".join(job_search_queries)
                )

            if cover_letter:
                add_user_activity_safe(
                    st.session_state.username,
                    "cover_letter",
                    f"Generated cover letter for {saved_best_career}."
                )

            st.session_state.saved_upload_key = upload_key


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
