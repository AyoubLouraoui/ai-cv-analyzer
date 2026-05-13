import streamlit as st
import plotly.express as px
import pandas as pd
import re
import json
import secrets as py_secrets
import requests
from urllib.parse import urlencode, urlparse

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


def get_user_by_email_safe(email):
    if hasattr(database, "get_user_by_email"):
        return database.get_user_by_email(email)

    return None


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


def get_social_user_value(key, default=""):
    try:
        return st.user.get(key, default)
    except Exception:
        return getattr(st.user, key, default)


def is_social_login_active():
    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False


def make_social_username(email, name):
    base = email.split("@")[0] if email else name
    base = re.sub(r"[^A-Za-z0-9_]", "_", base.lower()).strip("_")

    return base or "social_user"


def ensure_social_user():
    email = get_social_user_value("email", "")
    name = get_social_user_value("name", "") or get_social_user_value("given_name", "")

    if not email:
        email = f"{get_social_user_value('sub', py_secrets.token_hex(8))}@social.local"

    existing_user = get_user_by_email_safe(email)

    if existing_user:
        return existing_user[1]

    username = make_social_username(email, name)
    base_username = username
    counter = 1

    while database.get_user(username) is not None:
        counter += 1
        username = f"{base_username}_{counter}"

    register_user(
        username,
        email,
        py_secrets.token_urlsafe(32)
    )

    add_user_activity_safe(username, "social_register", f"Account created with social login: {email}")

    return username


def ensure_external_oauth_user(email, name, provider):
    if not email:
        email = f"{provider}_{py_secrets.token_hex(8)}@social.local"

    existing_user = get_user_by_email_safe(email)

    if existing_user:
        return existing_user[1]

    username = make_social_username(email, name)
    base_username = username
    counter = 1

    while database.get_user(username) is not None:
        counter += 1
        username = f"{base_username}_{counter}"

    register_user(
        username,
        email,
        py_secrets.token_urlsafe(32)
    )

    add_user_activity_safe(username, "social_register", f"Account created with {provider}: {email}")

    return username


def complete_social_login():
    username = ensure_social_user()
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.is_admin = is_admin_user(username)
    st.session_state.auth_message = ""
    add_user_activity_safe(username, "social_login", "User logged in with social provider")
    st.rerun()


def get_oauth_config(provider):
    try:
        secrets_dict = st.secrets.to_dict()
    except Exception:
        secrets_dict = {}

    return secrets_dict.get("oauth", {}).get(provider, {})


def get_app_base_url():
    try:
        current_url = st.context.url
    except Exception:
        current_url = None

    if not current_url:
        current_url = get_current_url_from_headers()

    if not current_url:
        return get_secret("APP_URL", "http://localhost:8501")

    parsed_url = urlparse(current_url)

    if not parsed_url.scheme or not parsed_url.netloc:
        return get_secret("APP_URL", "http://localhost:8501")

    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def get_direct_oauth_redirect_uri():
    return get_app_base_url()


def start_direct_oauth(provider):
    provider_config = get_oauth_config(provider)
    client_id = provider_config.get("client_id")

    if not client_id:
        st.error(f"{provider.title()} login is not configured. Add oauth.{provider}.client_id in Secrets.")
        return

    state = f"{provider}:{py_secrets.token_urlsafe(24)}"
    st.session_state.oauth_state = state
    st.session_state.oauth_provider = provider
    redirect_uri = get_direct_oauth_redirect_uri()

    if provider == "github":
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        auth_url = "https://github.com/login/oauth/authorize?" + urlencode(params)
    elif provider == "facebook":
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "email,public_profile",
            "state": state,
            "response_type": "code",
        }
        auth_url = "https://www.facebook.com/v19.0/dialog/oauth?" + urlencode(params)
    else:
        st.error("Unsupported OAuth provider.")
        return

    st.markdown(
        f"<meta http-equiv='refresh' content='0; url={auth_url}'>",
        unsafe_allow_html=True
    )
    st.link_button(f"Continue to {provider.title()}", auth_url, use_container_width=True)


