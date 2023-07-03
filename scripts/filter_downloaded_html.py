import os
import pdb
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def main():
    errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"

    i = int(os.getenv('SGE_TASK_ID'))
    range_i = int(os.getenv('SGE_TASK_LAST')) - \
        int(os.getenv('SGE_TASK_FIRST')) + 1
    OUTPUT_PATH = f"../log-reports"

    co_list = [f for f in os.listdir('../data/html') if not f.startswith('.')]

    # Create interval
    intervals = np.linspace(0, len(co_list), range_i + 1)
    intervals = intervals.astype(int).tolist()
    start = intervals[i - 1]
    finish = intervals[i]
    co_list = co_list[start:finish]

    missed_timestamps = pd.DataFrame(
        columns=['entityid', 'timestamp', 'notes'])

    finished_cos = []
    partially_finished = []

    for company in co_list:
        if co_list.index(company) % 100 == 0:
            print(co_list.index(company))

        timestamps = pd.read_csv(
            f"../data/optimal-timestamps/{company}_timestamps.csv")
        timestamps = timestamps['timestamp'].astype(str).values.tolist()
        years = [t[:4] for t in timestamps]
        months = [t[4:6] for t in timestamps]

        company_directory = f"../data/html/{company}"

        remaining_timestamps = timestamps.copy()

        for time in range(len(timestamps)):
            index_path = os.path.join(
                company_directory, f"{years[time]}/{months[time]}/index.html")
            if os.path.isfile(index_path):
                with open(index_path, 'r') as file:
                    html_content = file.read()

                    file_size = int(os.stat(index_path).st_size / 1024)
                    if file_size == 0:
                        missed_timestamps = missed_timestamps.append(
                            {'entityid': company, 'timestamp': timestamps[time], 'notes': 'emptyFile'}, ignore_index=True
                        )
                        continue
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        missed_timestamps = missed_timestamps.append(
                            {'entityid': company, 'timestamp': timestamps[time], 'notes': 'unparsable'}, ignore_index=True
                        )
                        continue
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        missed_timestamps = missed_timestamps.append(
                            {'entityid': company, 'timestamp': timestamps[time], 'notes': '429Error'}, ignore_index=True
                        )
                        continue
                remaining_timestamps.remove(timestamps[time])
            else:
                missed_timestamps = missed_timestamps.append(
                    {'entityid': company, 'timestamp': timestamps[time], 'notes': 'missingFile'}, ignore_index=True
                )

        if len(remaining_timestamps) == 0:
            finished_cos.append(int(company))
        else:
            partially_finished.append(len(remaining_timestamps))

    # 1. How many companies have we downloaded, at-least partially?

    # 3. How many companies are we still missing (completely)?

    # 2. How many companies have we downloaded completely, in full?
    finished_cos = pd.Series(finished_cos)
    finished_cos.to_csv(
        OUTPUT_PATH + f"/completely-finished/{i}.csv", index=False)

    # 4. How many companies have we downloaded partially?
    missed_timestamps.to_csv(
        OUTPUT_PATH + f"/missed-timestamps/{i}.csv", index=False)

    return finished_cos


if __name__ == "__main__":
    main()
