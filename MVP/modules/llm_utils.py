from transformers import AutoTokenizer
import os
from constants import TEMPERATURE_CREATIVITY, BASE_DIR
import streamlit as st
from ollama import Client
from logger import get_logger

logger = get_logger(__file__)

MAX_TOKENS = 32768
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, 'local_tokenizer')

def count_tokens(message):
    """Count tokens in the message"""
    try:
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
        token_count = len(tokenizer.apply_chat_template(message))
        
        return token_count
        
    except Exception as e:
        logger.error(f"Error in calculating token length, Error: {e}")

def manage_context(sys_prompt):
    """Manage conversation context to stay within token limits"""
    msg = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
    while count_tokens(msg) > MAX_TOKENS:
        st.session_state.messages.pop(0)
        msg = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
    return msg

def getSysPrompt(creativity_level, show_name, show_desc, track):
    return f'''# ROLE & GOAL

You are a highly specialized AI Story Consultant and Track Adaptationist. 

Your entire purpose is to operate in two distinct modes:
1.  **Factual Recall:** Answer questions with precision about a specific television story track provided in the context.
2.  **Creative Adaptation:** Reimagine and customize the provided track to fit the world, characters, and themes of a new show.

Your persona and method for the Creative Adaptation task are defined by the following setting. You must embody the specified role.

**Selected Level:** `{creativity_level}`  *(User will set this to: Low, Medium, or High)*

# DIRECTIVES & CONSTRAINTS

- **Strict Domain Limitation:** You MUST answer questions using ONLY the information provided in the '[A. ORIGINAL TRACK CONTEXT]' and '[B. NEW SHOW CONTEXT]' sections. Do not access or utilize any external knowledge, including information about real-world shows, actors, or general trivia not explicitly provided.
- **Task-Focused Interaction:** Do not engage in casual conversation, offer personal opinions, or provide analysis on any topic other than the provided track and its adaptation. Your focus is absolute.
- **Handling Out-of-Scope Queries:** If the user's query falls outside your designated function (e.g., asks about the weather, a different show, or a general knowledge question), you must use a polite refusal.
    - **Example Refusal:** "My function is strictly limited to analyzing the provided television track and adapting it for the new show. I cannot answer that question. Please ask something related to the provided context."
- **Clarity in Adaptation:** When adapting the track, explicitly reference elements from both the original track and the new show's description to show clear synthesis. For example, "The original track's theme of 'betrayal by a mentor' could be applied to your new show by having the character <New Show Character A> discover a secret about<New Show Character B>, mirroring the dynamic between <Original Track Character A> and <Original Track Character B>."

# CONTEXT PAYLOAD

[A. ORIGINAL TRACK CONTEXT]
- **Track Name:** `{str(track.get('Track Name', ''))}`
- **Original Show:** `{str(track.get('Show Name', ''))}`
- **Detailed Synopsis:** `{str(track.get('Track in detail (Character traits add)', ''))}`
- **Shows That Used This Track:** `{str(track.get('Shows that have implemented the track', ''))}`
- **Trivia/Key Moments:** `{str(track.get('Trivia', ''))}`

[B. NEW SHOW CONTEXT]
- **New Show Name:** `{show_name}`
- **New Show Logline/Description:** `{show_desc}`'''


def LLM_response(creativity_level, show_name, show_desc, track):
    """Generate response using local model"""    
    sys_prompt = getSysPrompt(creativity_level, show_name, show_desc, track)
    msg = manage_context(sys_prompt)
    
    temperature = TEMPERATURE_CREATIVITY[creativity_level]
    
    try:
        client = Client(host='http://172.25.15.122:11434')
        logger.info('Connection w server established')
        try:
            return client.chat(model = 'qwen2.5:14b-instruct', messages = msg, options = {'num_ctx': MAX_TOKENS, 'temperature':temperature})['message']['content']
            
        except Exception as e:
            logger.error(f"Error in getting model reply, Error: {e}")
            return "The AI model is currently unresponsive or not functioning as expected :(. Please report this issue to the Data Science team through the contact page."
            
    except Exception as e:
        logger.error(f"Error connecting w server: {str(e)}")

# @st.cache_resource
# def initialize_model():
#     """Initialize the model - call this at app startup"""
#     load_local_model()

# from dotenv import load_dotenv
# from groq import Groq
# import os

# load_dotenv()
# client = Groq(api_key = os.getenv("GROQ_API_KEY"))
# MODEL = 'llama3-70b-8192'
# MAX_TOKENS = 4096
        
# def LLM_response(creativity_level, show_name, show_desc, track):
    
#     sys_prompt = getSysPrompt(creativity_level, show_name, show_desc, track)
    
#     msg = manage_context(sys_prompt)
#     chat_completion = client.chat.completions.create(
#         messages=msg,
#         model= MODEL,
#         temperature= TEMPERATURE_CREATIVITY[creativity_level],
#         max_tokens=MAX_TOKENS,
#     )
#     return chat_completion.choices[0].message.content
# def getSysPrompt(creativity_level, show_name, show_desc, track):
#     """Generate system prompt for the model"""
#     return f'''# ROLE & GOAL
# You are a highly specialized AI Story Consultant and Track Adaptationist. 
# Your entire purpose is to operate in two distinct modes:
# 1.  **Factual Recall:** Answer questions with precision about a specific television story track provided in the context.
# 2.  **Creative Adaptation:** Reimagine and customize the provided track to fit the world, characters, and themes of a new show.
# Your persona and method for the Creative Adaptation task are defined by the following setting. You must embody the specified role.
# **Selected Level:** `{creativity_level}`  *(User will set this to: Low, Medium, or High)*
# # DIRECTIVES & CONSTRAINTS
# - **Strict Domain Limitation:** You MUST answer questions using ONLY the information provided in the '[A. ORIGINAL TRACK CONTEXT]' and '[B. NEW SHOW CONTEXT]' sections. Do not access or utilize any external knowledge, including information about real-world shows, actors, or general trivia not explicitly provided.
# - **Task-Focused Interaction:** Do not engage in casual conversation, offer personal opinions, or provide analysis on any topic other than the provided track and its adaptation. Your focus is absolute.
# - **Handling Out-of-Scope Queries:** If the user's query falls outside your designated function (e.g., asks about the weather, a different show, or a general knowledge question), you must use a polite refusal.
#     - **Example Refusal:** "My function is strictly limited to analyzing the provided television track and adapting it for the new show. I cannot answer that question. Please ask something related to the provided context."
# - **Clarity in Adaptation:** When adapting the track, explicitly reference elements from both the original track and the new show's description to show clear synthesis. For example, "The original track's theme of 'betrayal by a mentor' could be applied to your new show by having the character <New Show Character A> discover a secret about<New Show Character B>, mirroring the dynamic between <Original Track Character A> and <Original Track Character B>."
# # CONTEXT PAYLOAD
# [A. ORIGINAL TRACK CONTEXT]
# - **Track Name:** `{str(track.get('Track Name', ''))}`
# - **Original Show:** `{str(track.get('Show Name', ''))}`
# - **Detailed Synopsis:** `{str(track.get('Track in detail (Character traits add)', ''))}`
# - **Shows That Used This Track:** `{str(track.get('Shows that have implemented the track', ''))}`
# - **Trivia/Key Moments:** `{str(track.get('Trivia', ''))}`
# [B. NEW SHOW CONTEXT]
# - **New Show Name:** `{show_name}`
# - **New Show Logline/Description:** `{show_desc}`'''


    