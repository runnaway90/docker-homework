import pandas as pd

df = pd.read_parquet('/workspaces/docker-homework/green_tripdata_2025-11.parquet')

print(df.head())