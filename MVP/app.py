import streamlit as st
from streamlit import Page
from constants import BASE_DIR
import os

st.set_page_config(page_title="TV Track Dashboard", layout="wide", page_icon="📺")
pages_dir = os.path.join(BASE_DIR, 'pages')

pages = [
    Page(os.path.join(pages_dir, "home.py"), title="🏠 Home"),
    Page(os.path.join(pages_dir, "faq.py"), title="❓ FAQ"),
    Page(os.path.join(pages_dir, "contact.py"), title="📬 Contact Us"),
    Page(os.path.join(pages_dir, "admin.py"), title="🔐 Admin"),
]

pg = st.navigation(pages, position="top")
pg.run()