from pandasai import clear_cache
import streamlit as st

def clear_chat_history():
    st.session_state.messages = []
    clear_cache()
