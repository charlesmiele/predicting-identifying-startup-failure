import pandas as pd
import os
from bs4 import BeautifulSoup
import pdb

errorTxt = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"

# Create empty DF
lr_columns = ['entityid', 'error', 'filepath']
lr = pd.DataFrame(columns=lr_columns)

overall_count = 0
missing_429 = 0
missing_file = 0

# Iterate through all the files
co_list = [f for f in os.listdir('data/html') if not f.startswith('.')]
for company in co_list:
    print(company)
    print(co_list.index(company), "out of", len(co_list))
    timestamps = pd.read_csv(
        f"data/optimal-timestamps/{company}_timestamps.csv")
    timestamps = timestamps['timestamp'].astype('str').tolist()
    years = [t[:4] for t in timestamps]
    months = [t[4:6] for t in timestamps]

    company_directory = f"data/html/{company}"

    for time in range(len(timestamps)):
        overall_count += 1
        # This line looks confusing, but it works since `years` and `months` are of equal length
        index_path = os.path.join(
            company_directory, f"{years[time]}/{months[time]}/index.html")
        if os.path.isfile(index_path):
            with open(index_path, 'r') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                soup_str = soup.get_text()
                if soup_str == errorTxt:
                    lr = lr.append(
                        {'enityid': company, 'error': 0, 'filepath': index_path}, ignore_index=True)
                    missing_429 += 1
        else:
            # Missing file
            lr = lr.append(
                {'enityid': company, 'error': 1, 'filepath': index_path}, ignore_index=True)
            missing_file += 1

lr.to_csv('data/missing_429s.csv', index=False)

# Summary statistics
pdb.set_trace()
