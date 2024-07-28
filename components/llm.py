import streamlit as st
from pandasai.llm import OpenAI

def get_LLM(llm_type, user_api_key):
    try:
        if not user_api_key:
            st.error("No API key provided! Please provide your OpenAI API key.")
            return None

        llm = OpenAI(api_token=user_api_key, model=llm_type, temperature=0, seed=26)
        return llm
    except Exception as e:
        st.error(f"Error in LLM creation: {e}")
        return None