def complete_direct_oauth(provider, code):
    provider_config = get_oauth_config(provider)
    client_id = provider_config.get("client_id")
    client_secret = provider_config.get("client_secret")
    redirect_uri = get_direct_oauth_redirect_uri()

    if not client_id or not client_secret:
        st.error(f"{provider.title()} login is not configured. Add client_id and client_secret in Secrets.")
        return

    try:
        if provider == "github":
            token_response = requests.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                timeout=15,
            )
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                st.error("GitHub login failed. No access token returned.")
                return

            user_response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
                timeout=15,
            )
            user_data = user_response.json()

            email = user_data.get("email")
            name = user_data.get("name") or user_data.get("login")

            if not email:
                emails_response = requests.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
                    timeout=15,
                )
                for item in emails_response.json():
                    if item.get("primary") and item.get("verified"):
                        email = item.get("email")
                        break

        elif provider == "facebook":
            token_response = requests.get(
                "https://graph.facebook.com/v19.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                timeout=15,
            )
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                st.error("Facebook login failed. No access token returned.")
                return

            user_response = requests.get(
                "https://graph.facebook.com/me",
                params={"fields": "id,name,email", "access_token": access_token},
                timeout=15,
            )
            user_data = user_response.json()
            email = user_data.get("email")
            name = user_data.get("name")
        else:
            st.error("Unsupported OAuth provider.")
            return

        username = ensure_external_oauth_user(email, name, provider)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = is_admin_user(username)
        st.session_state.auth_message = ""
        add_user_activity_safe(username, "social_login", f"User logged in with {provider}")
        st.query_params.clear()
        st.rerun()

    except Exception as error:
        st.error(f"{provider.title()} login failed.")
        st.caption(str(error))


def start_social_login(provider):
    if provider in ["github", "facebook"]:
        start_direct_oauth(provider)
        return

    config_errors = get_social_login_config_errors(provider)
    provider_name = SOCIAL_PROVIDER_NAMES.get(provider, provider.title())

    if config_errors:
        st.error(
            f"{provider_name} login is not configured yet. "
            "Add the OAuth settings in Streamlit Secrets first."
        )
        for config_error in config_errors:
            st.caption(config_error)
        return

    try:
        st.login(provider)
    except Exception as error:
        st.error(
            f"Could not start {provider_name} login. "
            "Check your Streamlit Secrets and OAuth redirect URI."
        )
        st.caption(str(error))


SOCIAL_PROVIDER_NAMES = {
    "google": "Google",
    "github": "GitHub",
    "facebook": "Facebook",
}


def get_auth_secrets():
    try:
        return st.secrets.to_dict().get("auth", {})
    except Exception:
        return {}


def get_social_login_config_errors(provider):
    auth_config = get_auth_secrets()
    provider_config = auth_config.get(provider, {})
    config_errors = []

    for field in ["redirect_uri", "cookie_secret"]:
        if not auth_config.get(field):
            config_errors.append(f"Missing: auth.{field}")

    for field in ["client_id", "client_secret", "server_metadata_url"]:
        if not provider_config.get(field):
            config_errors.append(f"Missing: auth.{provider}.{field}")

    configured_redirect_uri = auth_config.get("redirect_uri")
    current_redirect_uri = get_current_oauth_callback_uri()

    if (
        configured_redirect_uri
        and current_redirect_uri
        and configured_redirect_uri.rstrip("/") != current_redirect_uri.rstrip("/")
    ):
        config_errors.append(
            "Redirect URI mismatch. "
            f"Secrets has {configured_redirect_uri}, but this app needs {current_redirect_uri}"
        )

    return config_errors


