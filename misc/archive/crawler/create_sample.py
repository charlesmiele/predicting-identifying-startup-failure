import pandas as pd

sample_num = 3

df = pd.read_csv('startup_url_list.csv')
df = df.sample(20)
df.to_csv(f"url_sample_{sample_num}.csv", index=False)
