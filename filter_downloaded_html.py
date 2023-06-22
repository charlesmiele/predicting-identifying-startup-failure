import os
import pdb
import pandas as pd


def main():
    co_list = [f for f in os.listdir('data/html') if not f.startswith('.')]
    finished_cos = []
    partially_finished = []

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
        else:
            partially_finished.append(len(remaining_timestamps))

    # Summary
    print(len(finished_cos), "companies are completely finished")
    print("In ratio form:", len(finished_cos) / len(co_list))

    print(
        f"On average, companies with remaining timestamps are missing {sum(partially_finished) / len(partially_finished)}")

    # TODO: Export lingering timestamps to a CSV
    return finished_cos


if __name__ == "__main__":
    main()
