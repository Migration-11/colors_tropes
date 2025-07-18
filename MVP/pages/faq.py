import streamlit as st
import os 
from constants import BASE_DIR
# from constants import USERNAME

if "user" not in st.session_state:
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={os.environ.get("BASE_URL")}">', unsafe_allow_html=True)

with st.sidebar:
    st.image(os.path.join(BASE_DIR, "media","tracks_logo.png"), width=150)
    st.markdown(f"👤 **User:** `{st.session_state.user}`")
    st.markdown("📺 **TV Track Dashboard**")
    st.markdown("---")
    st.markdown("Use the top navigation bar to switch pages.")


st.title("❓ Frequently Asked Questions")

with st.expander("What is this app about?"):
    st.write("It helps you explore and interact with TV show story tracks.")

with st.expander("Can I suggest new tracks?"):
    st.write("This feature is coming soon!")