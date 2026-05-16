import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import pandas as pd
import re
import json
import html
import base64
import textwrap
import secrets as py_secrets
import requests
from urllib.parse import urlencode, urlparse

from auth_system import register_user, register_social_user, login_user, hash_password
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


def update_user_password_safe(user_id, password):
    if hasattr(database, "update_user_password"):
        database.update_user_password(user_id, hash_password(password))


def clear_user_social_identity_safe(user_id):
    if hasattr(database, "clear_user_social_identity"):
        database.clear_user_social_identity(user_id)


def delete_user_safe(user_id):
    if hasattr(database, "delete_user"):
        database.delete_user(user_id)


def get_user_by_email_safe(email):
    if hasattr(database, "get_user_by_email"):
        return database.get_user_by_email(email)

    return None


def get_current_user_safe():
    if hasattr(database, "get_user"):
        return database.get_user(st.session_state.username)

    return None


def get_user_by_social_identity_safe(provider, social_sub):
    if hasattr(database, "get_user_by_social_identity") and social_sub:
        return database.get_user_by_social_identity(provider, social_sub)

    return None


def update_user_social_identity_safe(username, provider, social_sub):
    if hasattr(database, "update_user_social_identity") and social_sub:
        database.update_user_social_identity(username, provider, social_sub)


def update_user_account_credentials_safe(username, email, password=None):
    if hasattr(database, "update_user_account_credentials"):
        password_hash = hash_password(password) if password else None
        database.update_user_account_credentials(username, email, password_hash)


def update_user_profile_image_safe(username, profile_image):
    if hasattr(database, "update_user_profile_image"):
        database.update_user_profile_image(username, profile_image)


def get_user_profile_image(user):
    if user and len(user) > 6 and user[6]:
        profile_image = str(user[6])
        if profile_image.startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,")):
            return profile_image

    return ""


def uploaded_profile_image_to_data_uri(uploaded_file):
    allowed_types = {
        "image/png": "image/png",
        "image/jpeg": "image/jpeg",
        "image/jpg": "image/jpeg",
        "image/webp": "image/webp",
    }
    mime_type = allowed_types.get(uploaded_file.type)

    if not mime_type:
        return None, "Please upload a PNG, JPG, or WEBP image."

    image_bytes = uploaded_file.getvalue()
    max_size = 1_000_000

    if len(image_bytes) > max_size:
        return None, "Profile image must be 1 MB or smaller."

    encoded_image = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded_image}", ""


def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email.strip()) is not None


def get_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def set_flash_success(message):
    st.session_state.flash_success = message


def show_flash_success():
    message = st.session_state.get("flash_success", "")

    if message:
        st.success(message)
        st.session_state.flash_success = ""


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


def split_secret_list(value):
    if not value:
        return []

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [str(item).strip() for item in value if str(item).strip()]


def get_admin_reset_username_for_email(email):
    admin_emails = split_secret_list(get_secret("ADMIN_EMAILS", ""))
    admin_email = get_secret("ADMIN_EMAIL", "")

    if admin_email:
        admin_emails.append(str(admin_email).strip())

    normalized_admin_emails = {
        item.lower()
        for item in admin_emails
        if item
    }

    if email.strip().lower() not in normalized_admin_emails:
        return ""

    admin_username = get_secret("ADMIN_USERNAME", "")

    if admin_username:
        return str(admin_username).strip()

    admin_usernames = split_secret_list(get_secret("ADMIN_USERNAMES", "admin"))
    return admin_usernames[0] if admin_usernames else "admin"


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


def clean_account_name(value):
    value = (value or "").strip()

    if not value:
        return ""

    first_name = value.split()[0]
    return re.sub(r"[^A-Za-z0-9_]", "_", first_name.lower()).strip("_")


def make_social_username(email, name):
    base = clean_account_name(name)

    if not base and email:
        base = clean_account_name(email.split("@")[0])

    return base or "social_user"


def make_social_display_name(username):
    name = (
        get_social_user_value("given_name", "")
        or get_social_user_value("name", "")
        or username
    )

    return (name or username).strip().split()[0]


def ensure_social_user():
    email = get_social_user_value("email", "")
    name = get_social_user_value("given_name", "") or get_social_user_value("name", "")
    provider = "google"
    social_sub = get_social_user_value("sub", "")

    if not email:
        email = f"{social_sub or py_secrets.token_hex(8)}@social.local"

    existing_social_user = get_user_by_social_identity_safe(provider, social_sub)

    if existing_social_user:
        return existing_social_user[1]

    existing_user = get_user_by_email_safe(email)

    if existing_user:
        update_user_social_identity_safe(existing_user[1], provider, social_sub)
        return existing_user[1]

    username = make_social_username(email, name)
    base_username = username
    counter = 1

    while database.get_user(username) is not None:
        counter += 1
        username = f"{base_username}_{counter}"

    register_social_user(
        username,
        email
    )

    update_user_social_identity_safe(username, provider, social_sub)

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

    register_social_user(
        username,
        email
    )

    add_user_activity_safe(username, "social_register", f"Account created with {provider}: {email}")

    return username


def complete_social_login():
    username = ensure_social_user()
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.display_name = make_social_display_name(username)
    st.session_state.is_admin = is_admin_user(username)
    st.session_state.auth_message = ""
    set_flash_success(f"Welcome {st.session_state.display_name}. Login successful.")
    add_user_activity_safe(username, "social_login", "User logged in with social provider")
    st.rerun()


def get_oauth_config(provider):
    try:
        secrets_dict = st.secrets.to_dict()
    except Exception:
        secrets_dict = {}

    return secrets_dict.get("oauth", {}).get(provider, {})


OAUTH_RETURN_STORAGE_KEY = "ai_cv_oauth_return_url"


def get_query_param_pairs(extra_params=None):
    pairs = []

    for key in st.query_params.keys():
        if key == "oauth_forwarded":
            continue

        try:
            values = st.query_params.get_all(key)
        except Exception:
            values = [st.query_params.get(key)]

        for value in values:
            if value is not None:
                pairs.append((key, value))

    if extra_params:
        pairs.extend(extra_params)

    return pairs


def get_forwarded_oauth_url():
    query_string = urlencode(get_query_param_pairs([("oauth_forwarded", "1")]), doseq=True)
    return f"{get_app_base_url()}/?{query_string}"


def render_oauth_return_listener():
    components.html(
        f"""
        <script>
        (function () {{
            const key = {json.dumps(OAUTH_RETURN_STORAGE_KEY)};

            function consumeOAuthReturn() {{
                let raw = null;
                try {{
                    raw = window.localStorage.getItem(key);
                }} catch (error) {{
                    return;
                }}

                if (!raw) {{
                    return;
                }}

                let payload = null;
                try {{
                    payload = JSON.parse(raw);
                }} catch (error) {{
                    return;
                }}

                if (!payload || !payload.url || Date.now() - payload.ts > 300000) {{
                    try {{ window.localStorage.removeItem(key); }} catch (error) {{}}
                    return;
                }}

                try {{ window.localStorage.removeItem(key); }} catch (error) {{}}
                window.parent.location.href = payload.url;
            }}

            window.addEventListener("storage", function (event) {{
                if (event.key === key) {{
                    consumeOAuthReturn();
                }}
            }});

            window.setInterval(consumeOAuthReturn, 700);
            consumeOAuthReturn();
        }})();
        </script>
        """,
        height=0,
    )


