import os
import pandas as pd
import streamlit as st
from pandasai import Agent
from pandasai.llm import OpenAI
from pandasai.responses.streamlit_response import StreamlitResponse

# Sample data with a text column
data = {
    "ID": [1, 2, 3, 4, 5],
    "Text": ["The quick brown fox jumps over the lazy dog.",
             "A fast brown fox leaps over a lazy dog.",
             "Bright stars shine in the night sky.",
             "The night sky is filled with bright stars.",
             "The lazy dog is sleeping peacefully."]
}
df = pd.DataFrame(data)

# Function to create the LLM
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

# Function to create the PandasAI agent
def get_agent(data, llm, agent_context):
    extras = "Modify the generated code to be compatible with Streamlit. Specifically, replace fig.show() with fig.write_json('temp_plot.json') and use the library import plotly.express as px."
    agent = Agent(data, description=agent_context + extras,
                  config={"llm": llm, "verbose": True, "open_charts": False,
                          "response_parser": StreamlitResponse,  
                          "custom_whitelisted_dependencies": ["seaborn", "openai", "streamlit_ydata_profiling", "plotly", "wordcloud", "string"]})
    return agent

# Function to transform the user prompt
def transform_prompt(user_prompt):
    if "semantic classification" in user_prompt.lower():
        return f"""
        Classify the following sentences into groups based on their semantic similarity. 
        For each group, provide a keyword representing the group, the group name, and the number of sentences in that group.
        Format the response as a list of dictionaries with keys 'keyword', 'group_name', and 'count'.
        Sentences:
        {df['Text'].to_list()}
        """
    return user_prompt

# Main function for Streamlit
def main():
    st.title("Semantic Text Classification with PandasAI")

    user_api_key = st.text_input("Enter your OpenAI API key:", type="password")
    llm_type = st.selectbox("Choose the OpenAI model:", ["gpt-4o"])
    
    llm = get_LLM(llm_type, user_api_key)
    
    if llm:
        agent = get_agent([df], llm, "Perform data analysis")
        
        user_prompt = st.text_input("Enter your query:")
        
        if st.button("Run Query"):
            transformed_prompt = transform_prompt(user_prompt)
            response = agent.chat(transformed_prompt)
            st.write(response)

if __name__ == "__main__":
    main()
