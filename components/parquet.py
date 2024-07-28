import pandas as pd
df = pd.read_csv('data/trials_limpa.csv')
df.to_parquet('data/trials_limpa.parquet')