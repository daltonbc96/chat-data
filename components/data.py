import pandas as pd
import streamlit as st
import os

@st.cache_data(show_spinner=False)
def extract_dataframes(files):
    dfs = {}
    for file in files:
        file_extension = file.name.split('.')[-1].lower()
        if file_extension == 'csv':
            csv_name = file.name.split('.')[0]
            df = pd.read_csv(file)
            dfs[csv_name] = {'Sheet1': df}
        elif file_extension in ['xlsx', 'xls']:
            xls = pd.ExcelFile(file)
            sheet_dfs = {sheet_name: pd.read_excel(file, sheet_name=sheet_name) for sheet_name in xls.sheet_names}
            dfs[file.name] = sheet_dfs
        elif file_extension == 'parquet':
            parquet_name = file.name.split('.')[0]
            df = pd.read_parquet(file, engine="pyarrow")
            dfs[parquet_name] = {'Sheet1': df}
        else:
            st.error(f"Unsupported file type: {file.name}! Please upload a CSV, Excel, or Parquet file.")
    return dfs

@st.cache_data(show_spinner=False)
def load_data_from_folder(folder_path):
    dfs = {}
    with st.spinner('Loading data from local folder...'):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            file_extension = file_name.split('.')[-1].lower()
            if file_extension == 'csv':
                df = pd.read_csv(file_path)
                dfs[file_name] = {'Sheet1': df}
            elif file_extension in ['xlsx', 'xls']:
                xls = pd.ExcelFile(file_path)
                sheet_dfs = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name) for sheet_name in xls.sheet_names}
                dfs[file_name] = sheet_dfs
            elif file_extension == 'parquet':
                try:
                    df = pd.read_parquet(file_path, engine="pyarrow")
                    dfs[file_name] = {'Sheet1': df}
                except Exception as e:
                    st.error(f"Error reading {file_name}: {e}")
            else:
                st.error(f"Unsupported file type: {file_name}! Please ensure the folder contains only CSV, Excel, or Parquet files.")
    return dfs


