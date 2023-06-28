import pandas as pd
import os
from bs4 import BeautifulSoup

errorTxt = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"


# Select random sample of "0.0" errors
df = pd.read_csv('data/missing_429s.csv')
df = df[df['error'] == 0.0].sample(20)

for index, row in df.iterrows():
    print("Filepath:", row.filepath)
    print('---Lines---')
    with open(row.filepath, 'r') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        soup_str = soup.get_text()
        print(soup_str == errorTxt)
