#from typing import Optional
from pandasai import Agent
from pandasai.responses.streamlit_response import StreamlitResponse
from pandasai.skills import skill
import pandas as pd



#import re
#import pandas as pd
#from bertopic import BERTopic
#from umap import UMAP
#from tqdm import tqdm
#from sklearn.feature_extraction.text import TfidfVectorizer



def get_agent(data, llm, agent_context):
    extras = "Modify the generated code to be compatible with Streamlit. Specifically, replace fig.show() with fig.write_json('temp_plot.json') and use the library import plotly.express as px."
    agent = Agent(data, description=agent_context + extras,
                  config={"llm": llm, "verbose": True, "open_charts": False,
                         "response_parser": StreamlitResponse, 
                          "enforce_privacy": False,
                          "max_retries": len(data),
                     
                          "response_parser": None,  
                          "enable_cache": True,             
                          "custom_whitelisted_dependencies": ["seaborn", "gensim", "ydata_profiling", "streamlit_ydata_profiling", "plotly", "wordcloud", "string", "bertopic", "umap", "tqdm", "sklearn"]})
    #agent.add_skills(find_topic)
    #agent.add_skills(plot_line_chart)
    return agent





# def clean_text(text: str) -> str:
#     if pd.isna(text) or text is None:
#         return ''
#     text = text.lower()
#     text = re.sub(r'\d+', ' ', text)  # Remove numbers
#     text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
#     text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
#     return text.strip()

# from gensim.models.doc2vec import Doc2Vec, TaggedDocument

# from sklearn.preprocessing import normalize

# @skill
# def find_topic(df: pd.DataFrame, text_column: str, nr_topics: Optional[int] = None):
#     """
#     Generate topics from the specified column in the DataFrame. The user can also define the number of topics. 
#     The function cleans the text, removes stopwords, and then uses BERTopic to generate the topics. 
#     Finally, it visualizes the topics using Streamlit.

#     Args:
#         df (pd.DataFrame): The input DataFrame containing the text data.
#         text_column (str): The name of the column containing the text data.
#         nr_topics (Optional[int]): The number of topics to generate. If None, it will use the default number of topics.
#     """
#     # Clean and preprocess text
#     df['clean'] = df[text_column].apply(lambda x: clean_text(x))

#     docs = df[df['clean'] != '']['clean']

#     documents = [TaggedDocument(doc.split(), [i]) for i, doc in enumerate(docs)]

#     # Treinamento do modelo Doc2Vec
#     model = Doc2Vec(documents, vector_size=2, window=2, min_count=1, workers=4, epochs=10)

#     # Transformação dos documentos em vetores
#     doc_vectors = [model.infer_vector(doc.words) for doc in documents]
#     doc_vectors = normalize(doc_vectors)

#     # Configuração do BERTopic
#     topic_model = BERTopic(vectorizer_model=None)

#     # Ajuste do modelo BERTopic
#     topics, probs = topic_model.fit_transform(docs.tolist(), embeddings=doc_vectors)

#     return topic_model, topics, probs





import pandas as pd
import plotly.express as px
from pandasai.skills import skill

@skill
def plot_line_chart(df: pd.DataFrame, x_column: str, y_column: str):
    """
    Generate a line plot using the specified columns for the x and y axes specified by the user. 
    
    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        x_column (str): The name of the column to be used for the x-axis.
        y_column (str): The name of the column to be used for the y-axis.
    """
    # Handle non-numeric data in x_column
    if df[x_column].dtype == 'object':
        df[x_column] = df[x_column].astype('category').cat.codes

    # Handle non-numeric data in y_column
    if df[y_column].dtype == 'object':
        df[y_column] = df[y_column].astype('category').cat.codes

    # Plot using Plotly Express
    fig = px.line(df, x=x_column, y=y_column, title=f'Line Chart of {y_column} vs {x_column}')
    fig.write_json("temp_plot.json")
    return "Plot created successfully and saved as temp_plot.json"
