import pandas as pd
import os
import pdb


df = pd.read_csv('../data/analysis-3/1_revised_webpage_metadata.csv')
for i in range(2, 51):
    try:
        dfi = pd.read_csv(
            f"../data/analysis-3/{i}_revised_webpage_metadata.csv")
        df = pd.concat([df, dfi], ignore_index=True)
        print(i, "has been concated")
        print(df['entityid'].nunique(), "companies")
        print(len(df.index), "rows")
        print("---")
    except pd.errors.EmptyDataError:
        print(i, "is empty.")
df.to_csv('../data/3_final_webpage_metadata.csv')
