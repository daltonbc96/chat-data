import os
import uuid
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

from utils.clear_cache import clear_chat_history, clear_saved_files
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
    pills_container = st.container(border=True, height=300)

    prompts = {
    "Line Chart: Trials by Year and Country": 
        "Create a line chart that shows the Number of Trials by Year and Country for the years 1999 to 2022. Use the **Date_registration3** column to extract the years, and filter the data to include only trials registered between 1999 and 2022. Group the data by **Year** and **country** to calculate the number of trials for each year and each country, ensuring that each country has its own line in the chart. On the **x-axis**, display the years, and on the **y-axis**, show the Number of Trials. Make sure that the **country** column is used as the color parameter so that each country's data is represented by a separate line in the chart with different colors.",
    "Line Chart: Trials by Year and Regions":  
        "Create a line chart titled 'Number of Trials by Year and Region (1999-2022)' that shows the total number of trials registered each year, grouped by **regions**. Use the **Date_registration3** column to extract the years, and filter the data to include only trials registered between 1999 and 2022. Group the data by **Year** and **regions** to calculate the total number of trials for each year and each region. On the x-axis, display the years, and on the y-axis, show the total number of trials. Each line in the chart should represent a different region, with the **regions** names used as labels.",
    "Line Chart: Total Trials Over Time": 
        "Create a line chart titled 'Number of Trials Over Time (1999 to 2022)' that shows the total number of trials registered each year, considering all countries together. Use the **Date_registration3** column to extract the years, and filter the data to include only trials registered between 1999 and 2022. Group the data by **Year** to calculate the total number of trials for each year. On the **x-axis**, display the years, and on the **y-axis**, show the total number of trials for each year.",
   
    "Bar Chart: Trials by Country": 
        "Create a bar chart titled 'Number of Trials by Country or Area' that shows the total number of trials for each country or area using the entire dataframe. Use the **Date_registration3** column to extract the years, and filter the data to include only trials registered between 1999 and 2022. Ensure that all rows in the dataframe are included in the analysis. Group the data by **country** to calculate the total number of trials for each country. On the **y-axis**, display the names of the countries, and on the **x-axis**, show the total number of trials. Each bar should represent a different country, ordered by the number of trials in descending order so that the countries with the most trials are at the top of the chart.",

    "Bar Chart: Trials by Phase of Development": 
      "Create a bar chart titled 'Trials by Phase of Development' that shows the total number of trials for each development phase. Use the **specific_phase** column for the y-axis and the total number of trials for each phase on the x-axis. Ensure each bar is colored differently according to the phase it represents. The phases should be ordered from 'Phase I' at the top, increasing progressively through 'Phase II', 'Phase III', 'Phase IV', and ending with 'Unknown or Not applicable' at the bottom. For phases with combined values like 'Phase I/Phase II' or 'Phase III/Phase IV', place them between the individual phases in the correct order.",


    "Bar Chart: Trials by Life Stage of Participants": "Create a bar chart titled 'Trials by Life Stage of Participants' that shows the total number of trials for each life stage of participants. Use the **Age Classification** column for the y-axis and the total number of trials for each age classification on the x-axis. Ensure each bar is colored differently according to the age classification it represents. The age classifications should be ordered chronologically, with the older stages (e.g., 'Older adults') at the top, progressing downwards to the younger stages (e.g., 'Post neonatal infants'), and ending with 'Unknown or not applicable' at the bottom. For categories with combined values like 'Older children, Young adolescents' or 'Young adults, Older adults', place them in the appropriate order based on the ages they represent.",
    
    "Bar Chart: Trials by Health Sub-Category": "Create a bar chart titled 'Trials by Health Sub-Category' that shows the total number of trials for each health sub-category. Use the **Disease Condition Sub Group** column for the y-axis and the total number of trials for each sub-group on the x-axis. Ensure each bar is colored differently according to the health sub-category it represents. Organize the y-axis by frequency, displaying the sub-groups with the highest number of trials at the top and the lowest at the bottom.",


    "Donut Chart: Trials by Health Category":"Create a donut chart titled 'Trials by Health Category' that shows the absolute number and percentage of trials for each category in the **Disease Condition Main Group** column. Use the entire dataframe to include all trials without any filtering. Each category in the **Disease Condition Main Group** should have a unique color. Display both the absolute number of trials and the percentage for each category on the chart.",

    "Donut Chart: Trials by Sex of Participants": "Create a donut chart titled 'Trials by Sex of Participants' that shows the absolute number and percentage of trials for each category in the **Inclusion_gender** column. Use the entire dataframe to include all trials without any filtering. Each category in the **Inclusion_gender** should have a unique color. Display both the absolute number of trials and the percentage for each category on the chart.",
    
     
    "Stacked Line Chart: Trials by Income Classification": "Create a stacked line chart titled **Trials by Income Classification** that shows the total number of trials for each income classification of countries over time. Use the income_classification column for the y-axis and the total number of trials for each year on the x-axis. Ensure the lines are stacked to show the cumulative number of trials within each income classification over time, with different colors representing each income classification. Ensure the stacked lines do not overlap smaller areas, maintaining the visibility of all income classification.",
    
    "Stacked Line Chart: Trials by Intervention Type Over Time": "Create a stacked line chart titled 'Trials by Intervention Type Over Time' that shows the total number of trials for each type of intervention over the years. Use the intervention_type column to differentiate the areas by color, ensuring each type of intervention is represented by a distinct color. On the x-axis, display the years extracted from the Date_registration3 column, and on the y-axis, show the total number of trials. Ensure the stacked lines do not overlap smaller areas, maintaining the visibility of all intervention types.",
    
    "Stacked Line Chart: Trials Involving Multiple Countries Over Time":  "Create a stacked line chart titled 'Trials Involving Multiple Countries Over Time' that shows the total number of trials over the years, categorized by whether they involve multiple countries or not. Use the multiple_countries column to differentiate between trials that involve multiple countries and those that do not. On the y-axis, display the number of trials, and on the x-axis, show the years extracted from the Date_registration3 column. Ensure the lines are stacked to show the cumulative number of trials over time, with different colors representing trials involving multiple countries ('Yes') or not ('No').",

    "Table: Trials by Conditions": "Create a table that displays the total number of trials for each condition of focus in the investigation. Use the condition_1 column to list the names of the conditions in one column and the corresponding number of trials for each condition in another column. Ensure the table is sorted in descending order based on the number of trials.",
    
    "Table: Trials by Specific Group Countries": "Create a stacked line chart titled 'Trials by Multi-Country Involvement Over Time' that shows the total number of trials each year, categorized by whether they involve multiple countries or not. Use the Date_registration3 column to extract the years, and filter the data to include trials registered over the available years. For the y-axis, use the total number of trials, and for the x-axis, use the years. Use the multiple_countries column, which is a boolean, to differentiate between trials that involve multiple countries and those that do not. Ensure that the chart is a stacked line chart, where the lines are stacked to show the cumulative number of trials over time, with different colors representing trials involving multiple countries ('Yes') or not ('No').",
    "Table: Trials by Sponsor": "Create a table that displays the total number of trials for each primary sponsor. Use the primary_sponsor column to list the names of the sponsors in one column and the corresponding number of trials for each sponsor in another column. Ensure the table is sorted in descending order based on the number of trials."
    }


    with pills_container:
        selected_prompt = custom_pills("Choose one of the suggestions below and see the suggested prompt in the input field", prompts, index=None, clearable=False, key="pills", reset_key=str(st.session_state.reset_key))
        
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
    st.sidebar.button("CLEAR 🗑️", on_click=lambda: [clear_chat_history(), clear_saved_files()])






