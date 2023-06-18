import os
import pdb
import pandas as pd


def main():
    co_list = os.listdir('data/html')
    finished_cos = []
    for company in co_list:
        timestamps = pd.read_csv(
            f"data/optimal-timestamps/{company}_timestamps.csv")
        timestamps = timestamps['timestamp'].astype(str).values.tolist()
        years = [t[:4] for t in timestamps]
        months = [t[4:6] for t in timestamps]

        company_directory = f"data/html/{company}"

        remaining_timestamps = timestamps.copy()

        for time in range(len(timestamps)):
            if os.path.isfile(os.path.join(company_directory, f"{years[time]}/{months[time]}/index.html")):
                remaining_timestamps.remove(timestamps[time])

        if len(remaining_timestamps) == 0:
            finished_cos.append(int(company))

    return finished_cos


if __name__ == "__main__":
    main()
