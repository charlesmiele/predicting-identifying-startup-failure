import pandas as pd
import os
import numpy as np

# Read environment variables
i = int(os.getenv('SGE_TASK_ID'))
range_i = int(os.getenv('SGE_TASK_LAST')) - \
    int(os.getenv('SGE_TASK_FIRST')) + 1

# Add grid stuff
jsons = os.listdir('../data/raw-json')

# Calculate given interval
num_urls = len(jsons)
intervals = np.linspace(0, num_urls, range_i + 1)
intervals = intervals.astype(int).tolist()
start = intervals[i - 1]
finish = intervals[i]
json_subset = jsons.iloc[start:finish]


df = pd.read_csv(
    f"../data/raw-json/{json_subset[0]}", dtype={'statuscode': object})
df['entityid'] = json_subset[0][:-4]
df = df.loc[df.statuscode == '200', ['entityid', 'timestamp']]

for i in range(2, len(json_subset)):
    if i % 1000 == 0:
        print(i)
    dfi = pd.read_csv(
        f"../data/raw-json/{json_subset[i]}", dtype={'statuscode': object})
    dfi['entityid'] = json_subset[i][:-4]
    dfi = dfi.loc[dfi.statuscode ==
                  '200', ['entityid', 'timestamp']]
    df = pd.concat([df, dfi], axis=0)

df.to_csv(f'../data/simple_jsons/df{i}.csv', index=False)