def get_current_oauth_callback_uri():
    try:
        current_url = st.context.url
    except Exception:
        current_url = None

    if not current_url:
        current_url = get_current_url_from_headers()

    if not current_url:
        return None

    parsed_url = urlparse(current_url)

    if not parsed_url.scheme or not parsed_url.netloc:
        return None

    if parsed_url.netloc.endswith(".streamlit.app"):
        callback_path = "/~/+/oauth2callback"
    else:
        base_path = parsed_url.path.strip("/")
        callback_path = f"/{base_path}/oauth2callback" if base_path else "/oauth2callback"

    return f"{parsed_url.scheme}://{parsed_url.netloc}{callback_path}"


def get_current_url_from_headers():
    try:
        headers = st.context.headers
    except Exception:
        return None

    try:
        host = headers.get("host") or headers.get("Host")
        proto = (
            headers.get("x-forwarded-proto")
            or headers.get("X-Forwarded-Proto")
            or "https"
        )
    except Exception:
        return None

    if not host:
        return None

    return f"{proto}://{host}"


def show_social_login_diagnostics(provider):
    auth_config = get_auth_secrets()
    provider_config = auth_config.get(provider, {})
    configured_redirect_uri = auth_config.get("redirect_uri", "not set")
    expected_redirect_uri = get_current_oauth_callback_uri() or "unknown"

    with st.expander("Google login setup check"):
        st.write("Redirect URI configured in Streamlit Secrets:")
        st.code(configured_redirect_uri)
        st.write("Redirect URI this app expects:")
        st.code(expected_redirect_uri)
        st.write(
            "Google client ID:",
            "configured" if provider_config.get("client_id") else "missing"
        )
        st.write(
            "Google client secret:",
            "configured" if provider_config.get("client_secret") else "missing"
        )
        st.write(
            "Google metadata URL:",
            "configured" if provider_config.get("server_metadata_url") else "missing"
        )


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
    display: none;
}

.subtitle {
    text-align: center;
    font-size: 17px;
    color: #b6c4d6;
    margin: 14px auto 32px auto;
    max-width: 720px;
    display: none;
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

.auth-form {
    max-width: 460px;
    margin: 0 auto;
}

.auth-form [data-testid="stTextInput"],
.auth-form [data-testid="stButton"],
.auth-form .stButton,
.auth-form .stAlert {
    max-width: 460px;
    margin-left: auto;
    margin-right: auto;
}

.auth-form .stButton > button,
.auth-form [data-testid="stButton"] button {
    width: 100%;
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

.app-hero {
    position: relative;
    overflow: hidden;
    padding: 34px;
    margin: 8px 0 24px 0;
    border-radius: 22px;
    border: 1px solid rgba(125, 211, 252, 0.24);
    background:
        linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(12, 74, 110, 0.36)),
        linear-gradient(90deg, rgba(20, 184, 166, 0.14), rgba(251, 191, 36, 0.10));
    box-shadow: 0 26px 70px rgba(0, 0, 0, 0.36);
}

.app-hero::after {
    content: "";
    position: absolute;
    right: -120px;
    top: -120px;
    width: 310px;
    height: 310px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(45, 212, 191, 0.22), transparent 62%);
}

.hero-kicker {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    margin-bottom: 16px;
    border-radius: 999px;
    color: #ccfbf1;
    background: rgba(20, 184, 166, 0.12);
    border: 1px solid rgba(45, 212, 191, 0.28);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.02em;
}

.hero-title {
    position: relative;
    z-index: 1;
    max-width: 820px;
    margin: 0;
    font-size: clamp(38px, 5vw, 68px);
    line-height: 1;
    font-weight: 950;
    letter-spacing: 0;
    color: #f8fafc;
}

.hero-title span {
    color: #fbbf24;
}

.hero-copy {
    position: relative;
    z-index: 1;
    max-width: 720px;
    margin: 18px 0 0 0;
    color: #c6d3e1;
    font-size: 17px;
    line-height: 1.65;
}

.hero-strip {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 26px;
}