def render_oauth_popup_return_bridge():
    forwarded_url = get_forwarded_oauth_url()

    st.info("Returning you to AI CV Analyzer...")
    st.markdown(
        f"""
        <a href="{html.escape(forwarded_url)}" target="_self"
           style="display:block;text-align:center;padding:12px 16px;border-radius:10px;
                  background:linear-gradient(135deg,#0bd9a0,#0ea5e9);color:#020d18;
                  font-weight:800;text-decoration:none;">
            Continue to AI CV Analyzer
        </a>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <script>
        (function () {{
            const url = {json.dumps(forwarded_url)};
            const key = {json.dumps(OAUTH_RETURN_STORAGE_KEY)};
            let openerUpdated = false;

            try {{
                const openerWindow = window.top.opener || window.opener;
                if (openerWindow && !openerWindow.closed) {{
                    openerWindow.location.href = url;
                    openerUpdated = true;
                }}
            }} catch (error) {{}}

            try {{
                window.localStorage.setItem(key, JSON.stringify({{ url: url, ts: Date.now() }}));
            }} catch (error) {{}}

            window.setTimeout(function () {{
                if (openerUpdated) {{
                    try {{ window.top.close(); }} catch (error) {{}}
                }}
            }}, 900);
        }})();
        </script>
        """,
        height=0,
    )


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


def get_redirect_uri_from_oauth_state(state):
    if not state:
        return None

    parts = str(state).split(":", 2)

    if len(parts) == 3 and parts[2].startswith(("http://", "https://")):
        return parts[2]

    return None


def get_direct_oauth_url(provider):
    provider_config = get_oauth_config(provider)
    client_id = provider_config.get("client_id")

    if not client_id:
        return None

    if "oauth_states" not in st.session_state:
        st.session_state.oauth_states = {}
    if "oauth_redirect_uris" not in st.session_state:
        st.session_state.oauth_redirect_uris = {}

    redirect_uri = get_direct_oauth_redirect_uri()
    state = st.session_state.oauth_states.get(provider)

    if not state or get_redirect_uri_from_oauth_state(state) != redirect_uri:
        state = f"{provider}:{py_secrets.token_urlsafe(24)}:{redirect_uri}"
        st.session_state.oauth_states[provider] = state

    st.session_state.oauth_redirect_uris[state] = redirect_uri
    st.session_state.oauth_state = state

    if provider == "github":
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        return "https://github.com/login/oauth/authorize?" + urlencode(params)
    elif provider == "facebook":
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "public_profile",
            "state": state,
            "response_type": "code",
        }
        return "https://www.facebook.com/v19.0/dialog/oauth?" + urlencode(params)

    return None


def start_direct_oauth(provider):
    auth_url = get_direct_oauth_url(provider)

    if not auth_url:
        st.error(f"{provider.title()} login is not configured. Add oauth.{provider}.client_id in Secrets.")
        return

    st.markdown(
        f"""
        <a href="{html.escape(auth_url)}" target="_top"
           style="display:block;text-align:center;padding:12px 16px;border-radius:12px;
                  background:linear-gradient(135deg,#0f766e,#0ea5e9);color:white;
                  font-weight:800;text-decoration:none;">
            Continue to {provider.title()}
        </a>
        """,
        unsafe_allow_html=True
    )


def render_direct_oauth_button(provider, label):
    auth_url = get_direct_oauth_url(provider)
    title = f"Continue with {provider.title()}"

    if not auth_url:
        if st.button(label, use_container_width=True, disabled=True):
            pass
        st.caption(f"Add oauth.{provider}.client_id and oauth.{provider}.client_secret in Secrets.")
        return

    st.markdown(
        f"""
        <a class="direct-oauth-btn {html.escape(provider)}"
           href="{html.escape(auth_url)}"
           target="_top"
           rel="opener"
           title="{html.escape(title)}"
           aria-label="{html.escape(title)}">
            <span class="social-label">{html.escape(label)}</span>
        </a>
        """,
        unsafe_allow_html=True
    )


def show_oauth_token_error(provider, token_response, token_data):
    provider_name = SOCIAL_PROVIDER_NAMES.get(provider, provider.title())
    error_data = token_data.get("error") if isinstance(token_data, dict) else None

    if isinstance(error_data, dict):
        message = error_data.get("message") or error_data.get("error_user_msg")
        code = error_data.get("code")
        error_type = error_data.get("type")
    elif error_data:
        message = str(error_data)
        code = token_data.get("error_code") if isinstance(token_data, dict) else None
        error_type = token_data.get("error_description") if isinstance(token_data, dict) else None
    else:
        message = token_data.get("error_description") if isinstance(token_data, dict) else None
        code = token_data.get("error_code") if isinstance(token_data, dict) else None
        error_type = token_data.get("error") if isinstance(token_data, dict) else None

    st.error(f"{provider_name} login failed. No access token returned.")

    if message:
        st.caption(f"{provider_name} says: {message}")
    if code or error_type:
        st.caption(f"Details: {error_type or 'OAuth error'} / {code or token_response.status_code}")
    if not message and not error_type:
        st.caption(f"HTTP status: {token_response.status_code}")


def complete_direct_oauth(provider, code, redirect_uri=None):
    provider_config = get_oauth_config(provider)
    client_id = provider_config.get("client_id")
    client_secret = provider_config.get("client_secret")
    redirect_uri = redirect_uri or get_direct_oauth_redirect_uri()

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
                show_oauth_token_error(provider, token_response, token_data)
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
                show_oauth_token_error(provider, token_response, token_data)
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
        set_flash_success(f"Welcome {username}. Login successful.")
        add_user_activity_safe(username, "social_login", f"User logged in with {provider}")
        if "oauth_states" in st.session_state:
            st.session_state.oauth_states.pop(provider, None)
        if "oauth_redirect_uris" in st.session_state:
            st.session_state.oauth_redirect_uris.pop(st.query_params.get("state"), None)
        st.query_params.clear()
        st.rerun()

    except Exception as error:
        st.error(f"{provider.title()} login failed.")
        st.caption(str(error))


