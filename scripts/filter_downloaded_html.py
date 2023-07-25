import os
import pdb
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import sys

# SETUP

errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"


def detect_jsheavy(soup):
    x = {
        'p_count': ['p'],
        'h_count': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        'img_count': ['img'],
        'a_count': ['a'],
    }

    count = 0
    script_sum = len(soup.find_all('script'))

    for i in x:
        for y in x[i]:
            count += len(soup.find_all(y))

    return (count < 10 and count < script_sum and script_sum > 3)


'''
i = int(os.getenv('SGE_TASK_ID'))
range_i = int(os.getenv('SGE_TASK_LAST')) - \
    int(os.getenv('SGE_TASK_FIRST')) + 1
'''
i = sys.arg[1]
range_i = 200 - 1


# Get list of HTML directories (identified by entityids)
co_list = [f for f in os.listdir(
    '../data/html') if not f.startswith('.')]

# Create interval
intervals = np.linspace(0, len(co_list), range_i + 1)
intervals = intervals.astype(int).tolist()
start = intervals[i - 1]
finish = intervals[i]

co_list = co_list[start:finish]


# Create empty DataFrame that will be used to tag files
missed_timestamps = pd.DataFrame(
    columns=['entityid', 'timestamp', 'filepath', 'notes'])

# MAIN LOOP
# Iterate through companies (must have at least one downloaded page)
for company in co_list[1:100]:
    print(company)
    '''
    if co_list.index(company) % 100 == 0:
        print(co_list.index(company))
    '''

    # Look at company's timestamps
    timestamps = pd.read_csv(
        f"../data/optimal-timestamps/{company}_timestamps.csv")
    timestamps = timestamps['timestamp'].astype(str).values.tolist()
    years = [t[:4] for t in timestamps]  # Get year
    months = [t[4:6] for t in timestamps]  # Get month

    company_directory = f"../data/html/{company}"  # Get HTMLs

    # Iterate through times in timestamps
    for time in range(len(timestamps)):
        # Create index path
        index_path = os.path.join(
            company_directory, f"{years[time]}/{months[time]}/index.html")

        # Fill in row values
        data = {
            'entityid': company,
            'timestamp': timestamps[time],
            'filepath': index_path,
            'notes': ""
        }

        # See if file exists
        if os.path.isfile(index_path):
            # Open file
            with open(index_path, 'r') as file:
                html_content = file.read()  # Ready file
                # Get file size
                file_size = int(os.stat(index_path).st_size / 1024)

                if file_size == 0:
                    # Empty file
                    data['notes'] = 'emptyFile'
                    # Add row
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
                    continue

                try:
                    # Try to parse it
                    soup = BeautifulSoup(html_content, 'html.parser')
                except UnboundLocalError:
                    # Unparsable
                    data['notes'] = 'unparsable'
                    # Add row
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
                    continue

                body_tag = soup.body
                if body_tag:
                    num_inside_body = len(body_tag.find_all())
                    if num_inside_body < 5:
                        # Only 5 tags inside <body>
                        data['notes'] = 'SmallBody'
                        # Add row
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                # ^ There's no 'else' here because some websites forget to add body tags, but they're fine

                soup_str = soup.get_text()
                # 429 Error (specific)
                if soup_str == errortxt_429:
                    data['notes'] = '429Error'
                    # Add row
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
                    continue

                # Includes a weird amount of JavaScript
                if detect_jsheavy(soup):
                    data['notes'] = 'JSHeavy'
                    # Add row
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
                    continue

        else:
            # File doesn't exist
            data['notes'] = 'MissingFile'

        missed_timestamps = missed_timestamps.append(
            data, ignore_index=True)

# 4. How many companies have we downloaded partially?
missed_timestamps.to_csv(f"LogReport/{i}.csv", index=False)
