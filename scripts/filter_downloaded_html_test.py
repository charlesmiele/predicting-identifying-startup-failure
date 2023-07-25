import os
import pdb
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def main():
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

        return (count < 2)

    co_list = [f for f in os.listdir(
        '../data/SubsetHTML') if not f.startswith('.')]

    missed_timestamps = pd.DataFrame(
        columns=['entityid', 'timestamp', 'notes'])

    for company in co_list:
        print(company)

        # TODO: Fix
        timestamps = pd.read_csv(
            f"../data/SubsetTimestamps/{company}_timestamps.csv")
        timestamps = timestamps['timestamp'].astype(str).values.tolist()
        years = [t[:4] for t in timestamps]
        months = [t[4:6] for t in timestamps]

        for time in range(len(timestamps)):
            # TODO: Fix
            index_path = os.path.join(
                f"../data/SubsetHTML/{company}/{years[time]}/{months[time]}/index.html")
            data = {
                'entityid': company,
                'timestamp': timestamps[time],
                'notes': ""
            }
            # Open file
            if os.path.isfile(index_path):
                with open(index_path, 'r') as file:
                    # Read file
                    html_content = file.read()
                    file_size = int(os.stat(index_path).st_size / 1024)
                    # Empty file
                    if file_size == 0:
                        data['notes'] = 'emptyFile'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # Try to parse
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        data['notes'] = 'unparsable'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    body_tag = soup.body
                    if body_tag:
                        num_inside_body = len(body_tag.find_all())
                        # Not a lot of elements in the webpage (suspect)
                        if num_inside_body < 3:
                            data['notes'] = 'SmallBody'
                            missed_timestamps = missed_timestamps.append(
                                data, ignore_index=True)
                            continue
                    else:
                        # No body tag
                        data['notes'] = 'NoBody'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    soup_str = soup.get_text()
                    # 429 Text
                    if soup_str == errortxt_429:
                        data['notes'] = '429Error'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # Includes a lot of JavaScript (suspect)
                    if detect_jsheavy(soup):
                        data['notes'] = 'JSHeavy'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # It's good now
                    data['notes'] = 'Good'
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
            else:
                # Couldn't find the file
                data['notes'] = 'MissingFile'
                missed_timestamps = missed_timestamps.append(
                    data, ignore_index=True)

    # 4. How many companies have we downloaded partially?
    missed_timestamps.to_csv(f"missed_timestamps_sample.csv", index=False)


if __name__ == "__main__":
    main()