def start_social_login(provider):
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
    client_id = str(provider_config.get("client_id", "")).strip()
    server_metadata_url = str(provider_config.get("server_metadata_url", "")).strip()
    client_kwargs = provider_config.get("client_kwargs", {}) or {}

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

    if provider == "facebook":
        if client_id.isdigit():
            config_errors.append(
                "auth.facebook.client_id looks like a Meta/Facebook App ID. "
                "Use the Auth0 Application Client ID instead."
            )

        if client_id.startswith(("Ov", "Iv1.")):
            config_errors.append(
                "auth.facebook.client_id looks like a GitHub OAuth Client ID. "
                "Use the Auth0 Application Client ID instead."
            )

        if server_metadata_url and "auth0.com" not in server_metadata_url:
            config_errors.append(
                "For Streamlit st.login, Facebook should go through Auth0. "
                "Set auth.facebook.server_metadata_url to your Auth0 .well-known/openid-configuration URL."
            )

        if "auth0.com" in server_metadata_url and client_kwargs.get("connection") != "facebook":
            config_errors.append(
                'Missing or wrong: auth.facebook.client_kwargs = { "connection" = "facebook" }'
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
    padding-bottom: 0 !important;
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
.st-key-google_reg a {
    min-height: 48px !important;
    font-size: 15px !important;
    color: #e2eaf5 !important;
    background: rgba(255,255,255,0.04) !important;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 533.5 544.3' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%234285f4' d='M533.5 278.4c0-18.5-1.5-37.1-4.7-55.3H272.1v104.8h147c-6.1 33.8-25.7 63.7-54.4 82.7v68h87.7c51.5-47.4 81.1-117.4 81.1-200.2z'/%3E%3Cpath fill='%2334a853' d='M272.1 544.3c73.4 0 135.3-24.1 180.4-65.7l-87.7-68c-24.4 16.6-55.9 26-92.6 26-71 0-131.2-47.9-152.8-112.3H28.9v70.1c46.2 91.9 140.3 149.9 243.2 149.9z'/%3E%3Cpath fill='%23fbbc04' d='M119.3 324.3c-11.4-33.8-11.4-70.4 0-104.2V150H28.9c-38.6 76.9-38.6 167.5 0 244.4l90.4-70.1z'/%3E%3Cpath fill='%23ea4335' d='M272.1 107.7c38.8-.6 76.3 14 104.4 40.8l77.7-77.7C405 24.6 339.7-.8 272.1 0 169.2 0 75.1 58 28.9 150l90.4 70.1c21.5-64.5 81.8-112.4 152.8-112.4z'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: calc(50% - 96px) center !important;
    background-size: 20px 20px !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 16px !important;
    transition: transform 140ms ease, opacity 140ms ease, border-color 140ms ease !important;
}

.st-key-google_login button:hover,
.st-key-google_login a:hover,
.st-key-google_reg button:hover,
.st-key-google_reg a:hover {
    transform: translateY(-1px) !important;
    opacity: 0.88 !important;
    border-color: rgba(11,217,160,0.36) !important;
}

.st-key-google_login button::before,
.st-key-google_login a::before,
.st-key-google_reg button::before,
.st-key-google_reg a::before {
    display: none !important;
}

.st-key-google_login button p,
.st-key-google_reg button p {
    color: #e2eaf5 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}

.direct-oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 48px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #d7dee8;
    box-shadow: 0 1px 2px rgba(15,23,42,0.08);
    color: #0f172a;
    font-size: 15px;
    font-weight: 500;
    gap: 10px;
    margin-top: 8px;
    text-decoration: none;
    transition: transform 140ms ease, opacity 140ms ease, border-color 140ms ease;
}

.direct-oauth-btn:hover {
    transform: translateY(-1px);
    opacity: 0.96;
    border-color: #b8c4d4;
}

.direct-oauth-btn::before {
    content: "";
    display: block;
    width: 20px;
    height: 20px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}

.direct-oauth-btn.github::before {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%23181717' d='M12 .5C5.73.5.65 5.58.65 11.85c0 5.02 3.26 9.28 7.78 10.78.57.11.78-.25.78-.55v-2.17c-3.17.69-3.84-1.36-3.84-1.36-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.67 1.24 3.32.95.1-.74.4-1.24.72-1.53-2.53-.29-5.19-1.27-5.19-5.64 0-1.25.45-2.26 1.18-3.06-.12-.29-.51-1.45.11-3.02 0 0 .96-.31 3.14 1.17.91-.25 1.89-.38 2.86-.38.97 0 1.95.13 2.86.38 2.18-1.48 3.14-1.17 3.14-1.17.62 1.57.23 2.73.11 3.02.73.8 1.18 1.81 1.18 3.06 0 4.38-2.67 5.34-5.21 5.63.41.36.77 1.06.77 2.14v3.17c0 .3.21.66.79.55 4.52-1.5 7.77-5.76 7.77-10.78C23.35 5.58 18.27.5 12 .5z'/%3E%3C/svg%3E");
}

.direct-oauth-btn.facebook::before {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle fill='%231877f2' cx='12' cy='12' r='12'/%3E%3Cpath fill='%23fff' d='M15.12 12.75l.38-2.49h-2.39V8.64c0-.68.33-1.34 1.4-1.34h1.09V5.18s-.99-.17-1.94-.17c-1.98 0-3.27 1.2-3.27 3.37v1.88H8.2v2.49h2.19v6.02h2.72v-6.02h2.01z'/%3E%3C/svg%3E");
}

.social-label {
    line-height: 1.2;
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

.st-key-profile_circle {
    display: flex;
    justify-content: center;
    margin: 2px 0 6px;
}

.st-key-profile_circle button {
    position: relative !important;
    overflow: hidden !important;
    width: 58px !important;
    height: 58px !important;
    min-height: 58px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #0bd9a0 0%, #0ea5e9 100%) !important;
    border: 2px solid rgba(240,246,255,0.72) !important;
    box-shadow: 0 10px 26px rgba(14,165,233,0.26) !important;
    color: #02111f !important;
    font-weight: 900 !important;
}

.st-key-profile_circle button:hover {
    transform: translateY(-1px) scale(1.03) !important;
    opacity: 0.96 !important;
    border-color: #f0f6ff !important;
}

.st-key-profile_circle button p {
    font-size: 24px !important;
    line-height: 1 !important;
    margin: 0 !important;
    color: #02111f !important;
    font-weight: 900 !important;
}

.profile-name {
    color: #f0f6ff;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.15;
    padding-top: 8px;
    word-break: break-word;
}

.profile-hint {
    color: #8fa8be;
    font-size: 11px;
    margin-top: 3px;
}

.profile-menu-title {
    color: #8fa8be;
    font-size: 11px;
    letter-spacing: 0.08em;
    margin: 8px 0 8px;
    text-transform: uppercase;
}

.st-key-profile_menu_dashboard button,
.st-key-profile_menu_cv button,
.st-key-profile_menu_account button,
.st-key-profile_menu_about button {
    background: rgba(15, 23, 42, 0.78) !important;
    border: 1px solid rgba(143, 168, 190, 0.28) !important;
    border-radius: 12px !important;
    color: #f0f6ff !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
}

.st-key-profile_menu_dashboard button:hover,
.st-key-profile_menu_cv button:hover,
.st-key-profile_menu_account button:hover,
.st-key-profile_menu_about button:hover {
    border-color: rgba(11, 217, 160, 0.72) !important;
    background: rgba(11, 217, 160, 0.12) !important;
}

.st-key-profile_menu_logout button {
    background: rgba(127, 29, 29, 0.22) !important;
    border: 1px solid rgba(248, 113, 113, 0.42) !important;
    border-radius: 12px !important;
    color: #fecaca !important;
    font-weight: 800 !important;
}

.account-profile-preview {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0bd9a0 0%, #0ea5e9 100%);
    background-size: cover;
    background-position: center;
    border: 3px solid rgba(240,246,255,0.84);
    box-shadow: 0 14px 36px rgba(14,165,233,0.24);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #02111f;
    font-size: 36px;
    font-weight: 900;
    margin-bottom: 14px;
}

.admin-table-card {
    margin: 14px 0 22px;
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 16px;
    background:
        linear-gradient(135deg, rgba(11,217,160,0.08), rgba(14,165,233,0.05)),
        rgba(5, 12, 24, 0.78);
    overflow: hidden;
    box-shadow: 0 18px 42px rgba(0,0,0,0.18);
}

.admin-table-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 18px 20px;
    border-bottom: 1px solid rgba(148,163,184,0.12);
}

.admin-table-title {
    color: #f0f6ff;
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    margin: 0;
}

.admin-table-subtitle {
    color: #8fa8be;
    font-size: 13px;
    margin-top: 4px;
}

.admin-table-count {
    min-width: 44px;
    height: 34px;
    padding: 0 12px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #02111f;
    background: linear-gradient(135deg, #0bd9a0, #0ea5e9);
    font-weight: 900;
    box-shadow: 0 10px 24px rgba(14,165,233,0.24);
}

.admin-table-scroll {
    overflow-x: auto;
}

.admin-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 720px;
}

.admin-table th {
    padding: 13px 18px;
    text-align: left;
    color: #8fa8be;
    background: rgba(2,6,23,0.42);
    border-bottom: 1px solid rgba(148,163,184,0.12);
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    white-space: nowrap;
}

.admin-table td {
    padding: 15px 18px;
    color: #dbe8f7;
    border-bottom: 1px solid rgba(148,163,184,0.08);
    font-size: 14px;
    vertical-align: middle;
}

.admin-table tr:last-child td {
    border-bottom: 0;
}

.admin-table tbody tr {
    transition: background 140ms ease;
}

.admin-table tbody tr:hover {
    background: rgba(11,217,160,0.055);
}

.admin-id {
    color: #0bd9a0;
    font-weight: 900;
}

.admin-strong {
    color: #f0f6ff;
    font-weight: 800;
}

.admin-muted {
    color: #8fa8be;
}

.admin-details-cell {
    max-width: 420px;
    color: #b8c7d8;
}

.admin-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    border: 1px solid rgba(148,163,184,0.18);
    white-space: nowrap;
}

.admin-pill.green {
    color: #7cf7ca;
    background: rgba(11,217,160,0.12);
    border-color: rgba(11,217,160,0.32);
}

.admin-pill.blue {
    color: #93d5ff;
    background: rgba(14,165,233,0.13);
    border-color: rgba(14,165,233,0.34);
}

