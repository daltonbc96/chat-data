import streamlit as st
from components.sidebar import setup_sidebar
from components.chat_window import chat_window
from components.agent import get_agent
from components.data import extract_dataframes, load_data_from_folder
from components.llm import get_LLM

# Ensure data is stored in session state
if 'data' not in st.session_state:
    st.session_state['data'] = {}

if 'llm' not in st.session_state:
    st.session_state['llm'] = {}

def main():
    st.set_page_config(page_title="Chat with Your Data", page_icon="🤖", layout="wide")

    margins_css = """
    <style>
        .main > div {
            padding-left: 3%;
            padding-right: 3%;
            padding-top: 4%;
            padding-bottom: 3%;
        }

        [alt=Logo] { height: 4rem; }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)

    # Container principal
    with st.container():
        col1, col2 = st.columns([1, 2])

        # Primeiro container à esquerda
        with col1:
            st.title("Chat with Your Data")

            # Set up the sidebar
            agent_context, file_upload, llm_type, user_api_key, data_option = setup_sidebar()

            if data_option == 'Upload':
                if file_upload:
                    st.session_state['data'] = extract_dataframes(file_upload)
                    selected_file = st.selectbox("Select a file:", list(st.session_state['data'].keys()))

                    file_extension = selected_file.split('.')[-1].lower()
                    if file_extension in ['xls', 'xlsx']:
                        selected_df = st.selectbox("Select a sheet:", list(st.session_state['data'][selected_file].keys()))
                    else:
                        selected_df = 'Sheet1'

                    with st.expander("See the sample data"):
                        st.dataframe(st.session_state['data'][selected_file][selected_df].head())

                    with st.expander("See columns"):
                        column_names = st.session_state['data'][selected_file][selected_df].columns.tolist()
                        markdown_columns = "\n".join(f"- {col}" for col in column_names)
                        st.markdown(markdown_columns)

                    st.session_state['llm'] = get_LLM(llm_type, user_api_key)

                    if st.session_state['llm']:
                        analyst = get_agent(st.session_state['data'][selected_file][selected_df], st.session_state['llm'], agent_context)

                        # Containers na coluna da direita
                        with col2:
                            chat_window(analyst, variables_list=column_names)
                else:
                    st.warning("Please upload your data first! You can upload CSV or Excel files.")
            elif data_option == 'Local Folder':
                st.session_state['data'] = load_data_from_folder("data")
                if st.session_state['data']:
                    selected_file = st.selectbox("Select a file:", list(st.session_state['data'].keys()))

                    file_extension = selected_file.split('.')[-1].lower()
                    if file_extension in ['xls', 'xlsx']:
                        selected_df = st.selectbox("Select a sheet:", list(st.session_state['data'][selected_file].keys()))
                    else:
                        selected_df = 'Sheet1'

                    with st.expander("See the sample data"):
                        st.dataframe(st.session_state['data'][selected_file][selected_df].head())

                    with st.expander("See columns"):
                        column_names = st.session_state['data'][selected_file][selected_df].columns.tolist()
                        markdown_columns = "\n".join(f"- {col}" for col in column_names)
                        st.markdown(markdown_columns)

                    st.session_state['llm'] = get_LLM(llm_type, user_api_key)

                    if st.session_state['llm']:
                        analyst = get_agent(st.session_state['data'][selected_file][selected_df], st.session_state['llm'], agent_context)

                        # Containers na coluna da direita
                        with col2:
                            chat_window(analyst, variables_list=column_names)
                else:
                    st.warning("No data found in the local folder.")

if __name__ == "__main__":
    main()
