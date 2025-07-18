import streamlit as st
import os 
from constants import BASE_DIR
# from constants import USERNAME

def _local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_contact_us():
    st.markdown(
        "<h2 style='text-align: center'>Get in Touch with us!</h2>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([0.5, 2, 0.5])

    with col1:
        st.write("")

    with col2:
        contact_form = """
            <form action="https://formsubmit.co/Sumit.Chaudhary@jiostar.com" method="POST" enctype="multipart/form-data">
                <input type='hidden' name="_captcha" value="false">
                <input type="text" name="name" placeholder="Your Name" required>
                <input type="email" name="email" placeholder="Your Email" required>
                <textarea name="message" placeholder="Details of your problem" rows="6" required></textarea>
                <button type="submit">Send</button>
            </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)

        # Load local CSS
        _local_css("style/style.css")

    with col3:
        st.write("")

if "user" not in st.session_state:
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={os.environ.get("BASE_URL")}">', unsafe_allow_html=True)

with st.sidebar:
    st.image(os.path.join(BASE_DIR, "media","tracks_logo.png"), width=150)
    st.markdown(f"👤 **User:** `{st.session_state.user}`")
    st.markdown("📺 **TV Track Dashboard**")
    st.markdown("---")
    st.markdown("Use the top navigation bar to switch pages.")

get_contact_us()