.hero-pill {
    padding: 13px 14px;
    border-radius: 14px;
    background: rgba(2, 6, 23, 0.38);
    border: 1px solid rgba(148, 163, 184, 0.18);
    color: #dbeafe;
    font-weight: 800;
    font-size: 13px;
}

.admin-hero {
    border-color: rgba(251, 191, 36, 0.28);
    background:
        linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(120, 53, 15, 0.26)),
        linear-gradient(90deg, rgba(251, 191, 36, 0.14), rgba(45, 212, 191, 0.10));
}

.dashboard-note {
    padding: 14px 16px;
    margin: 0 0 18px 0;
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(125, 211, 252, 0.18);
    color: #cbd5e1;
}

.sidebar-brand {
    padding: 16px;
    margin-bottom: 14px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(14, 116, 144, 0.32), rgba(15, 23, 42, 0.94));
    border: 1px solid rgba(125, 211, 252, 0.20);
}

.sidebar-brand-title {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 950;
    margin: 0;
}

.sidebar-brand-subtitle {
    color: #9fb2c8;
    font-size: 13px;
    margin: 6px 0 0 0;
}

.feature-chip {
    display: block;
    padding: 8px 10px;
    margin: 6px 0;
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.62);
    border: 1px solid rgba(148, 163, 184, 0.14);
    color: #dbeafe;
    font-weight: 700;
    font-size: 13px;
}

@media (max-width: 760px) {
    .app-hero {
        padding: 24px;
    }

    .hero-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(11,217,160,0.09), transparent 28%),
        radial-gradient(circle at 85% 8%, rgba(255,165,50,0.07), transparent 24%),
        linear-gradient(135deg, #040a14 0%, #070f1c 50%, #0a1220 100%);
    color: #e2eaf5;
    font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
}

.gs-section {
    max-width: 900px;
    margin: 36px auto 0;
    text-align: center;
}

.gs-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 14px;
    border-radius: 999px;
    border: 1px solid rgba(11,217,160,0.25);
    background: rgba(11,217,160,0.06);
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #63ffca;
    margin-bottom: 14px;
}

.gs-headline {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 5vw, 42px);
    font-weight: 800;
    color: #f0f6ff;
    letter-spacing: -0.02em;
    line-height: 1.08;
    margin: 0 0 10px;
}

.gs-headline span {
    background: linear-gradient(90deg, #0bd9a0 0%, #ffb43c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.gs-sub {
    font-size: 14px;
    color: #6f8499;
    margin: 0 0 20px;
    line-height: 1.6;
}

.gs-perks {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 28px;
}

.gs-perk {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    color: #8fa8be;
}

.gs-perk-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #0bd9a0;
    flex-shrink: 0;
}

.auth-page-wrap {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    max-width: 900px;
    margin: 32px auto 22px;
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.12);
}

.auth-left {
    background: linear-gradient(160deg, #071120 0%, #0a1929 60%, #081420 100%);
    padding: 44px 36px;
    display: flex;
    flex-direction: column;
    gap: 32px;
    position: relative;
    overflow: hidden;
    border-right: 1px solid rgba(148,163,184,0.08);
}

.auth-left-card {
    border-radius: 24px;
    border: 1px solid rgba(148,163,184,0.12);
    min-height: 520px;
}

.auth-left::before {
    content: '';
    position: absolute;
    top: -60px;
    right: -60px;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(11,217,160,0.14) 0%, transparent 65%);
    pointer-events: none;
}

.auth-left::after {
    content: '';
    position: absolute;
    bottom: -40px;
    left: -40px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(14,165,233,0.10) 0%, transparent 65%);
    pointer-events: none;
}

.auth-logo-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, #0bd9a0, #0ea5e9);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 14px;
}

.auth-brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #f0f6ff;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0 0 8px;
}

