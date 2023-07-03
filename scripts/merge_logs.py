import pandas as pd
import os

df = pd.read_csv('../log-reports/missed-timestamps/1.csv')

for i in range(2, 201):
    dfi = pd.read_csv(f"../log-reports/missed-timestamps/{i}.csv")
    df = pd.concat([df, dfi], ignore_index=True)

df.to_csv('../log-reports/missed-timestamps.csv')
print('exported 1')

df2 = pd.read_csv('../log-reports/completely-finished/1.csv')

for i in range(2, 201):
    dfi = pd.read_csv(f"../log-reports/completely-finished/{i}.csv")
    df2 = pd.concat([df2, dfi], ignore_index=True)

df2.to_csv('../log-reports/completely-finished.csv')
print('exported 2')
