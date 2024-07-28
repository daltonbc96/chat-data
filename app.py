import streamlit as st
from components.sidebar import setup_sidebar
from components.chat_window import chat_window
from components.agent import get_agent
from components.data import extract_dataframes, load_data_from_folder
from components.llm import get_LLM


data = {}

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
    with st.container(border=False, height=800):
        col1, col2 = st.columns([1, 2])

        # Primeiro container à esquerda
        with col1:
            st.title("Chat with Your Data")

            # Set up the sidebar
            agent_context, file_upload, llm_type, user_api_key, data_option = setup_sidebar()

            if data_option == 'Upload':
                if file_upload:
                    data = extract_dataframes(file_upload)
                    selected_file = st.selectbox("Select a file:", list(data.keys()))

                    file_extension = selected_file.split('.')[-1].lower()
                    if file_extension in ['xls', 'xlsx']:
                        selected_df = st.selectbox("Select a sheet:", list(data[selected_file].keys()))
                    else:
                        selected_df = 'Sheet1'

                    with st.expander("See the data"):
                        st.dataframe(data[selected_file][selected_df])

                    llm = get_LLM(llm_type, user_api_key)

                    if llm:
                        analyst = get_agent(data[selected_file][selected_df], llm, agent_context)

                        # Containers na coluna da direita
                        with col2:
                            chat_window(analyst)
                else:
                    st.warning("Please upload your data first! You can upload CSV or Excel files.")
            elif data_option == 'Local Folder':
                data = load_data_from_folder("data")
                if data:
                    selected_file = st.selectbox("Select a file:", list(data.keys()))

                    file_extension = selected_file.split('.')[-1].lower()
                    if file_extension in ['xls', 'xlsx']:
                        selected_df = st.selectbox("Select a sheet:", list(data[selected_file].keys()))
                    else:
                        selected_df = 'Sheet1'

                    with st.expander("See the data"):
                        st.dataframe(data[selected_file][selected_df])

                    llm = get_LLM(llm_type, user_api_key)

                    if llm:
                        analyst = get_agent(data[selected_file][selected_df], llm, agent_context)

                        # Containers na coluna da direita
                        with col2:
                            chat_window(analyst)
                else:
                    st.warning("No data found in the local folder.")

if __name__ == "__main__":
    main()