.auth-brand-name span {
    background: linear-gradient(90deg, #0bd9a0, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.auth-brand-desc {
    font-size: 13px;
    color: #7a94ae;
    line-height: 1.6;
    margin: 0;
}

.auth-feat-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.auth-feat-list li {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #9fb2c8;
}

.auth-feat-check {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    flex-shrink: 0;
    background: rgba(11,217,160,0.10);
    border: 1px solid rgba(11,217,160,0.20);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    color: #0bd9a0;
}

.auth-stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.auth-stat-chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 12px;
    padding: 12px 14px;
}

.auth-stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #e2eaf5;
    line-height: 1;
}

.auth-stat-accent {
    color: #0bd9a0;
    font-size: 14px;
}

.auth-stat-lbl {
    font-size: 11px;
    color: #8fa8be;
    margin-top: 3px;
}

.auth-right {
    background: #060e1c;
    padding: 40px 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 460px;
}

.auth-right-note {
    max-width: 280px;
    color: #7a94ae;
    font-size: 13px;
    line-height: 1.6;
    text-align: center;
}

.auth-free-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    border-radius: 999px;
    border: 1px solid rgba(11,217,160,0.22);
    background: rgba(11,217,160,0.06);
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #0bd9a0;
    margin-bottom: 18px;
}

.auth-pulse {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #0bd9a0;
    display: inline-block;
    animation: auth-pulse 2s ease-in-out infinite;
}

@keyframes auth-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.35; transform: scale(0.65); }
}

.card {
    background: rgba(9, 18, 32, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.16);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28);
}

.section-title,
h1,
h2,
h3 {
    font-family: 'Syne', sans-serif;
    color: #f0f6ff;
}

.section-title {
    font-size: 20px;
}