.admin-pill.amber {
    color: #fde68a;
    background: rgba(251,191,36,0.12);
    border-color: rgba(251,191,36,0.34);
}

.admin-pill.red {
    color: #fecaca;
    background: rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.34);
}

.admin-pill.slate {
    color: #cbd5e1;
    background: rgba(148,163,184,0.10);
    border-color: rgba(148,163,184,0.22);
}

.admin-manage-title {
    margin: 22px 0 12px;
    color: #f0f6ff;
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
}

.about-shell {
    display: grid;
    grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
    gap: 18px;
    margin-top: 18px;
}

.about-panel {
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 18px;
    background:
        linear-gradient(135deg, rgba(11,217,160,0.08), rgba(14,165,233,0.05)),
        rgba(5, 12, 24, 0.82);
    padding: 24px;
    box-shadow: 0 18px 42px rgba(0,0,0,0.16);
}

.about-kicker {
    color: #0bd9a0;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.about-panel h2 {
    margin: 0 0 12px;
    color: #f0f6ff;
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    line-height: 1.1;
}

.about-panel p {
    color: #b8c7d8;
    font-size: 15px;
    line-height: 1.75;
    margin: 0 0 14px;
}

.about-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-top: 14px;
}

.about-feature {
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 14px;
    background: rgba(2,6,23,0.42);
    color: #e2eaf5;
    font-weight: 800;
    padding: 13px 14px;
}

.about-links {
    display: grid;
    gap: 10px;
    margin-top: 16px;
}

.about-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 46px;
    padding: 0 14px;
    border-radius: 13px;
    color: #f0f6ff !important;
    background: rgba(15,23,42,0.78);
    border: 1px solid rgba(143,168,190,0.28);
    text-decoration: none !important;
    font-weight: 800;
    transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
}

.about-link:hover {
    transform: translateY(-1px);
    border-color: rgba(11,217,160,0.72);
    background: rgba(11,217,160,0.12);
}

.about-link.missing {
    color: #8fa8be !important;
    cursor: default;
}

.about-signature {
    color: #8fa8be;
    font-size: 13px;
    line-height: 1.65;
    margin-top: 14px;
}

.site-footer {
    width: 100vw;
    min-height: 96px;
    margin: 56px calc(50% - 50vw) -1rem;
    padding: 0 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    background: #080910;
    border-top: 1px solid rgba(148,163,184,0.08);
    color: #59638f;
    font-size: 15px;
    letter-spacing: 0.01em;
}

.site-footer-name {
    color: #0bd9a0;
    font-weight: 800;
    text-decoration: none;
}

.site-footer-name:hover {
    color: #5eead4;
    text-decoration: none;
}

