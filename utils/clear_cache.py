from pandasai import clear_cache
import streamlit as st
import shutil
import os

def clear_chat_history():
    st.session_state.messages = []
    clear_cache()


# Função para limpar o diretório saved_files
def clear_saved_files(directory='saved_files'):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        os.makedirs(directory)



# Função para rodar apenas na inicialização da aplicação
def run_once():
    if "initialized" not in st.session_state:
        clear_saved_files()
        st.session_state["initialized"] = True