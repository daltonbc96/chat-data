import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from pandasai import clear_cache
from utils.sanitizer import sanitize_query
from streamlit_pills import pills
from typing import Iterable, Union, Callable


def display_message(message):
    with st.chat_message(message["role"]):
        if 'question' in message:
            st.markdown(message["question"], unsafe_allow_html=True)
        elif 'response' in message:
            display_response(message['response'])
        elif 'error' in message:
            st.text(message['error'])

def display_response(response):
    if isinstance(response, str) and response.endswith('.png'):
        st.image(response)
    elif isinstance(response, str) and response.endswith('.json'):
        fig = pio.read_json(response)
        st.plotly_chart(fig)
    elif isinstance(response, pd.DataFrame):
        st.dataframe(response)
    elif isinstance(response, np.ndarray):
        st.markdown(response, unsafe_allow_html=True)
    elif isinstance(response, plt.Figure):
        st.pyplot(response)
    elif isinstance(response, Image.Image):
        st.image(response, caption='Custom Image')
    elif isinstance(response, go.Figure):
        st.plotly_chart(response)
    elif isinstance(response, int) or isinstance(response, float):
        st.markdown(response, unsafe_allow_html=True)
    else:
        st.markdown(response, unsafe_allow_html=True)

def clear_chat_history():
    st.session_state.messages = []
    clear_cache()

def custom_pills(label: str, options: Iterable[str], icons: Iterable[str] = None, index: Union[int, None] = 0,
                 format_func: Callable = None, label_visibility: str = "visible", clearable: bool = None,
                 key: str = None, reset_key: str = None):
    """
    Mostra pills clicáveis com a opção de resetar a seleção.

    Args:
        label (str): O rótulo mostrado acima das pills.
        options (iterable of str): Os textos mostrados dentro das pills.
        icons (iterable of str, optional): Os ícones de emoji mostrados no lado esquerdo das pills. Cada item deve ser um único emoji. Padrão None.
        index (int or None, optional): O índice da pill que é selecionada por padrão. Se None, nenhuma pill é selecionada. Padrão 0.
        format_func (callable, optional): Uma função que é aplicada ao texto da pill antes da renderização. Padrão None.
        label_visibility ("visible" or "hidden" or "collapsed", optional): A visibilidade do rótulo. Use isso em vez de `label=""` para acessibilidade. Padrão "visible".
        clearable (bool, optional): Se o usuário pode desmarcar a pill selecionada clicando nela. Padrão None.
        key (str, optional): A chave do componente. Padrão None.
        reset_key (str, optional): A chave utilizada para resetar a seleção. Padrão None.

    Returns:
        (any): O texto da pill selecionada pelo usuário (mesmo valor em `options`).
    """
    
    # Crie uma chave única para o componente para forçar a atualização quando necessário
    unique_key = f"{key}-{reset_key}" if key and reset_key else key
    
    # Passar os argumentos para a função pills
    selected = pills(label=label, options=options, icons=icons, index=index, format_func=format_func,
                     label_visibility=label_visibility, clearable=clearable, key=unique_key)
    
    return selected


def chat_window(analyst):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_prompt" not in st.session_state:
        st.session_state.selected_prompt = ""

    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0

    if "input_value" not in st.session_state:
        st.session_state.input_value = ""

    def reset_selection():
        st.session_state.selected_prompt = ""
        st.session_state.input_value = ""
        st.session_state.reset_key += 1

    def update_input_value(value):
        st.session_state.input_value = value

    # Container for chat messages with a limited height
    chat_container = st.container(border=True, height=500)

    with chat_container:

        st.text("What do you want to know about your data? Type it below!")

        # Display existing chat messages
        for message in st.session_state.messages:
            display_message(message)

    # Container for user input
    user_input_container = st.container(border=True)

    with user_input_container:
        user_question = st.chat_input("What are you curious about? Type it here ...", key="chat_input")

    # Container for prompt suggestions (pills)
    pills_container = st.container(border=True, height=150)

    with pills_container:
        general_prompts = [
            "What is the summary of the dataset?",
            "Show me a plot of the data distribution.",
            "What are the key statistics?",
            "How many missing values are there?",
            "Can you identify outliers in the data?"
        ]
        
        selected_pill = custom_pills("Prompt suggestions", general_prompts, index=None, clearable=False, key="pills", reset_key=str(st.session_state.reset_key))
        if selected_pill:
            st.session_state.selected_prompt = selected_pill
            update_input_value(selected_pill)
            js = f"""
                <script>
                    var chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                    nativeInputValueSetter.call(chatInput, "{st.session_state.input_value}");
                    var event = new Event('input', {{ bubbles: true }});
                    chatInput.dispatchEvent(event);
                </script>
            """
            st.components.v1.html(js)
            reset_selection()

    if user_question:
        sanitized_question = sanitize_query(user_question)

        with chat_container:
            with st.chat_message("user"):
                st.markdown(sanitized_question)
            st.session_state.messages.append({"role": "user", "question": sanitized_question})

        try:
            with chat_container:
                with st.spinner("Analyzing..."):
                    response = analyst.chat(sanitized_question)
                    st.session_state.messages.append({"role": "assistant", "response": response})
                    display_response(response)
        except Exception as e:
            with chat_container:
                st.error(f"⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question! Error: {e}")

        st.rerun()

    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️", on_click=clear_chat_history)


