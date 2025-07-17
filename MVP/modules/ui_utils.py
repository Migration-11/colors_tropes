import time 
import streamlit as st
from modules.data_utils import save_db
from modules.llm_utils import LLM_response
from constants import CHAT_DB_PATH, DB_PATH
from logger import get_logger

logger = get_logger(__file__)

def getTotal_likes_comments_views(idx):
    try:
        total_likes = st.session_state.db_df[st.session_state.db_df['track_id'] == idx]['liked'].sum()
        total_comments = st.session_state.db_df[st.session_state.db_df['track_id'] == idx]['comments'].apply(len).sum()
        total_views = st.session_state.db_df[st.session_state.db_df['track_id'] == idx]['views'].sum()
    
        return total_likes, total_comments, total_views
        
    except Exception as e:
        logger.error(f"Error in getting total likes comments views, Error: {e}")
        return 0,0,0

def updateViewCount(idx):
    try:
        row_index = st.session_state.db_df.index[(st.session_state.db_df['track_id'] == idx) & (st.session_state.db_df['username'] == st.session_state.user)][0]
        st.session_state.db_df.loc[row_index, 'views'] += 1
        save_db(st.session_state.db_df, DB_PATH)
    
    except Exception as e:
        logger.error(f"Error in updating view count, Error: {e}")


def stream_message(message):
    for line in message.splitlines():
        for word in line:
            yield word 
            time.sleep(0.009)
        yield "\n"
        
@st.fragment
def display_chat(db, creativity_level, show_name, show_desc, track):
    st.session_state.messages = db.loc[st.session_state.user_index, 'chat_history']    
    if "prev_stream" not in st.session_state:
        st.session_state.prev_stream = len(st.session_state.messages)-1 if st.session_state.messages else 0
        
    for idx,  msg in enumerate(st.session_state.messages):
        if idx == len(st.session_state.messages)-1 and idx != st.session_state.prev_stream:
            st.chat_message(msg["role"]).write_stream(stream_message(msg["content"]))
            st.session_state.prev_stream = idx 
        else:
            st.chat_message(msg["role"]).write(msg["content"])
    
    col1, col2 = st.columns([3, 0.4])
    with col1:
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."): 
                response = LLM_response(creativity_level, show_name, show_desc, track)
            logger.info("reply received")
            st.session_state.messages.append({"role": "assistant", "content": response})

            try:
                db.at[st.session_state.user_index, 'chat_history'] = st.session_state.messages
                save_db(db, CHAT_DB_PATH)
                
            except Exception as e:
                logger.error(f"Error in updating chat history, Error: {e}")

            st.rerun(scope="fragment")
            
    with col2:
        if st.button(':small[Clear History]', type="tertiary", use_container_width=True):
            try:
                db.at[st.session_state.user_index, 'chat_history'] = []
                save_db(db, CHAT_DB_PATH)
                
            except Exception as e:
                logger.error(f"Error in clearing chat history, Error: {e}")
            st.rerun(scope="fragment")
            

@st.dialog("Chat with LLM", width= "large")
def chat_ui(db, track):
    st.session_state.user_index = db.index[(db['track_id'] == st.session_state.selected_card) & (db['username'] == st.session_state.user) ][0]
    st.write(f"Selected Track: :green[{track.get('Track Name', '')}]")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        creativity_level = st.selectbox("Select Creativity level:", ['Low', 'Medium', 'High'])
        
    with col2:
        show_name = st.text_input("Enter Show Name:")
        
    with col3:
        show_desc = st.text_input("Enter Basic Show Description:")
    
    display_chat(db, creativity_level, show_name, show_desc, track)