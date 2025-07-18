import os
import streamlit as st
from streamlit import Page
from constants import BASE_DIR
from logger import get_logger, get_remote_ip, get_session_id
from auth import AuthMiddleware, RedisCacheManager

logger = get_logger(__file__)
st.set_page_config(page_title="TV Track Dashboard", layout="wide", page_icon="📺")

# --- SSO Authentication Setup ---
initial_token = st.query_params.get("auth_token", None)
if "auth_token" in st.query_params:
    st.query_params.clear()
FORCE_AUTH = os.environ.get('FORCE_AUTH', "FALSE").lower() == "true"
LOGIN_URL = f"{os.environ.get('LOGIN_URL')}?applicationName={os.environ.get('APPLICATION_NAME')}&redirectUrl={os.environ.get('BASE_URL')}"
SSO_LOGOUT_URL = os.environ.get('LOGOUT_URL')

# Initialize Redis cache manager
redis_manager = RedisCacheManager(
    host=os.environ.get('REDIS_HOST'),
    port=int(os.environ.get('REDIS_PORT')),
    db=int(os.environ.get('REDIS_DB')),
    protocol=int(os.environ.get('REDIS_PROTOCOL'))
)

# Initialize authentication middleware
# This will handle user authentication and session management
# It will also manage the retrieval of user information and tokens
auth = AuthMiddleware(
    redis_manager=redis_manager,
    BASE_URL=os.environ.get('BASE_URL'),
    HEALTH_CHECK_URL=os.environ.get('HEALTH_CHECK_URL'),
    VERIFY_AUTH_URL=os.environ.get('VERIFY_AUTH_URL'),
    LOGOUT_URL=os.environ.get('LOGOUT_URL')
)


ip_addr = get_remote_ip()
session_id = get_session_id(page=True)

# --- Authentication Check ---
if auth.ready(st) and auth.authorize(force=FORCE_AUTH, session_id=session_id, st=st, auth_token=initial_token):
    # Retrieve user info and token
    user = auth.get_user_info(session_id=session_id, st=st, ip=ip_addr)
    token = auth._retrieve_token(session_id, st)

    if user:
        # Set user name in session state
        user_name = user.get("name") or user.get("mail") or user.get("email") or "User"
        st.sidebar.markdown(f"**Welcome, {user_name}!**")
        st.session_state.user = user_name

    if st.sidebar.button("Logout"):
        # Clear session state and redirect to logout URL
        LOGOUT_URL = f"{SSO_LOGOUT_URL}?auth_token={token}&redirectUrl={os.environ.get('BASE_URL')}"
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={LOGOUT_URL}">', unsafe_allow_html=True)
    else:
        pages_dir = os.path.join(BASE_DIR, 'pages')

        pages = [
            Page(os.path.join(pages_dir, "home.py"), title="🏠 Home"),
            Page(os.path.join(pages_dir, "faq.py"), title="❓ FAQ"),
            Page(os.path.join(pages_dir, "contact.py"), title="📬 Contact Us"),
            Page(os.path.join(pages_dir, "admin.py"), title="🔐 Admin"),
        ]

        pg = st.navigation(pages, position="top")
        pg.run()
else:
    logger.info("Redirecting to login page...")
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={LOGIN_URL}">', unsafe_allow_html=True)
