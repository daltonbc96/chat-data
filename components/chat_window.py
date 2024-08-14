import os
import uuid
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

from utils.clear_cache import clear_chat_history
from utils.sanitizer import sanitize_query
from components.pills import custom_pills
from components.search_suggestions import show_chat_input_with_suggestions


# Function to save file with unique name
def save_file_with_unique_name(file_content, extension, directory='saved_files'):
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(directory, unique_filename)
    
    # Save file content to the unique path
    mode = 'wb' if isinstance(file_content, bytes) else 'w'
    with open(file_path, mode) as f:
        f.write(file_content)
    
    return file_path

# Modify display_response function
def display_response(response):
    if isinstance(response, str) and response.endswith('.png'):
        with open(response, 'rb') as file:
            content = file.read()
        file_path = save_file_with_unique_name(content, 'png')
        st.image(file_path)
        return file_path
    elif isinstance(response, str) and response.endswith('.json'):
        with open(response, 'r') as file:
            content = file.read()
        file_path = save_file_with_unique_name(content.encode(), 'json')
        fig = pio.read_json(file_path)
        st.plotly_chart(fig)
        return file_path
    elif isinstance(response, pd.DataFrame):
        st.dataframe(response)
        return None
    elif isinstance(response, np.ndarray):
        st.markdown(response, unsafe_allow_html=True)
        return None
    elif isinstance(response, plt.Figure):
        st.pyplot(response)
        return None
    elif isinstance(response, Image.Image):
        st.image(response, caption='Custom Image')
        return None
    elif isinstance(response, go.Figure):
        st.plotly_chart(response)
        return None
    elif isinstance(response, int) or isinstance(response, float):
        st.markdown(response, unsafe_allow_html=True)
        return None
    else:
        st.markdown(response, unsafe_allow_html=True)
        return None

def display_message(message):
    with st.chat_message(message["role"]):
        if 'question' in message:
            st.markdown(message["question"], unsafe_allow_html=True)
        elif 'response' in message:
            file_path = display_response(message['response'])
            if file_path:
                message['response'] = file_path  # Update message with file path

            if 'code_executed' in message:
                with st.expander("See code generated"):
                    st.markdown("**Generated Code:**")
                    st.code(message['code_executed'], language='python')

        elif 'error' in message:
            st.text(message['error'])

def chat_window(analyst, variables_list):
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

        with st.chat_message("assistant"):
            st.text("What do you want to know about your data? Type it below!")

        # Display existing chat messages
        for message in st.session_state.messages:
            display_message(message)

    # Container for user input
    user_input_container = st.container(border=False)

    with user_input_container:
        user_question = st.chat_input("What are you curious about? Type it here ...", key="chat_input")

        # Chama a função para mostrar as sugestões
        show_chat_input_with_suggestions(variables_list)

    # Container for prompt suggestions (pills)
    pills_container = st.container(border=True, height=150)

    prompts = {
        "Group by Similarity": "Please perform a semantic grouping of the cases in the variable *Text*. Provide a brief description of each group and the count of cases in each group.",
        "Summary": "Please provide a detailed summary of the dataset including key statistics for the variable *Text*.",
        "Outliers": "Identify and describe any outliers in the variable *Text*."
    }

    with pills_container:
        selected_prompt = custom_pills("Prompt suggestions", prompts, index=None, clearable=False, key="pills", reset_key=str(st.session_state.reset_key))
        if selected_prompt:
            # Update input value directly with the elaborated prompt
            st.session_state.input_value = selected_prompt
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
                    code_executed = analyst.last_code_generated  # Captura o código gerado pelo pandasai
                    message = {"role": "assistant", "response": response, "code_executed": code_executed}
                    st.session_state.messages.append(message)
                    
                    file_path = display_response(response)
                    if file_path:
                        message['response'] = file_path  # Update message with file path
        except Exception as e:
            with chat_container:
                st.error(f"⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question! Error: {e}")
        st.rerun()



    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️", on_click=clear_chat_history)






