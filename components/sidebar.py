import streamlit as st

def setup_sidebar():
    with st.sidebar:
        st.logo("logo.png")

        st.title("Configuration ⚙️")
        st.subheader("Agent Setup:")

        if 'agent_context' not in st.session_state:
            st.session_state['agent_context'] = "You are a data analysis agent. Your main goal is to help non-technical users to analyze data."

        def update_agent_context():
            st.session_state.agent_context = st.session_state.input_text

        st.text_area(
            label="Add here how your agent should act.", 
            value=st.session_state.agent_context, 
            key='input_text',
            on_change=update_agent_context
        )

        st.subheader("Data Setup:")
        data_option = st.radio("Choose data source:", ('Loaded Data', 'Upload'))
        file_upload = None
        if data_option == 'Upload':
            file_upload = st.file_uploader("Upload your Data", accept_multiple_files=True, type=['csv', 'xls', 'xlsx', '.parquet'])

        st.subheader("Model Setup:")
        llm_type = st.selectbox("Please select LLM", [
            "gpt-4o-mini-2024-07-18",
            "gpt-4o",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0613",
            "gpt-4-turbo-preview",        
            "gpt-4o-2024-05-13"
        ], index=0)

        user_api_key = st.text_input('Please add your API key', placeholder='Paste your API key here', type='password')
        st.markdown("[Get Your OpenAI API key here](https://platform.openai.com/api-keys)")

    return st.session_state.agent_context, file_upload, llm_type, user_api_key, data_option