.good-badge {
    border-radius: 10px;
    background: rgba(11,217,160,0.12);
    border: 1px solid rgba(11,217,160,0.28);
    font-size: 13px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06101e 0%, #0a1625 100%);
    border-right: 1px solid rgba(148,163,184,0.12);
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    border-radius: 10px !important;
    border: 1px solid rgba(11,217,160,0.36) !important;
    background: linear-gradient(135deg, #0bd9a0 0%, #0ea5e9 100%) !important;
    color: #020d18 !important;
    font-weight: 800 !important;
    min-height: 42px;
    transition: transform 140ms ease, opacity 140ms ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    transform: translateY(-1px);
    opacity: 0.88;
}

.st-key-google_login button,
.st-key-google_login a,
.st-key-google_reg button,
.st-key-google_reg a,
.st-key-github_login button,
.st-key-github_reg button,
.st-key-fb_login button,
.st-key-fb_reg button {
    min-height: 48px !important;
    font-size: 0 !important;
    color: transparent !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    box-shadow: none !important;
}

.st-key-google_login button::before,
.st-key-google_login a::before,
.st-key-google_reg button::before,
.st-key-google_reg a::before,
.st-key-github_login button::before,
.st-key-github_reg button::before,
.st-key-fb_login button::before,
.st-key-fb_reg button::before {
    content: "";
    display: block;
    width: 24px;
    height: 24px;
    margin: 0 auto;
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}

.st-key-google_login button::before,
.st-key-google_login a::before,
.st-key-google_reg button::before,
.st-key-google_reg a::before {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 533.5 544.3' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%234285f4' d='M533.5 278.4c0-18.5-1.5-37.1-4.7-55.3H272.1v104.8h147c-6.1 33.8-25.7 63.7-54.4 82.7v68h87.7c51.5-47.4 81.1-117.4 81.1-200.2z'/%3E%3Cpath fill='%2334a853' d='M272.1 544.3c73.4 0 135.3-24.1 180.4-65.7l-87.7-68c-24.4 16.6-55.9 26-92.6 26-71 0-131.2-47.9-152.8-112.3H28.9v70.1c46.2 91.9 140.3 149.9 243.2 149.9z'/%3E%3Cpath fill='%23fbbc04' d='M119.3 324.3c-11.4-33.8-11.4-70.4 0-104.2V150H28.9c-38.6 76.9-38.6 167.5 0 244.4l90.4-70.1z'/%3E%3Cpath fill='%23ea4335' d='M272.1 107.7c38.8-.6 76.3 14 104.4 40.8l77.7-77.7C405 24.6 339.7-.8 272.1 0 169.2 0 75.1 58 28.9 150l90.4 70.1c21.5-64.5 81.8-112.4 152.8-112.4z'/%3E%3C/svg%3E");
}

.st-key-github_login button::before,
.st-key-github_reg button::before {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%23f0f6ff' d='M12 .5C5.73.5.65 5.58.65 11.85c0 5.02 3.26 9.28 7.78 10.78.57.11.78-.25.78-.55v-2.17c-3.17.69-3.84-1.36-3.84-1.36-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.67 1.24 3.32.95.1-.74.4-1.24.72-1.53-2.53-.29-5.19-1.27-5.19-5.64 0-1.25.45-2.26 1.18-3.06-.12-.29-.51-1.45.11-3.02 0 0 .96-.31 3.14 1.17.91-.25 1.89-.38 2.86-.38.97 0 1.95.13 2.86.38 2.18-1.48 3.14-1.17 3.14-1.17.62 1.57.23 2.73.11 3.02.73.8 1.18 1.81 1.18 3.06 0 4.38-2.67 5.34-5.21 5.63.41.36.77 1.06.77 2.14v3.17c0 .3.21.66.79.55 4.52-1.5 7.77-5.76 7.77-10.78C23.35 5.58 18.27.5 12 .5z'/%3E%3C/svg%3E");
}

.st-key-fb_login button::before,
.st-key-fb_reg button::before {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle fill='%231877f2' cx='12' cy='12' r='12'/%3E%3Cpath fill='%23fff' d='M15.12 12.75l.38-2.49h-2.39V8.64c0-.68.33-1.34 1.4-1.34h1.09V5.18s-.99-.17-1.94-.17c-1.98 0-3.27 1.2-3.27 3.37v1.88H8.2v2.49h2.19v6.02h2.72v-6.02h2.01z'/%3E%3C/svg%3E");
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(2,6,23,0.72) !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    border-radius: 10px !important;
    color: #e2eaf5 !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(11,217,160,0.55) !important;
    box-shadow: 0 0 0 3px rgba(11,217,160,0.10) !important;
}

.app-hero {
    border-radius: 20px;
    border: 1px solid rgba(11,217,160,0.18);
    background:
        linear-gradient(135deg, rgba(10,20,38,0.94), rgba(12,60,100,0.34)),
        linear-gradient(90deg, rgba(11,217,160,0.12), rgba(251,191,36,0.08));
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(32px, 4vw, 56px);
    line-height: 1.05;
    font-weight: 800;
}

.hero-copy {
    color: #7a94ae;
    font-size: 15px;
}

.hero-title span {
    color: #fbbf24;
}

.sidebar-brand {
    padding: 14px;
    margin-bottom: 12px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(11,217,160,0.14), rgba(10,20,38,0.92));
    border: 1px solid rgba(11,217,160,0.16);
}

.sidebar-brand-title {
    color: #f0f6ff;
    font-size: 17px;
    font-weight: 800;
    margin: 0;
}

.sidebar-brand-subtitle {
    color: #8fa8be;
    font-size: 12px;
    margin: 5px 0 0;
}

