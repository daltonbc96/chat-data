import streamlit as st
import pandas as pd
from pandasai.llm import OpenAI
from pandasai import Agent
from pandasai import clear_cache
from pandasai.responses.streamlit_response import StreamlitResponse
from pandasai.skills import skill


from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report
import os

#from personal_skills import generate_insights
# Load environment variables


# Dictionary to store the extracted dataframes
data = {}



def main():
    st.set_page_config(page_title="Chat with Your Data", page_icon="🤖")



    st.html("""
    <style>
        [alt=Logo] {
        height: 5rem;
        }
    </style>
    """)

    st.title("Chat with Your Data")
    
    # Side Menu Bar
    with st.sidebar:
        st.logo(image="logo.png", link="https://www.paho.org/en")
        st.title("Configuration:⚙️")
        st.subheader("Agent Setup:")

        if 'agent_context' not in st.session_state:
            st.session_state['agent_context'] = "You are a data analysis agent. Your main goal is to help non-technical users to analyze data"
        def update_agent_context():
            st.session_state.agent_context = st.session_state.input_text

        st.text_area(
            label="Add here how your agent should act. [See documentation](https://docs.pandas-ai.com/examples#description-for-an-agent)", 
            value=st.session_state.agent_context, 
            key='input_text',
            on_change=update_agent_context
        )



        # Activating Demo Data
        st.subheader("Data Setup:")
        file_upload = st.file_uploader("Upload your Data", accept_multiple_files=True, type=['csv', 'xls', 'xlsx'])
        #st.markdown(":blue[*Please ensure the first row has the column names.*]")
        
        st.subheader("Model Setup:")

        # Selecting LLM to use
        llm_type = st.selectbox("Please select LLM", [
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
        
        # Adding user's API Key
        user_api_key = st.text_input('Please add your API key', placeholder='Paste your API key here', type='password')
        
        # Get PandasAI API key here
        st.markdown("[Get Your OpenAI API key here](https://platform.openai.com/api-keys)")


      

    if file_upload:
        data = extract_dataframes(file_upload)
        selected_file = st.selectbox("Select a file:", list(data.keys()))

        # Verifica se o arquivo é do tipo xls ou xlsx antes de exibir o selectbox para selecionar planilhas
        file_extension = selected_file.split('.')[-1].lower()
        if file_extension in ['xls', 'xlsx']:
            selected_df = st.selectbox("Select a sheet:", list(data[selected_file].keys()))
        else:
            selected_df = 'Sheet1'  # Para arquivos CSV, usar 'Sheet1' como padrão

        with st.expander("See the data"):
            st.dataframe(data[selected_file][selected_df])
        
        llm = get_LLM(llm_type, user_api_key)
        
        if llm:
            # Instantiating PandasAI agent
            analyst = get_agent(data[selected_file][selected_df], llm)
            # Starting the chat with the PandasAI agent
            chat_window(analyst)
            
    else:
        st.warning("Please upload your data first! You can upload CSV or Excel files.")

# Function to get LLM
def get_LLM(llm_type, user_api_key):
    """
    Função para criar um objeto LLM baseado no tipo selecionado pelo usuário.
    Args:
        llm_type: Tipo de LLM selecionado pelo usuário.
        user_api_key: Chave da API fornecida pelo usuário.
    Returns:
        llm: Objeto LLM configurado.
    """
    try:
        if not user_api_key:
            st.error("No API key provided! Please provide your OpenAI API key.")
            return None

        llm = OpenAI(api_token=user_api_key, model=llm_type, temperature=0, seed=26)
        return llm
    except Exception as e:
        st.error(f"Error in LLM creation: {e}")
        return None

# Função para janela de chat
def chat_window(analyst):
    with st.chat_message("assistant"):
        st.text("What do you want to know about your data?")

    # Initializing message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Displaying the message history on re-run
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Printing the questions
            if 'question' in message:
                st.markdown(message["question"],  unsafe_allow_html=True)
            # Printing the code generated and the evaluated code
            elif 'response' in message:
                response = message['response']
                if isinstance(response, str) and response.endswith('.png'):
                    st.image(response)
                else:
                    st.markdown(response,  unsafe_allow_html=True)
            # Retrieving error messages
            elif 'error' in message:
                st.text(message['error'])

    # Getting the questions from the users
    user_question = st.chat_input("What are you curious about? ")

    if user_question:
        sanitized_question = sanitize_query(user_question)
       # if user_question != sanitized_question:
        #    st.warning("Your question contained words that are not allowed and were removed for security reasons.")

        # Displaying the user question in the chat message
        with st.chat_message("user"):
            st.markdown(sanitized_question)
        # Adding user question to chat history
        st.session_state.messages.append({"role": "user", "question": sanitized_question})
       
        try:
            with st.spinner("Analyzing..."):
                response = analyst.chat(sanitized_question)
                st.session_state.messages.append({"role": "assistant", "response": response})
                # Check if the response is an image path and display it
                if isinstance(response, str) and response.endswith('.png'):
                    st.image(response)
                else:
                    st.markdown(response,  unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question! Error: {e}")

    # Function to clear history
    def clear_chat_history():
        st.session_state.messages = []
        clear_cache()

    # Button for clearing history
    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️", on_click=clear_chat_history)

def get_agent(data, llm):
    """
    Função para criar um agente nos dataframes extraídos dos arquivos carregados.
    Args:
        data: Um dicionário com os dataframes extraídos dos dados carregados.
        llm: Objeto LLM baseado no tipo selecionado.
    Returns:
        agent: Agente PandasAI configurado.
    """
    #os.environ['PANDASAI_API_KEY'] = "$2a$10$MrC0y4d412.qpJ86/8lQpOSI7RykVPGYBWjICmQhMgVG0mA5/tKXu"
   # df = SmartDataframe(data)

    extras = "Don't return information with text and a graphic or image at the same time. In these cases, return only the text and ask the user if they want you to generate a separate graphic or image. If in doubt, always ask the user before proceeding with the request."
    agent = Agent(data, description= st.session_state.agent_context + extras,
                  config={"llm": llm, "verbose": True, "open_charts": False,
                              "response_parser": StreamlitResponse,  
                              "custom_whitelisted_dependencies": ["seaborn", "ydata_profiling", "streamlit_ydata_profiling", "plotly"]})
    #agent.add_skills(generate_descriptive)
    return agent

def extract_dataframes(files):
    """
    Função para extrair dataframes dos arquivos carregados.
    Args: 
        files: Lista de Upload_File objects
    Processamento: Baseado no tipo de arquivo, ler CSV ou Excel para extrair os dataframes.
    Output: 
        dfs: Um dicionário com os dataframes.
    """
    dfs = {}
    for file in files:
        file_extension = file.name.split('.')[-1].lower()
        if file_extension == 'csv':
            csv_name = file.name.split('.')[0]
            df = pd.read_csv(file)
            dfs[csv_name] = {'Sheet1': df}
        elif file_extension in ['xlsx', 'xls']:
            # Ler o arquivo Excel
            xls = pd.ExcelFile(file)
            # Iterar por cada planilha no arquivo Excel e armazená-las em dataframes
            sheet_dfs = {}
            for sheet_name in xls.sheet_names:
                sheet_dfs[sheet_name] = pd.read_excel(file, sheet_name=sheet_name)
            dfs[file.name] = sheet_dfs
        else:
            st.error(f"Unsupported file type: {file.name}! Please upload a CSV or Excel file.")
    # Retornar os dataframes
    return dfs

def sanitize_query(query):
    dangerous_keywords = [" os", " io", ".os", ".io", "'os'", "'io'", '"os"', '"io"', "chr(", "chr)", "chr ", "(chr", "b64decode"]
    for keyword in dangerous_keywords:
        query = query.replace(keyword, "")
    return query




@skill
def generate_descriptive(df: pd.DataFrame, threshold: float = 0.1):
    """
    Generate a profiling report based on the dataframe content and display it as HTML.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        str: A message indicating the report is ready and the path where it's stored.
    """
    for col in df.select_dtypes(include=['object']).columns:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio < threshold:
            df[col] = df[col].astype('category')

    report = ProfileReport(df, title="Profiling Report", minimal=True, explorative=True)
    
    # Generate the file path based on the root of the project
    report_path = os.path.abspath("report.html")
    report.to_file(report_path)
    
    # Create an HTML hyperlink
    report_link = f'''The report is ready and can be accessed at the following address: {report_path}'''
    return report_link
if __name__ == "__main__":
    main()