@media (max-width: 760px) {
    .site-footer {
        min-height: auto;
        padding: 24px 22px;
        flex-direction: column;
        align-items: flex-start;
    }

    .about-shell {
        grid-template-columns: 1fr;
    }

    .about-feature-grid {
        grid-template-columns: 1fr;
    }

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

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

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

if "confirm_reset_password_user_id" not in st.session_state:
    st.session_state.confirm_reset_password_user_id = None

if "confirm_unlink_social_user_id" not in st.session_state:
    st.session_state.confirm_unlink_social_user_id = None

if "account_verification_code" not in st.session_state:
    st.session_state.account_verification_code = ""

if "account_verification_email" not in st.session_state:
    st.session_state.account_verification_email = ""

if "account_verified" not in st.session_state:
    st.session_state.account_verified = False

if "profile_menu_open" not in st.session_state:
    st.session_state.profile_menu_open = False

if "forgot_password_open" not in st.session_state:
    st.session_state.forgot_password_open = False

if "forgot_password_code" not in st.session_state:
    st.session_state.forgot_password_code = ""

if "forgot_password_email" not in st.session_state:
    st.session_state.forgot_password_email = ""

if "forgot_password_user_id" not in st.session_state:
    st.session_state.forgot_password_user_id = None

if "forgot_password_username" not in st.session_state:
    st.session_state.forgot_password_username = ""

if "flash_success" not in st.session_state:
    st.session_state.flash_success = ""

show_flash_success()


if not st.session_state.logged_in and is_social_login_active():
    complete_social_login()

if not st.session_state.logged_in and "code" in st.query_params:
    if st.query_params.get("oauth_forwarded") != "1":
        render_oauth_popup_return_bridge()
        st.stop()

    callback_state = st.query_params.get("state")
    callback_provider = st.session_state.get("oauth_provider")

    if not callback_provider and callback_state and ":" in callback_state:
        callback_provider = callback_state.split(":", 1)[0]

    expected_state = st.session_state.get("oauth_states", {}).get(callback_provider) or st.session_state.get("oauth_state")
    callback_redirect_uri = (
        st.session_state.get("oauth_redirect_uris", {}).get(callback_state)
        or get_redirect_uri_from_oauth_state(callback_state)
    )

    if callback_provider in ["github", "facebook"]:
        if expected_state and callback_state != expected_state:
            st.error("OAuth state mismatch. Please try logging in again.")
            st.stop()

        complete_direct_oauth(callback_provider, st.query_params.get("code"), callback_redirect_uri)
        st.stop()


def get_current_account_email(user):
    google_email = get_social_user_value("email", "") if is_social_login_active() else ""

    if google_email:
        return google_email.strip().lower()

    if user and len(user) > 2 and user[2]:
        return str(user[2]).strip().lower()

    return ""


def render_account_settings():
    user = get_current_user_safe()

    if not user:
        st.error("Could not load your account. Please log out and log in again.")
        return

    current_email = get_current_account_email(user)
    stored_email = str(user[2] or "").strip().lower()
    is_google_account = is_social_login_active()
    current_profile_image = get_user_profile_image(user)
    had_platform_password_before = bool(user[3])
    has_created_password = bool(user[3]) and bool(user[7]) if len(user) > 7 else bool(user[3])

    st.markdown(
        """
        <div class="app-hero">
            <div class="hero-kicker">ACCOUNT SECURITY</div>
            <h1 class="hero-title">Manage your login details.</h1>
            <p class="hero-copy">
                Update your account email or create a password after confirming
                the verification code sent to your current email.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Account Settings</div>", unsafe_allow_html=True)

    st.write(f"Username: **{st.session_state.username}**")

    profile_letter = (st.session_state.display_name or st.session_state.username or "U").strip()[:1].upper()

    if current_profile_image:
        st.markdown(
            f"<div class='account-profile-preview' style='background-image: url({json.dumps(current_profile_image)});'></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='account-profile-preview'>{html.escape(profile_letter)}</div>",
            unsafe_allow_html=True
        )

    profile_upload = st.file_uploader(
        "Profile picture",
        type=["png", "jpg", "jpeg", "webp"],
        key="account_profile_picture"
    )
    profile_save_col, profile_remove_col = st.columns(2)

    with profile_save_col:
        if st.button(
            "Save profile picture",
            use_container_width=True,
            key="account_save_profile_picture",
            disabled=profile_upload is None
        ):
            if not profile_upload:
                st.error("Please choose a profile picture first.")
            else:
                profile_image, profile_error = uploaded_profile_image_to_data_uri(profile_upload)

                if profile_error:
                    st.error(profile_error)
                else:
                    try:
                        update_user_profile_image_safe(st.session_state.username, profile_image)
                        add_user_activity_safe(
                            st.session_state.username,
                            "profile_picture_update",
                            "Updated profile picture."
                        )
                        set_flash_success("Profile picture updated successfully.")
                        st.rerun()
                    except Exception:
                        st.error("Could not update your profile picture.")

    with profile_remove_col:
        if st.button(
            "Remove profile picture",
            use_container_width=True,
            key="account_remove_profile_picture",
            disabled=not current_profile_image
        ):
            try:
                update_user_profile_image_safe(st.session_state.username, None)
                add_user_activity_safe(
                    st.session_state.username,
                    "profile_picture_remove",
                    "Removed profile picture."
                )
                set_flash_success("Profile picture removed successfully.")
                st.rerun()
            except Exception:
                st.error("Could not remove your profile picture.")

    if current_email:
        st.write(f"Verification email: **{current_email}**")
    else:
        st.warning("No email is linked to this account yet.")

    if is_google_account and not has_created_password:
        st.info("You are logged in with Google. You can create a password after verifying your Google email.")

    send_col, status_col = st.columns([1, 1])

    with send_col:
        if st.button("Send verification code", use_container_width=True, key="account_send_code"):
            if not current_email or not is_valid_email(current_email):
                st.error("Your current account email is not valid.")
            else:
                code = generate_verification_code()
                sent, message = send_verification_email(current_email, code)

                if sent:
                    st.session_state.account_verification_code = code
                    st.session_state.account_verification_email = current_email
                    st.session_state.account_verified = False
                    st.success(message)
                else:
                    st.error(message)

    with status_col:
        if st.session_state.account_verification_email == current_email and st.session_state.account_verification_code:
            st.info("A verification code was sent to your current email.")
        else:
            st.caption("Send a code before saving changes.")

    verification_code = st.text_input(
        "Verification code",
        key="account_verification_input",
        placeholder="6-digit code"
    )

    new_email = st.text_input(
        "New email",
        value=stored_email or current_email,
        key="account_new_email"
    )

    password_label = "Create password" if is_google_account and not has_created_password else "New password"
    new_password = st.text_input(
        password_label,
        type="password",
        key="account_new_password",
        placeholder="Leave empty if you only want to change email"
    )
    confirm_password = st.text_input(
        "Confirm password",
        type="password",
        key="account_confirm_password",
        placeholder="Repeat new password"
    )

    if st.button("Save account changes", use_container_width=True, key="account_save_changes"):
        normalized_new_email = new_email.strip().lower()
        email_changed = normalized_new_email != stored_email
        password_changed = bool(new_password)

        if not st.session_state.account_verification_code:
            st.error("Please send a verification code first.")
        elif st.session_state.account_verification_email != current_email:
            st.error("Please send a fresh verification code to your current email.")
        elif verification_code.strip() != st.session_state.account_verification_code:
            st.error("Invalid verification code.")
        elif not normalized_new_email or not is_valid_email(normalized_new_email):
            st.error("Please enter a valid email address.")
        elif not email_changed and not password_changed:
            st.error("No changes to save.")
        elif password_changed and len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        elif password_changed and new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            existing_email_user = get_user_by_email_safe(normalized_new_email)

            if existing_email_user and existing_email_user[1] != st.session_state.username:
                st.error("This email is already used by another account.")
            else:
                try:
                    update_user_account_credentials_safe(
                        st.session_state.username,
                        normalized_new_email,
                        new_password if password_changed else None
                    )
                    st.session_state.account_verification_code = ""
                    st.session_state.account_verification_email = ""
                    st.session_state.account_verified = False
                    if password_changed and not had_platform_password_before:
                        activity_action = "password_create"
                        activity_details = "Created platform password after email verification."
                    elif password_changed:
                        activity_action = "password_changed"
                        activity_details = "Changed platform password after email verification."
                    elif email_changed:
                        activity_action = "email_update"
                        activity_details = "Updated account email after email verification."
                    else:
                        activity_action = "account_update"
                        activity_details = "Updated account settings."

                    add_user_activity_safe(
                        st.session_state.username,
                        activity_action,
                        activity_details
                    )
                    set_flash_success("Account updated successfully.")
                    st.rerun()
                except Exception:
                    st.error("Could not update your account. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_about_link(label, secret_name, default_url=""):
    url = str(get_secret(secret_name, default_url) or default_url).strip()
    safe_label = html.escape(label)

    if url:
        return (
            f"<a class='about-link' href='{html.escape(url, quote=True)}' target='_blank' rel='noopener noreferrer'>"
            f"<span>{safe_label}</span><span>Open</span></a>"
        )

    return (
        f"<div class='about-link missing'><span>{safe_label}</span>"
        f"<span>Coming soon</span></div>"
    )


def render_about_page():
    st.markdown(
        textwrap.dedent("""
        <div class="app-hero">
            <div class="hero-kicker">ABOUT AI CV ANALYZER</div>
            <h1 class="hero-title">Built to make smarter CVs accessible.</h1>
            <p class="hero-copy">
                A practical AI project created to help talented people improve their resumes,
                understand ATS systems, and get closer to real interview opportunities.
            </p>
            <div class="hero-strip">
                <div class="hero-pill">AI CV analysis</div>
                <div class="hero-pill">ATS optimization</div>
                <div class="hero-pill">Skill detection</div>
                <div class="hero-pill">Practical career tools</div>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True
    )

    portfolio_link = render_about_link("Portfolio Website", "PORTFOLIO_URL", "https://ayoublouraoui.netlify.app/")
    github_link = render_about_link("GitHub", "GITHUB_URL", "https://github.com/AyoubLouraoui")
    linkedin_link = render_about_link("LinkedIn", "LINKEDIN_URL", "https://www.linkedin.com/in/ayoub-louraoui-91111628a/")
    instagram_link = render_about_link("Instagram", "INSTAGRAM_URL", "https://www.instagram.com/ayoublouraoui_/")

    story_html = textwrap.dedent("""
    <div class="about-panel">
        <div class="about-kicker">The Story</div>
        <h2>Hi, I'm Ayoub Louraoui.</h2>
        <p>
            I'm an AI and Data enthusiast passionate about building smart and useful
            digital solutions.
        </p>
        <p>
            AI CV Analyzer was created from a simple observation: many talented people
            struggle to get interviews not because they lack skills, but because their CVs
            are not optimized for modern recruitment systems.
        </p>
        <p>
            As someone interested in Artificial Intelligence and data-driven technologies,
            I wanted to build a project that solves a real problem while also reflecting my
            passion for AI and web development.
        </p>
        <p>That's how AI CV Analyzer was born.</p>
        <p>
            This platform uses Artificial Intelligence to analyze resumes, detect strengths
            and weaknesses, identify important keywords, and provide smart suggestions to
            help users improve their CVs and become more ATS-friendly.
        </p>
        <p>
            More than just a project, AI CV Analyzer represents my journey of learning,
            building, and turning ideas into practical tools that can help people in real life.
        </p>
        <p>
            My goal is to create technology that is simple, useful, and accessible to everyone.
        </p>
        <div class="about-signature">Thank you for visiting and supporting the project.</div>
    </div>
    """).strip()
    links_html = textwrap.dedent(f"""
    <div class="about-panel">
        <div class="about-kicker">Features</div>
        <h2>What It Helps With</h2>
        <div class="about-feature-grid">
            <div class="about-feature">AI-powered CV analysis</div>
            <div class="about-feature">ATS compatibility checking</div>
            <div class="about-feature">Keyword and skill detection</div>
            <div class="about-feature">Personalized suggestions</div>
            <div class="about-feature">Simple and fast user experience</div>
        </div>
        <div style="height: 22px;"></div>
        <div class="about-kicker">Connect With Me</div>
        <h2>Find My Work</h2>
        <div class="about-links">
            {portfolio_link}
            {github_link}
            {linkedin_link}
            {instagram_link}
        </div>
        <div class="about-signature">
            Links point to my portfolio, GitHub, LinkedIn, and Instagram profiles.
        </div>
    </div>
    """).strip()

    about_story_col, about_links_col = st.columns([1.25, 0.75], gap="large")

    with about_story_col:
        st.html(story_html)

    with about_links_col:
        st.html(links_html)

    return

    st.markdown(
        textwrap.dedent(f"""
        <div class="about-shell">
            <div class="about-panel">
                <div class="about-kicker">The Story</div>
                <h2>Hi, I'm Ayoub Louraoui.</h2>
                <p>
                    I'm an AI and Data enthusiast passionate about building smart and useful
                    digital solutions.
                </p>
                <p>
                    AI CV Analyzer was created from a simple observation: many talented people
                    struggle to get interviews not because they lack skills, but because their CVs
                    are not optimized for modern recruitment systems.
                </p>
                <p>
                    As someone interested in Artificial Intelligence and data-driven technologies,
                    I wanted to build a project that solves a real problem while also reflecting my
                    passion for AI and web development.
                </p>
                <p>That's how AI CV Analyzer was born.</p>
                <p>
                    This platform uses Artificial Intelligence to analyze resumes, detect strengths
                    and weaknesses, identify important keywords, and provide smart suggestions to
                    help users improve their CVs and become more ATS-friendly.
                </p>
                <p>
                    More than just a project, AI CV Analyzer represents my journey of learning,
                    building, and turning ideas into practical tools that can help people in real life.
                </p>
                <p>
                    My goal is to create technology that is simple, useful, and accessible to everyone.
                </p>
                <div class="about-signature">Thank you for visiting and supporting the project 🚀</div>
            </div>

            <div class="about-panel">
                <div class="about-kicker">Features</div>
                <h2>What It Helps With</h2>
                <div class="about-feature-grid">
                    <div class="about-feature">AI-powered CV analysis</div>
                    <div class="about-feature">ATS compatibility checking</div>
                    <div class="about-feature">Keyword and skill detection</div>
                    <div class="about-feature">Personalized suggestions</div>
                    <div class="about-feature">Simple and fast user experience</div>
                </div>

                <div style="height: 22px;"></div>
                <div class="about-kicker">Connect With Me</div>
                <h2>Find My Work</h2>
                <div class="about-links">
                    {portfolio_link}
                    {github_link}
                    {linkedin_link}
                    {instagram_link}
                </div>
                <div class="about-signature">
                    Links point to my portfolio, GitHub, LinkedIn, and Instagram profiles.
                </div>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True
    )


def render_footer():
    st.html(
        """
        <footer class="site-footer">
            <div>&copy; 2026 Ayoub Louraoui &middot; Casablanca, Morocco</div>
            <div>Built and coded by <a class="site-footer-name" href="https://www.instagram.com/ayoublouraoui_/" target="_blank" rel="noopener noreferrer">Ayoub</a></div>
        </footer>
        """
    )


def get_admin_user_fields(user):
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "password": user[3] if len(user) > 3 else "",
        "social_provider": user[4] if len(user) > 4 else "",
        "social_sub": user[5] if len(user) > 5 else "",
        "profile_image": user[6] if len(user) > 6 else "",
        "password_created": bool(user[7]) if len(user) > 7 and user[7] is not None else bool((user[3] if len(user) > 3 else "") and not (user[4] if len(user) > 4 else "")),
        "password_created_at": user[8] if len(user) > 8 else "",
    }


def get_admin_account_type(user):
    fields = get_admin_user_fields(user)
    provider = (fields["social_provider"] or "").strip().lower()

    if provider == "google":
        return "Google"
    if provider:
        return provider.title()

    return "Application"


def admin_html(value):
    return html.escape("" if value is None else str(value))


def admin_pill(label, variant="slate"):
    safe_label = admin_html(label)
    safe_variant = admin_html(variant)
    return f"<span class='admin-pill {safe_variant}'>{safe_label}</span>"


def render_admin_table(title, subtitle, columns, rows):
    table_head = "".join(f"<th>{admin_html(label)}</th>" for _, label in columns)

    if rows:
        table_rows = []

        for row in rows:
            cells = "".join(f"<td>{row.get(key, '')}</td>" for key, _ in columns)
            table_rows.append(f"<tr>{cells}</tr>")

        table_body = "".join(table_rows)
    else:
        table_body = (
            f"<tr><td colspan='{len(columns)}' class='admin-muted'>No records found yet.</td></tr>"
        )

    st.markdown(
        f"""
        <div class="admin-table-card">
            <div class="admin-table-head">
                <div>
                    <div class="admin-table-title">{admin_html(title)}</div>
                    <div class="admin-table-subtitle">{admin_html(subtitle)}</div>
                </div>
                <div class="admin-table-count">{len(rows)}</div>
            </div>
            <div class="admin-table-scroll">
                <table class="admin-table">
                    <thead><tr>{table_head}</tr></thead>
                    <tbody>{table_body}</tbody>
                </table>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_admin_users_table(users):
    rows = []

    for user in users:
        fields = get_admin_user_fields(user)
        account_type = get_admin_account_type(user)
        provider = (fields["social_provider"] or "").strip().lower()
        account_variant = "blue" if provider == "google" else "green"
        has_created_password = bool(fields["password"]) and bool(fields["password_created"])

        rows.append({
            "id": f"<span class='admin-id'>#{admin_html(fields['id'])}</span>",
            "username": f"<span class='admin-strong'>{admin_html(fields['username'])}</span>",
            "email": f"<span class='admin-muted'>{admin_html(fields['email'] or 'No email')}</span>",
            "type": admin_pill(account_type, account_variant),
            "password": admin_pill("Created" if has_created_password else "Uncreated", "green" if has_created_password else "amber"),
            "google": admin_pill("Linked" if provider == "google" else "Not linked", "blue" if provider == "google" else "slate"),
        })

    render_admin_table(
        "Users",
        "Accounts registered in your AI CV Analyzer workspace.",
        [
            ("id", "ID"),
            ("username", "Username"),
            ("email", "Email"),
            ("type", "Account Type"),
            ("password", "Password"),
            ("google", "Google"),
        ],
        rows
    )


def get_activity_variant(action):
    action_text = (action or "").lower()

    if "delete" in action_text or "remove" in action_text:
        return "red"
    if "reset" in action_text or "password" in action_text or "update" in action_text or "changed" in action_text:
        return "amber"
    if "login" in action_text:
        return "blue"
    if "register" in action_text or "upload" in action_text or "created" in action_text:
        return "green"

    return "slate"


def format_activity_action(action):
    action_text = str(action or "").strip()

    if action_text.lower() == "password_update":
        return "password_changed"

    return action_text


def render_admin_activity_table(activities, username_filter=None):
    rows = []
    subtitle = "Latest actions tracked across accounts, CV uploads, and security changes."

    if username_filter:
        subtitle = f"Latest actions for {username_filter}."

    for activity in activities:
        action_label = format_activity_action(activity[2])
        rows.append({
            "id": f"<span class='admin-id'>#{admin_html(activity[0])}</span>",
            "username": f"<span class='admin-strong'>{admin_html(activity[1])}</span>",
            "action": admin_pill(action_label, get_activity_variant(action_label)),
            "details": f"<div class='admin-details-cell'>{admin_html(activity[3])}</div>",
            "created_at": f"<span class='admin-muted'>{admin_html(activity[4])}</span>",
        })

    render_admin_table(
        "User Activity",
        subtitle,
        [
            ("id", "ID"),
            ("username", "Username"),
            ("action", "Action"),
            ("details", "Details"),
            ("created_at", "Created At"),
        ],
        rows
    )


def has_password_activity(activities):
    password_actions = {
        "password_create",
        "password_changed",
        "password_update",
        "password_reset",
    }

    return any(
        str(activity[2] or "").strip().lower() in password_actions
        for activity in activities
    )


def clear_forgot_password_state(keep_open=False):
    st.session_state.forgot_password_open = keep_open
    st.session_state.forgot_password_code = ""
    st.session_state.forgot_password_email = ""
    st.session_state.forgot_password_user_id = None
    st.session_state.forgot_password_username = ""


def render_forgot_password_panel():
    st.markdown("#### Reset password")
    st.caption("Enter the email linked to your account. We will send a confirmation code first.")

    reset_email = st.text_input(
        "Account email",
        key="forgot_password_email_input",
        placeholder="you@example.com"
    )

    send_reset_code_col, close_reset_col = st.columns([1, 1])

    with send_reset_code_col:
        if st.button("Send reset code", use_container_width=True, key="forgot_password_send_code"):
            normalized_email = reset_email.strip().lower()

            if not normalized_email or not is_valid_email(normalized_email):
                st.error("Please enter a valid email address.")
            else:
                user = get_user_by_email_safe(normalized_email)
                reset_username = ""
                reset_user_id = None

                if user:
                    reset_user_id = user[0]
                    reset_username = user[1]
                else:
                    reset_username = get_admin_reset_username_for_email(normalized_email)

                if not reset_username:
                    st.error("No account was found with this email.")
                else:
                    code = generate_verification_code()
                    sent, message = send_verification_email(normalized_email, code)

                    if sent:
                        st.session_state.forgot_password_code = code
                        st.session_state.forgot_password_email = normalized_email
                        st.session_state.forgot_password_user_id = reset_user_id
                        st.session_state.forgot_password_username = reset_username
                        st.success(message)
                    else:
                        st.error(message)

    with close_reset_col:
        if st.button("Back to login", use_container_width=True, key="forgot_password_back"):
            clear_forgot_password_state(keep_open=False)
            st.rerun()

    if st.session_state.forgot_password_code:
        st.info("A confirmation code was sent to your email. Enter it before choosing a new password.")

        reset_code = st.text_input(
            "Confirmation code",
            key="forgot_password_code_input",
            placeholder="6-digit code"
        )
        new_password = st.text_input(
            "New password",
            type="password",
            key="forgot_password_new_password",
            placeholder="Enter a new password"
        )
        confirm_new_password = st.text_input(
            "Confirm new password",
            type="password",
            key="forgot_password_confirm_password",
            placeholder="Repeat the new password"
        )

        if st.button("Reset password and open dashboard", use_container_width=True, key="forgot_password_reset"):
            normalized_email = reset_email.strip().lower()

            if normalized_email != st.session_state.forgot_password_email:
                st.error("Please use the same email that received the code.")
            elif reset_code.strip() != st.session_state.forgot_password_code:
                st.error("Invalid confirmation code.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != confirm_new_password:
                st.error("Passwords do not match.")
            elif not st.session_state.forgot_password_username:
                st.error("Reset session expired. Please send a new code.")
            else:
                try:
                    username = st.session_state.forgot_password_username
                    if st.session_state.forgot_password_user_id:
                        update_user_password_safe(st.session_state.forgot_password_user_id, new_password)
                    else:
                        existing_admin_user = database.get_user(username)

                        if existing_admin_user:
                            update_user_password_safe(existing_admin_user[0], new_password)
                        else:
                            register_user(username, st.session_state.forgot_password_email, new_password)

                    add_user_activity_safe(username, "password_reset", "Password reset with email verification.")
                    clear_forgot_password_state(keep_open=False)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.display_name = username
                    st.session_state.is_admin = is_admin_user(username)
                    st.session_state.auth_message = ""
                    set_flash_success("Password reset successfully. Welcome back.")
                    st.rerun()
                except Exception:
                    st.error("Could not reset your password. Please try again.")


# =======================
# LOGIN / REGISTER
# =======================

if not st.session_state.logged_in:
    render_oauth_return_listener()

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
                    st.session_state.display_name = login_username
                    st.session_state.is_admin = is_admin_user(login_username)
                    st.session_state.auth_message = ""
                    add_user_activity_safe(login_username, "login", "User logged in")
                    set_flash_success(f"Welcome {login_username}. Login successful.")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            if st.button("Forgot password?", use_container_width=True, key="forgot_password_toggle"):
                st.session_state.forgot_password_open = not st.session_state.forgot_password_open
                if not st.session_state.forgot_password_open:
                    clear_forgot_password_state(keep_open=False)
                st.rerun()

            if st.session_state.forgot_password_open:
                render_forgot_password_panel()

            st.markdown(
                "<div style='text-align:center;margin:10px 0 8px;font-size:11.5px;color:#6f8499;letter-spacing:0.08em;'>OR CONTINUE WITH</div>",
                unsafe_allow_html=True
            )

            if st.button("Continue with Google", help="Continue with Google", use_container_width=True, key="google_login"):
                start_social_login("google")

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
                        st.session_state.display_name = new_username
                        st.session_state.is_admin = is_admin_user(new_username)
                        st.session_state.auth_message = ""
                        st.session_state.verification_code = ""
                        st.session_state.verification_email = ""
                        st.session_state.email_verified = False
                        add_user_activity_safe(new_username, "register", "Account created")
                        set_flash_success(f"Account created successfully. Welcome {new_username}.")
                        st.rerun()
                    except Exception:
                        st.error("❌ Username or email already exists")

            st.markdown(
                "<div style='text-align:center;margin:10px 0 8px;font-size:11.5px;color:#6f8499;letter-spacing:0.08em;'>OR CREATE ACCOUNT WITH</div>",
                unsafe_allow_html=True
            )

            st.caption(
                "Google, GitHub, or Facebook will create your account automatically and redirect you to your dashboard."
            )

            if st.button("Continue with Google", help="Create account with Google", use_container_width=True, key="google_reg"):
                start_social_login("google")

    render_footer()
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
    welcome_name = st.session_state.display_name or st.session_state.username
    is_admin = st.session_state.is_admin or is_admin_user(st.session_state.username)
    avatar_letter = (welcome_name.strip()[:1] or "U").upper()
    sidebar_user = get_current_user_safe()
    sidebar_profile_image = get_user_profile_image(sidebar_user)

    if sidebar_profile_image:
        st.markdown(
            f"""
            <style>
            .st-key-profile_circle button {{
                background: transparent !important;
                background-color: transparent !important;
                color: transparent !important;
            }}

            .st-key-profile_circle button::before {{
                content: "" !important;
                position: absolute !important;
                inset: 0 !important;
                border-radius: 50% !important;
                background: url({json.dumps(sidebar_profile_image)}) center center / cover no-repeat !important;
                z-index: 0 !important;
            }}

            .st-key-profile_circle button p {{
                color: transparent !important;
                opacity: 0 !important;
                position: relative !important;
                z-index: 1 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    profile_avatar_col, profile_name_col = st.columns([0.25, 0.75], vertical_alignment="center")
    with profile_avatar_col:
        if st.button(avatar_letter, key="profile_circle", help="Open account menu"):
            st.session_state.profile_menu_open = not st.session_state.profile_menu_open
            st.rerun()
    with profile_name_col:
        safe_welcome_name = html.escape(welcome_name)
        st.markdown(
            f"""
            <div class="profile-name">{safe_welcome_name}</div>
            <div class="profile-hint">Click the circle for menu</div>
            """,
            unsafe_allow_html=True
        )

    if is_admin:
        if st.session_state.get("admin_page") not in ["Admin Dashboard", "CV Analyzer", "Account Settings", "About"]:
            st.session_state.admin_page = "Admin Dashboard"
        admin_page = st.session_state.admin_page
    else:
        if st.session_state.get("user_page") not in ["CV Analyzer", "Account Settings", "About"]:
            st.session_state.user_page = "CV Analyzer"
        admin_page = st.session_state.user_page

    if st.session_state.profile_menu_open:
        st.markdown("<div class='profile-menu-title'>Account menu</div>", unsafe_allow_html=True)

        if is_admin:
            if st.button("Dashboard", use_container_width=True, key="profile_menu_dashboard"):
                st.session_state.admin_page = "Admin Dashboard"
                st.session_state.profile_menu_open = False
                st.rerun()

        if st.button("CV Analyzer", use_container_width=True, key="profile_menu_cv"):
            if is_admin:
                st.session_state.admin_page = "CV Analyzer"
            else:
                st.session_state.user_page = "CV Analyzer"
            st.session_state.profile_menu_open = False
            st.rerun()

        if st.button("Account Settings", use_container_width=True, key="profile_menu_account"):
            if is_admin:
                st.session_state.admin_page = "Account Settings"
            else:
                st.session_state.user_page = "Account Settings"
            st.session_state.profile_menu_open = False
            st.rerun()

        if st.button("About", use_container_width=True, key="profile_menu_about"):
            if is_admin:
                st.session_state.admin_page = "About"
            else:
                st.session_state.user_page = "About"
            st.session_state.profile_menu_open = False
            st.rerun()

        if st.button("Logout", use_container_width=True, key="profile_menu_logout"):
            logout_name = st.session_state.display_name or st.session_state.username
            add_user_activity_safe(st.session_state.username, "logout", "User logged out")
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.display_name = ""
            st.session_state.is_admin = False
            st.session_state.auth_message = ""
            st.session_state.profile_menu_open = False
            set_flash_success(f"{logout_name} logged out successfully.")
            if is_social_login_active():
                st.logout()
            st.rerun()

    if is_admin:
        st.success("Admin mode")

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
# ADMIN DASHBOARD
# =======================

if admin_page == "Account Settings":
    render_account_settings()
    render_footer()
    st.stop()


if admin_page == "About":
    render_about_page()
    render_footer()
    st.stop()


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
    selected_activity_username = None

    c1, c2, c3 = st.columns(3)
    c1.metric("Users", len(users))
    c2.metric("CV Uploads", len(uploads))
    c3.metric("Activities", len(activities))

    if users:
        render_admin_users_table(users)

        st.markdown("<div class='admin-manage-title'>Manage User</div>", unsafe_allow_html=True)

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
        selected_fields = get_admin_user_fields(selected_user)
        selected_account_type = get_admin_account_type(selected_user)
        selected_activity_username = selected_fields["username"]
        selected_has_created_password = bool(selected_fields["password"]) and bool(selected_fields["password_created"])

        st.write("#### User Details")
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        detail_col1.metric("User ID", selected_fields["id"])
        detail_col2.metric("Account Type", selected_account_type)
        detail_col3.metric("Password", "Created" if selected_has_created_password else "Uncreated")
        detail_col4.metric(
            "Google",
            "Linked" if selected_fields["social_provider"] == "google" else "Not linked"
        )

        st.caption(f"Email: {selected_fields['email'] or 'No email'}")

        if selected_fields["social_provider"]:
            st.info(
                f"This user registered or logged in with {selected_account_type}. "
                "You can still update the email, reset the password, unlink Google, or delete the account."
            )
        else:
            st.info("This user registered normally from the application.")

        edit_username = st.text_input(
            "Username",
            value=selected_fields["username"],
            key=f"admin_edit_username_{selected_fields['id']}"
        )
        edit_email = st.text_input(
            "Email",
            value=selected_fields["email"] or "",
            key=f"admin_edit_email_{selected_fields['id']}"
        )
        reset_password = st.text_input(
            "Reset password",
            type="password",
            key=f"admin_reset_password_{selected_fields['id']}",
            placeholder="Enter a new password for this user"
        )

        col_edit, col_reset, col_unlink, col_delete = st.columns(4)

        with col_edit:
            if st.button("Update User", use_container_width=True):
                st.session_state.confirm_update_user_id = selected_fields["id"]
                st.session_state.confirm_delete_user_id = None
                st.session_state.confirm_reset_password_user_id = None
                st.session_state.confirm_unlink_social_user_id = None

        with col_reset:
            if st.button("Reset Password", use_container_width=True):
                st.session_state.confirm_reset_password_user_id = selected_fields["id"]
                st.session_state.confirm_update_user_id = None
                st.session_state.confirm_delete_user_id = None
                st.session_state.confirm_unlink_social_user_id = None

        with col_unlink:
            if st.button("Unlink Google", use_container_width=True, disabled=selected_fields["social_provider"] != "google"):
                st.session_state.confirm_unlink_social_user_id = selected_fields["id"]
                st.session_state.confirm_update_user_id = None
                st.session_state.confirm_delete_user_id = None
                st.session_state.confirm_reset_password_user_id = None

        with col_delete:
            if st.button("Delete User", use_container_width=True):
                st.session_state.confirm_delete_user_id = selected_fields["id"]
                st.session_state.confirm_update_user_id = None
                st.session_state.confirm_reset_password_user_id = None
                st.session_state.confirm_unlink_social_user_id = None

        if st.session_state.confirm_update_user_id == selected_fields["id"]:
            st.warning(
                f"Confirm update for user '{selected_fields['username']}'?"
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
                            update_user_safe(selected_fields["id"], edit_username, edit_email)
                            if selected_fields["username"] == st.session_state.username:
                                st.session_state.username = edit_username
                                st.session_state.display_name = edit_username
                            st.session_state.confirm_update_user_id = None
                            set_flash_success("User updated successfully.")
                            st.rerun()
                        except Exception:
                            st.error("Could not update user. Username or email may already exist.")

            with cancel_update:
                if st.button("Cancel update", use_container_width=True):
                    st.session_state.confirm_update_user_id = None
                    st.rerun()

        if st.session_state.confirm_reset_password_user_id == selected_fields["id"]:
            st.warning(f"Confirm password reset for user '{selected_fields['username']}'?")
            confirm_reset, cancel_reset = st.columns(2)

            with confirm_reset:
                if st.button("Yes, reset password", use_container_width=True):
                    if not reset_password or len(reset_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            update_user_password_safe(selected_fields["id"], reset_password)
                            add_user_activity_safe(
                                selected_fields["username"],
                                "password_changed" if selected_has_created_password else "password_create",
                                "Admin changed this user's platform password."
                            )
                            st.session_state.confirm_reset_password_user_id = None
                            set_flash_success("Password changed successfully.")
                            st.rerun()
                        except Exception:
                            st.error("Could not reset password.")

            with cancel_reset:
                if st.button("Cancel password reset", use_container_width=True):
                    st.session_state.confirm_reset_password_user_id = None
                    st.rerun()

        if st.session_state.confirm_unlink_social_user_id == selected_fields["id"]:
            st.warning(
                f"Confirm unlink Google login for user '{selected_fields['username']}'?"
            )
            confirm_unlink, cancel_unlink = st.columns(2)

            with confirm_unlink:
                if st.button("Yes, unlink Google", use_container_width=True):
                    try:
                        clear_user_social_identity_safe(selected_fields["id"])
                        st.session_state.confirm_unlink_social_user_id = None
                        set_flash_success("Google login unlinked successfully.")
                        st.rerun()
                    except Exception:
                        st.error("Could not unlink Google login.")

            with cancel_unlink:
                if st.button("Cancel unlink", use_container_width=True):
                    st.session_state.confirm_unlink_social_user_id = None
                    st.rerun()

        if st.session_state.confirm_delete_user_id == selected_fields["id"]:
            st.warning(
                f"Confirm delete for user '{selected_fields['username']}'? This action cannot be undone."
            )
            confirm_delete, cancel_delete = st.columns(2)

            with confirm_delete:
                if st.button("Yes, delete user", use_container_width=True):
                    if selected_fields["username"] == st.session_state.username:
                        st.error("You cannot delete the account you are currently using.")
                    else:
                        try:
                            delete_user_safe(selected_fields["id"])
                            st.session_state.confirm_delete_user_id = None
                            set_flash_success("User deleted successfully.")
                            st.rerun()
                        except Exception:
                            st.error("Could not delete user.")

            with cancel_delete:
                if st.button("Cancel delete", use_container_width=True):
                    st.session_state.confirm_delete_user_id = None
                    st.rerun()
    else:
        render_admin_users_table([])

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

    selected_user_activities = [
        activity
        for activity in activities
        if selected_activity_username
        and str(activity[1] or "").strip().lower() == selected_activity_username.strip().lower()
    ]

    if (
        selected_activity_username
        and users
        and selected_fields["social_provider"] == "google"
        and selected_has_created_password
        and not has_password_activity(selected_user_activities)
    ):
        selected_user_activities.insert(
            0,
            (
                "status",
                selected_activity_username,
                "password_create",
                "Platform password is created for this Google-linked account.",
                selected_fields["password_created_at"] or "Not recorded"
            )
        )

    render_admin_activity_table(selected_user_activities, selected_activity_username)

    render_footer()
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
            st.success("CV uploaded and analysis saved successfully.")


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

render_footer()
