import time 
import streamlit as st
from modules.data_utils import save_db, load_interactions_db
from modules.llm_utils import LLM_response_stream
from constants import CHAT_DB_PATH, DB_PATH
from datetime import datetime, timedelta
from logger import get_logger

logger = get_logger(__file__)

@st.fragment
def display_comments(idx, USERS, df, current_user):
    db = load_interactions_db(DB_PATH, USERS, df)
    all_comments = []
    comments_for_track = db[db['track_id'] == idx]
    col1, col2 = st.columns([6, 0.75])
    with col1:
        st.markdown("### 💬 Comments")
    with col2:
        if st.button(':small[Refresh Comments 🔁]', use_container_width=True):
            st.rerun(scope='fragment')
        
    for _, comment_row in comments_for_track.iterrows():
        comment_user = comment_row['username']
        user_comments = comment_row['comments']
        
        for comment_index, comment_data in enumerate(user_comments):
            comment_text = comment_data[0]
            timestamp = comment_data[1]
            
            all_comments.append({
                'user': comment_user,
                'text': comment_text,
                'timestamp': timestamp,
                'user_comment_index': comment_index,
                'is_current_user': comment_user == current_user
            })
    
    all_comments.sort(key=lambda x: x['timestamp'])
    
    for comment in all_comments:
        col1, col2 = st.columns([6, 0.1])
        with col1:
            dt_object = datetime.fromtimestamp(comment['timestamp'])
            # ist_offset = timedelta(hours=5, minutes=30)
            # dt_ist = dt_object + ist_offset
            formatted_time_ist = dt_object.strftime('%H:%M, %d/%m')
            
            st.markdown(f"- ({formatted_time_ist}) **{comment['user']}**: {comment['text']}")
            
        with col2:
            if comment['is_current_user']:
                delete_key = f"delete_{idx}_{comment['user']}_{comment['user_comment_index']}"
                if st.button("╳", key=delete_key, help="Delete this comment", type="tertiary"):
                    try:
                        row_index = db.index[(db['track_id'] == idx) & (db['username'] == current_user)][0]
                        updated_comments = db.loc[row_index, 'comments'].copy()
                        if comment['user_comment_index'] < len(updated_comments):
                            updated_comments.pop(comment['user_comment_index'])
                            db.at[row_index, 'comments'] = updated_comments
                            save_db(db, DB_PATH)
                            st.session_state.db_df = db.copy()
                            st.rerun()
                            
                    except Exception as e:
                        logger.error(f"Error in deleting comment, Error: {e}")
                        
    
    if comment_input := st.chat_input("Add your comment:"):
            try:
                row_index = db.index[(db['track_id'] == idx) & (db['username'] == current_user)][0]
                db.loc[row_index, 'comments'].append([comment_input.strip(), time.time()])
                save_db(db, DB_PATH)
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error in Adding comment, Error: {e}")                

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


# def stream_message(message):
#     for line in message.splitlines():
#         for word in line:
#             yield word 
#             time.sleep(0.009)
#         yield "\n"
        
# @st.fragment
# def display_chat(db, creativity_level, show_name, show_desc, track):
#     st.session_state.messages = db.loc[st.session_state.user_index, 'chat_history']    
    
#     if "prev_stream" not in st.session_state:
#         st.session_state.prev_stream = len(st.session_state.messages)-1 if st.session_state.messages else 0
        
#     for idx,  msg in enumerate(st.session_state.messages):
#         if idx == len(st.session_state.messages)-1 and idx != st.session_state.prev_stream:
#             st.chat_message(msg["role"]).write_stream(stream_message(msg["content"]))
#             st.session_state.prev_stream = idx 
#         else:
#             st.chat_message(msg["role"]).write(msg["content"])
    
#     col1, col2 = st.columns([3, 0.4])
#     with col1:
#         if prompt := st.chat_input("Deconstruct the past track, or construct the future..."):
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.spinner("Thinking..."): 
#                 response = LLM_response(creativity_level, show_name, show_desc, track)
#             logger.info("reply received")
#             st.session_state.messages.append({"role": "assistant", "content": response})

#             try:
#                 db.at[st.session_state.user_index, 'chat_history'] = st.session_state.messages
#                 save_db(db, CHAT_DB_PATH)
                
#             except Exception as e:
#                 logger.error(f"Error in updating chat history, Error: {e}")

#             st.rerun(scope="fragment")
            
#     with col2:
#         if st.button(':small[Clear History]', type="tertiary", use_container_width=True):
#             try:
#                 db.at[st.session_state.user_index, 'chat_history'] = []
#                 save_db(db, CHAT_DB_PATH)
                
#             except Exception as e:
#                 logger.error(f"Error in clearing chat history, Error: {e}")
#             st.rerun(scope="fragment")

# def display_chat(db, creativity_level, show_name, show_desc, track):
#     """
#     Display the chat interface, handling real-time streaming for the latest response.
#     """
#     # Load and display the entire chat history on each run
#     st.session_state.messages = db.loc[st.session_state.user_index, 'chat_history']
#     for msg in st.session_state.messages:
#         st.chat_message(msg["role"]).write(msg["content"])

#     col1, col2 = st.columns([3, 0.4])

#     with col1:
#         if prompt := st.chat_input("Deconstruct the past track, or construct the future..."):
#             # 1. Append and display the user's new prompt
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             st.chat_message("user").write(prompt)

#             # 2. Stream the assistant's response in real-time
#             with st.chat_message("assistant"):
#                 # st.write_stream displays the content as it arrives and returns the full response
#                 full_response = st.write_stream(LLM_response_stream(creativity_level, show_name, show_desc, track))

#             # 3. Append the complete assistant response to the session state and save it
#             st.session_state.messages.append({"role": "assistant", "content": full_response})
#             logger.info("Stream finished, reply received.")

#             try:
#                 db.at[st.session_state.user_index, 'chat_history'] = st.session_state.messages
#                 save_db(db, CHAT_DB_PATH)
#             except Exception as e:
#                 logger.error(f"Error in updating chat history: {e}")

#     with col2:
#         if st.button(':small[Clear History]', type="tertiary", use_container_width=True):
#             try:
#                 db.at[st.session_state.user_index, 'chat_history'] = []
#                 save_db(db, CHAT_DB_PATH)
#                 st.rerun() # Rerun the app to clear the displayed chat
#             except Exception as e:
#                 logger.error(f"Error in clearing chat history: {e}")

@st.fragment
def display_chat(db, creativity_level, show_name, show_desc, track):
    """
    Displays the chat interface with a scrollable message area and a
    fixed input widget at the bottom.
    """
    message_container = st.container(height=700)

    st.session_state.messages = db.loc[st.session_state.user_index, 'chat_history']
    for msg in st.session_state.messages:
        message_container.chat_message(msg["role"]).write(msg["content"])

    col1, col2 = st.columns([3, 0.4])

    with col1:
        if prompt := st.chat_input("Deconstruct the past track, or construct the future..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            message_container.chat_message("user").write(prompt)

            with message_container.chat_message("assistant"):
                full_response = st.write_stream(LLM_response_stream(creativity_level, show_name, show_desc, track))
                
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            try:
                db.at[st.session_state.user_index, 'chat_history'] = st.session_state.messages
                save_db(db, CHAT_DB_PATH)
                
            except Exception as e:
                logger.error(f"Error in updating chat history, Error: {e}")
            
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