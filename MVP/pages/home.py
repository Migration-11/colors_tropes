import os
import streamlit as st
import pandas as pd
from streamlit_card import card
from constants import DATA_PATH, DB_PATH, CHAT_DB_PATH, USERS_DB_PATH
from modules.data_utils import load_data, load_interactions_db, load_context_db, save_db, load_users
from modules.ui_utils import getTotal_likes_comments_views, chat_ui, updateViewCount, display_comments
from logger import get_logger

logger = get_logger(__file__)

if "user" not in st.session_state:
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={os.environ.get("BASE_URL")}">', unsafe_allow_html=True)

def home_page() -> None:
    df = load_data(DATA_PATH)
    USERS = load_users(USERS_DB_PATH, st.session_state.user)
    db_df = load_interactions_db(DB_PATH, USERS, df)
    
    if "selected_card" not in st.session_state:
        st.session_state.selected_card = None
    if 'db_df' not in st.session_state:
        st.session_state.db_df = db_df.copy()
    
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/48/film-reel.png", width=100) 
        st.markdown(f"👤 **User:** `{st.session_state.user}`")
        

            
        st.markdown("📺 **TV Track Dashboard**")
        st.markdown("---")
        st.markdown("Use the top navigation bar to switch pages.")
        
    st.title("🎬 TV Show Tracks Dashboard")
    
    if st.session_state.selected_card is None:
        view_mode = "Expanded" if st.toggle("🔀 View Mode: Expanded", value=False) else "Compact"
        st.session_state.messages = []
        if "prev_stream" in st.session_state:
            del st.session_state.prev_stream    
    
    if st.session_state.selected_card is not None:
        idx = st.session_state.selected_card
        row = df.iloc[idx]
        current_user = st.session_state.user
        db = st.session_state.db_df
        
        if st.button("🔙 Back to All Tracks"):
            st.session_state.selected_card = None
            st.rerun()
        
        st.markdown(f"""
            <div style="background-color:#fff; padding:20px 25px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); margin-bottom:20px">
                <h3>🎞️ {str(row.get('Track Name', ''))}</h3>
                <p><strong>📺 Show Name:</strong> {str(row.get('Show Name', ''))}</p>
                <p><strong>📝 Track Details:</strong><br>{str(row.get('Track in detail (Character traits add)', ''))}</p>
            </div>
        """, unsafe_allow_html=True)
        
        total_likes = db[db['track_id'] == idx]['liked'].sum()
        
        user_has_liked = db[(db['track_id'] == idx) & (db['username'] == current_user)]['liked'].iloc[0] == 1
        like_button_text = "👎 Unlike" if user_has_liked else "👍 Like"
        like_button_key = f"like_{idx}_{current_user}"
        
        col1, _, col2 = st.columns([3, 3, 0.7])
        with col1:
            if st.button(f"{like_button_text} ({total_likes})", key=like_button_key):
                try:
                    row_index = db.index[(db['track_id'] == idx) & (db['username'] == current_user)][0]
                    db.loc[row_index, 'liked'] = 1 - db.loc[row_index, 'liked']
                    
                    save_db(db, DB_PATH)
                    st.session_state.db_df = db.copy() 
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"Error in updating Like button, Error: {e}")
                    
    
        with col2:
            if st.button("**Ask AI**💡", use_container_width= True):
                chat_ui(load_context_db(CHAT_DB_PATH, USERS, df), row)
                
        with st.container(border=True):
            display_comments(idx, USERS, df, current_user)
    
    elif view_mode == "Compact":
        st.markdown("### 🧭 Click a card to view full track details")
        cols = st.columns(3)
        for idx, row in df.iterrows():
            col = cols[idx % 3]
            with col:
                total_likes, total_comments, total_views = getTotal_likes_comments_views(idx)
                clicked = card(
                    title=str(row.get("Track Name", "")),
                    text=[str(row.get("Show Name", "")), f"👍: {total_likes} | 💬: {total_comments} | 👁️: {total_views}"],
                    styles={"card": {"width": "100%", "margin": "10px 0px"}},
                    key=f"card_{idx}"
                )
                
                if clicked:
                    st.session_state.selected_card = idx
                    updateViewCount(st.session_state.selected_card)
                    
                    st.rerun()
    
    elif view_mode == "Expanded":
        st.markdown("### 📖 Browse Full Track Previews")
        cols = st.columns(2)
        for idx, row in df.iterrows():
            with cols[idx % 2]:
                with st.container(border=True, height=350):
                    total_likes, total_comments, total_views = getTotal_likes_comments_views(idx)
                
                    st.markdown(f"""
                        <h4>🎞️ {str(row.get('Track Name', ''))}</h4>
                        <p><strong>📺 Show:</strong> {str(row.get('Show Name', ''))}</p>
                        <p><strong>📝 Track:</strong><br>
                        {str(row.get('Track in detail (Character traits add)', ''))[:200]}...</p>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**👍 Likes:** {total_likes} | **💬 Comments:** {total_comments} | **👁️ Views:** {total_views}")
                    if st.button("👁️ View Full Track", key=f"view_{idx}"):
                        st.session_state.selected_card = idx
                        updateViewCount(st.session_state.selected_card)
                        st.rerun()

if __name__ == '__main__':
    home_page()