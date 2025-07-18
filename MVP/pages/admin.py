import streamlit as st
import pandas as pd
import os
import shutil
from constants import DATA_PATH, BASE_DIR
from logger import get_logger

logger = get_logger(__file__)

if "user" not in st.session_state:
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={os.environ.get("BASE_URL")}">', unsafe_allow_html=True)

with st.sidebar:
    st.image(os.path.join(BASE_DIR, "media","tracks_logo.png"), width=150)
    
    st.markdown(f"👤 **User:** `{st.session_state.user}`")
    st.markdown("📺 **TV Track Dashboard**")
    st.markdown("---")
    st.markdown("Use the top navigation bar to switch pages.")

st.title("🔐 Admin Dashboard")


st.markdown("### 📤 Upload New Data File")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Backup old file
        backup_path = DATA_PATH.replace(".xlsx", "_old.xlsx")
        if os.path.exists(DATA_PATH):
            shutil.move(DATA_PATH, backup_path)
            st.info(f"Previous file backed up to: `{backup_path}`")

        # Save new file
        with open(DATA_PATH, "wb") as f:
            f.write(uploaded_file.read())
        st.success("✅ New data file uploaded and linked!")

    except Exception as e:
        st.error(f"❌ Error while replacing file: {e}")

# Show the current file being used
st.markdown("### 📊 Currently Linked Data File")
try:
    df = pd.read_excel(DATA_PATH)
    st.dataframe(df.head(20), use_container_width=True)
except Exception as e:
    st.error(f"Failed to read current data file")
    logger.error(f"Failed to read current data file {e}")
