
# Função principal para processar os dados de texto e encontrar tópicos

# Função principal para processar os dados de texto e encontrar tópicos
def find_topic(df, text_column, nr_topics=None):
    import re
    import pandas as pd
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords

    from bertopic import BERTopic
    from umap import UMAP
    from tqdm import tqdm
    import streamlit as st

    def clean(text):
        if pd.isna(text) or text is None:
            return ''
        text = (" ".join(x.lower() for x in text.split()))  # Transformar palavras em minúsculas
        text = re.sub('[1234567890]', ' ', text)  # Remover números
        text = re.sub('[^\w\s\n]', ' ', text)  # Remover espaços e quebras de linha
        text = re.sub(' +', ' ', text)  # Remover espaços duplos
        chars_to_remove = ['.', '/', '´', '`', '?', '!', '$', '%', '^', '&',
                           '*', '(', ')', '-', '_', '+', '=', '@', ':', '\\', ',',
                           ';', '<', '>', '|', '[', ']', '{', '}', '–', '“','»', '«', '°', '’']
        rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
        text = re.sub(rx, ' ', text)
        return text

    def remove_stopwords(text):
        stop_words = set(stopwords.words("english"))
        text = " ".join(x for x in text.split() if x not in stop_words)
        return text

    df['clean'] = ''

    for row_index, text in tqdm(enumerate(df[text_column])):
        text = clean(text)
        text = remove_stopwords(text)
        df.at[row_index, 'clean'] = text

    docs = df[df['clean'] != '']['clean']

    umap_model = UMAP(metric='cosine', random_state=42)  # Configurar semente
    topic_model = BERTopic(language="english", calculate_probabilities=True, verbose=True, umap_model=umap_model, nr_topics=nr_topics).fit_transform(docs)
    #topics, probs = topic_model.fit_transform(docs)

    plot = topic_model.visualize_topics()

    return st.pyplot(plot)

# Exemplo de uso


# Exemplo de uso
# topic_model, topics, probs = find_topic(df, 'Study_design', nr_topics=None)