@media (max-width: 760px) {
    .auth-page-wrap {
        grid-template-columns: 1fr;
    }

    .auth-left {
        display: none;
    }

    .auth-right {
        min-height: 180px;
    }
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


if not st.session_state.logged_in and is_social_login_active():
    complete_social_login()

if not st.session_state.logged_in and "code" in st.query_params:
    callback_state = st.query_params.get("state")
    callback_provider = st.session_state.get("oauth_provider")

    if not callback_provider and callback_state and ":" in callback_state:
        callback_provider = callback_state.split(":", 1)[0]

    expected_state = st.session_state.get("oauth_state")

    if callback_provider in ["github", "facebook"]:
        if expected_state and callback_state != expected_state:
            st.error("OAuth state mismatch. Please try logging in again.")
            st.stop()

        complete_direct_oauth(callback_provider, st.query_params.get("code"))
        st.stop()


# =======================
# LOGIN / REGISTER
# =======================

if not st.session_state.logged_in:
    st.markdown("""
    <div class="gs-section">
        <div class="gs-badge">
            <span class="auth-pulse"></span>
            Free forever &nbsp;·&nbsp; No credit card needed
        </div>
        <h1 class="gs-headline">
            Your CV, <span>analyzed.<br>optimized. hired.</span>
        </h1>
        <p class="gs-sub">
            Join thousands of professionals who use AI CV Analyzer<br>
            to land jobs in Morocco and around the world.
        </p>
        <div class="gs-perks">
            <span class="gs-perk"><span class="gs-perk-dot"></span> ATS scoring</span>
            <span class="gs-perk"><span class="gs-perk-dot"></span> AI cover letter</span>
            <span class="gs-perk"><span class="gs-perk-dot"></span> Career paths</span>
            <span class="gs-perk"><span class="gs-perk-dot"></span> Morocco &amp; global jobs</span>
            <span class="gs-perk"><span class="gs-perk-dot"></span> Interview prep</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_left_col, right_col = st.columns([1, 1], gap="large")

    with auth_left_col:
        st.markdown("""
        <div class="auth-left auth-left-card">
            <div>
                <div class="auth-logo-box">🤖</div>
                <div class="auth-brand-name">AI CV <span>Analyzer</span></div>
                <p class="auth-brand-desc">Career intelligence platform<br>built for the modern job seeker.</p>
            </div>
            <ul class="auth-feat-list">
                <li><span class="auth-feat-check">✓</span> ATS score &amp; keyword analysis</li>
                <li><span class="auth-feat-check">✓</span> AI career path prediction</li>
                <li><span class="auth-feat-check">✓</span> Smart cover letter generator</li>
                <li><span class="auth-feat-check">✓</span> Morocco &amp; global job matching</li>
                <li><span class="auth-feat-check">✓</span> Interview prep &amp; skill roadmap</li>
            </ul>
            <div class="auth-stats-grid">
                <div class="auth-stat-chip">
                    <div class="auth-stat-num">12<span class="auth-stat-accent">k+</span></div>
                    <div class="auth-stat-lbl">CVs analyzed</div>
                </div>
                <div class="auth-stat-chip">
                    <div class="auth-stat-num">94<span class="auth-stat-accent">%</span></div>
                    <div class="auth-stat-lbl">Match accuracy</div>
                </div>
                <div class="auth-stat-chip">
                    <div class="auth-stat-num">8</div>
                    <div class="auth-stat-lbl">AI features</div>
                </div>
                <div class="auth-stat-chip">
                    <div class="auth-stat-num">🇲🇦🌍</div>
                    <div class="auth-stat-lbl">Job markets</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown(
            '<div class="auth-free-badge"><span class="auth-pulse"></span>&nbsp; Free · No credit card needed</div>',
            unsafe_allow_html=True
        )

        login_tab, register_tab = st.tabs(["🔐 Sign in", "📝 Create account"])

        if st.session_state.auth_message:
            st.success(st.session_state.auth_message)

        with login_tab:
            login_username = st.text_input("Username", key="login_username", placeholder="your_username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")

            if st.button("Go to dashboard →", use_container_width=True, key="btn_login"):
                if login_user(login_username, login_password) or is_admin_login(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.is_admin = is_admin_user(login_username)
                    st.session_state.auth_message = ""
                    add_user_activity_safe(login_username, "login", "User logged in")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            st.markdown(
                "<div style='text-align:center;margin:10px 0 8px;font-size:11.5px;color:#6f8499;letter-spacing:0.08em;'>OR CONTINUE WITH</div>",
                unsafe_allow_html=True
            )

            g_col, gh_col, fb_col = st.columns(3)
            with g_col:
                if st.button("Google", help="Continue with Google", use_container_width=True, key="google_login"):
                    start_social_login("google")
            with gh_col:
                if st.button("GitHub", help="Continue with GitHub", use_container_width=True, key="github_login"):
                    start_social_login("github")
            with fb_col:
                if st.button("Facebook", help="Continue with Facebook", use_container_width=True, key="fb_login"):
                    start_social_login("facebook")

            show_social_login_diagnostics("google")

        with register_tab:
            new_username = st.text_input("Username", key="register_username", placeholder="your_username")
            new_email = st.text_input("Email", key="register_email", placeholder="you@example.com")
            new_password = st.text_input("Password", type="password", key="register_password", placeholder="••••••••")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="••••••••")
            verification_code = st.text_input("Email Verification Code", key="register_verification_code", placeholder="6-digit code")

            send_col, _ = st.columns([1, 0.01])
            with send_col:
                if st.button("Send verification code", use_container_width=True, key="btn_send_code"):
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

            if st.button("Create my account →", use_container_width=True, key="btn_register"):
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
                    except Exception:
                        st.error("❌ Username or email already exists")

            st.markdown(
                "<div style='text-align:center;margin:10px 0 8px;font-size:11.5px;color:#6f8499;letter-spacing:0.08em;'>OR CONTINUE WITH</div>",
                unsafe_allow_html=True
            )

            g2_col, gh2_col, fb2_col = st.columns(3)
            with g2_col:
                if st.button("Google", help="Continue with Google", use_container_width=True, key="google_reg"):
                    start_social_login("google")
            with gh2_col:
                if st.button("GitHub", help="Continue with GitHub", use_container_width=True, key="github_reg"):
                    start_social_login("github")
            with fb2_col:
                if st.button("Facebook", help="Continue with Facebook", use_container_width=True, key="fb_reg"):
                    start_social_login("facebook")

            show_social_login_diagnostics("google")

    st.stop()

# =======================
# SIDEBAR
# =======================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <p class="sidebar-brand-title">AI CV Analyzer</p>
            <p class="sidebar-brand-subtitle">Career intelligence workspace</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.success(f"👋 Welcome, {st.session_state.username}")

    if st.button("🚪 Logout", use_container_width=True):
        add_user_activity_safe(st.session_state.username, "logout", "User logged out")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = False
        st.session_state.auth_message = ""
        if is_social_login_active():
            st.logout()
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
    st.markdown(
        """
        <div class="app-hero admin-hero">
            <div class="hero-kicker">ADMIN COMMAND CENTER</div>
            <h1 class="hero-title">Control every user journey from one dashboard.</h1>
            <p class="hero-copy">
                Review uploaded CVs, inspect extracted text, track activity history,
                and manage accounts without leaving the workspace.
            </p>
            <div class="hero-strip">
                <div class="hero-pill">User management</div>
                <div class="hero-pill">CV archive</div>
                <div class="hero-pill">Activity timeline</div>
                <div class="hero-pill">Downloadable records</div>
            </div>
        </div>
        """,
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

st.markdown(
    """
    <div class="app-hero">
        <div class="hero-kicker">AI CAREER INTELLIGENCE</div>
        <h1 class="hero-title">Turn any CV into a clear <span>career plan.</span></h1>
        <p class="hero-copy">
            Upload a resume and get skill extraction, job recommendations,
            learning roadmaps, interview questions, ATS feedback, and live job discovery.
        </p>
        <div class="hero-strip">
            <div class="hero-pill">CV analysis</div>
            <div class="hero-pill">Career scoring</div>
            <div class="hero-pill">Roadmaps</div>
            <div class="hero-pill">Real jobs</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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
