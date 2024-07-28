from pandasai import Agent
from pandasai.responses.streamlit_response import StreamlitResponse

def get_agent(data, llm, agent_context):
    extras = "Modify the generated code to be compatible with Streamlit. Specifically, replace fig.show() with fig.write_json('temp_plot.json')."
    agent = Agent(data, description=agent_context + extras,
                  config={"llm": llm, "verbose": True, "open_charts": False,
                          "response_parser": StreamlitResponse,  
                          "custom_whitelisted_dependencies": ["seaborn", "ydata_profiling", "streamlit_ydata_profiling", "plotly"]})
    return agent
