import streamlit as st
import pandas as pd
import os
import ast
from logger import get_logger

logger = get_logger(__file__)

@st.cache_data
def load_data(file_path):
    """Loads the main track data from an Excel file."""
    return pd.read_excel(file_path)

@st.cache_data
def load_users(file_path, user):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=['username']).to_csv(file_path, index=False)
    db_df = pd.read_csv(file_path)
    needs_update = True if user not in db_df['username'].values else False

    if needs_update:
        new_rows_df = pd.DataFrame({'username': [user]})
        db_df = pd.concat([db_df, new_rows_df], ignore_index=True)
        db_df.to_csv(file_path, index=False)
        logger.info(f"Added new user: {user}")
        
    return db_df['username'].values


def load_interactions_db(file_path, users, tracks_df):
    """Loads the user interaction database, creating or updating it if necessary."""
    
    if not os.path.exists(file_path):
        pd.DataFrame(columns=['username', 'track_id', 'liked', 'views', 'comments']).to_csv(file_path, index=False)
    db_df = pd.read_csv(file_path)
    
    if 'comments' in db_df.columns:
        db_df['comments'] = db_df['comments'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
    needs_update = False
    all_rows = []
    for user in users:
        for track_id in tracks_df.index:
            if db_df[(db_df['username'] == user) & (db_df['track_id'] == track_id)].empty:
                needs_update = True
                new_row = {'username': user, 'track_id': track_id, 'liked': 0, 'views': 0, 'comments': []}
                all_rows.append(new_row)
    if needs_update:
        new_rows_df = pd.DataFrame(all_rows)
        db_df = pd.concat([db_df, new_rows_df], ignore_index=True)
        db_df.to_csv(file_path, index=False)
    return db_df

def load_context_db(file_path, users, tracks_df):
    """Loads the user interaction database, creating or updating it if necessary."""
    if not os.path.exists(file_path):
        pd.DataFrame(columns=['username', 'track_id', 'chat_history']).to_csv(file_path, index=False)
        
    db_df = pd.read_csv(file_path)
    if 'chat_history' in db_df.columns:
        db_df['chat_history'] = db_df['chat_history'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
    needs_update = False
    
    all_rows = []
    for user in users:
        for track_id in tracks_df.index:
            if db_df[(db_df['username'] == user) & (db_df['track_id'] == track_id)].empty:
                needs_update = True
                new_row = {'username': user, 'track_id': track_id, 'chat_history': []}
                all_rows.append(new_row)
            
    if needs_update:
        new_rows_df = pd.DataFrame(all_rows)
        db_df = pd.concat([db_df, new_rows_df], ignore_index=True)
        db_df.to_csv(file_path, index=False)
        
    return db_df

def save_db(df, path):
    """Saves the database DataFrame to the CSV file."""
    try:
        df.to_csv(path, index=False)
    except Exception as e:
         logger.error(f"Error in saving DB{path}, Error: {e}")
