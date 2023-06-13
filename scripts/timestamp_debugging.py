import pandas as pd
import datetime as dt
import os
import datetime
import pdb
import numpy as np

script_path = os.path.abspath(__file__)
script_path = os.path.dirname(script_path)

url_list_path = os.path.join(script_path, '../data/startup_url_list.csv')
url_list = pd.read_csv(url_list_path)


random_sample = np.random.randint(78000, size=10)
url_list = url_list.iloc[random_sample]

timestamp_list = os.listdir(os.path.join(script_path, '../data/raw-json'))

START_DATE_BUFFER = 180
END_DATE_BUFFER = 180

log_report = pd.DataFrame(columns=["entityid", "domain", "time_of_run", "earliest_screenshot", "start_date_with_buffer",
                                   "latest_screenshot", "end_date_with_buffer", "file_path", "failed", "reason_for_failure", ])


def add_log_row(entityid, domain,  start_date, end_date, earliest_screenshot="", latest_screenshot="",  failed=0, reason_for_failure="", file_path=""):
    global log_report
    # Create a date/time object for the current moment
    current_datetime = datetime.datetime.now()
    # Convert the date/time object to a string
    datetime_string = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    new_row = {
        'entityid': entityid,
        'domain': domain,
        'time_of_run': datetime_string,
        'failed': failed,
        'reason_for_failure': reason_for_failure,
        'earliest_screenshot': "" if "" else earliest_screenshot.strftime('%Y-%m-%d %H:%M:%S'),
        'start_date_with_buffer': start_date,
        'latest_screenshot': "" if "" else latest_screenshot.strftime('%Y-%m-%d %H:%M:%S'),
        'end_date_with_buffer': end_date,
        'file_path': file_path
    }
    log_report = log_report.append(new_row, ignore_index=True)


for index, row in url_list.iterrows():
    company_id = row['entityid']
    domain = row['weburl']
    file_id = str(company_id) + '.csv'
    if file_id in timestamp_list:
        print("Now working on", company_id)
        df = pd.read_csv(os.path.join(
            script_path, f"../data/raw-json/{file_id}"))
        # Only text/html & status-code == 200
        subset_df = df[(df["mimetype"] == "text/html")
                       & (df["statuscode"] == '200')]

        # Reduce to list of timestamps (as datetime objects)
        # TODO: This is returning error on one company for some reason
        # Print the row it got screwed up on
        # Print timestamp it got caught on
        timestamp_string = subset_df['timestamp'].astype(str)
        format_string = "%Y%m%d%H%M%S"

        timestamps = pd.to_datetime(
            timestamp_string, format=format_string, errors='coerce')
        timestamps.dropna()

        if pd.isna(row.startdate):
            add_log_row(company_id, domain, start_date="", end_date="", earliest_screenshot="",
                        latest_screenshot="", failed=1, reason_for_failure="Missing start date")
            continue
        else:
            s_date = pd.to_datetime(row.startdate) - \
                pd.Timedelta(days=START_DATE_BUFFER)
        if pd.isnull(row.exit_date):
            # Hardcode to last time I ran the JSON search
            e_date = pd.Timestamp(year=2023, month=6, day=6)
        else:
            e_date = pd.to_datetime(row.exit_date) + \
                pd.Timedelta(days=END_DATE_BUFFER)

        timestamps = timestamps[(timestamps >= s_date)
                                & (timestamps <= e_date)]

        intervals = pd.Series(s_date)

        try:
            intervals = pd.Series(pd.date_range(
                start=s_date, end=e_date, freq='6M').union(pd.Index([s_date, e_date])))
        except:
            add_log_row(company_id, domain, start_date="", end_date="", earliest_screenshot="",
                        latest_screenshot="", failed=1, reason_for_failure="Missing start date")
            continue

        optimal_intervals = pd.Series(dtype="datetime64[ns]")

        # TODO: Break this down for the reader
        for index, value in intervals.items():
            if index != (intervals.size - 1):
                sub_interval = timestamps[(timestamps >= intervals.iloc[index]) & (
                    timestamps <= intervals.iloc[index + 1])]
                if sub_interval.size != 0:
                    if optimal_intervals.size == 0 and sub_interval.size != 0:
                        optimal_intervals = optimal_intervals.append(
                            pd.Series(sub_interval.min()))
                    optimal_intervals = optimal_intervals.append(
                        pd.Series(sub_interval.max()))

        if optimal_intervals.size != 0:
            optimal_intervals = optimal_intervals.dt.strftime('%Y%m%d%H%M%S')
            optimal_intervals.to_csv(os.path.join(
                script_path, f"../data/optimal-timestamps/{company_id}_timestamps.csv"), index=False, header=["timestamp"])
            optimal_intervals = pd.to_datetime(
                optimal_intervals, format=format_string)
            add_log_row(company_id, domain,  s_date, e_date, earliest_screenshot=optimal_intervals.iloc[
                        0], latest_screenshot=optimal_intervals.iloc[-1], failed=0, file_path=f"optimal_timestamps/{company_id}_timestamps.csv")

log_report.to_csv(os.path.join(
    script_path, '../log-reports/optimal_timestamp_log_report.csv'), index=False)
