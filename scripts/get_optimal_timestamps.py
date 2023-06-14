import pandas as pd
import datetime as dt
import os
import datetime
import pdb
import numpy as np

# 6 month buffers for start date and end date
START_DATE_BUFFER = 180
END_DATE_BUFFER = 180

# Used for easier compatibility w/ remote server
script_path = os.path.abspath(__file__)
script_path = os.path.dirname(script_path)

# Import master url list
url_list_path = os.path.join(
    script_path, '../data/missing_jsons_executable.csv')
url_list = pd.read_csv(url_list_path)

# List all JSON files
timestamp_list = os.listdir(os.path.join(script_path, '../data/raw-json'))


# Create log report dataframe which will contain relevant info for debugging
log_report = pd.DataFrame(columns=["entityid", "domain", "time_of_run", "earliest_screenshot", "start_date_with_buffer",
                                   "latest_screenshot", "end_date_with_buffer", "file_path", "failed", "reason_for_failure", ])

# Function that adds to the log row dataframe


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
        'earliest_screenshot': "" if earliest_screenshot == "" else earliest_screenshot.strftime('%Y-%m-%d %H:%M:%S'),
        'start_date_with_buffer': start_date,
        'latest_screenshot': "" if latest_screenshot == "" else latest_screenshot.strftime('%Y-%m-%d %H:%M:%S'),
        'end_date_with_buffer': end_date,
        'file_path': file_path
    }
    log_report = log_report.append(new_row, ignore_index=True)


# Iterate through url list
for index, row in url_list.iterrows():
    company_id = row['entityid']
    domain = row['weburl']
    file_id = str(company_id) + '.csv'

    if file_id not in timestamp_list:
        # Add company to log report
        add_log_row(company_id, domain, start_date=row.startdate, end_date=row.exit_date, earliest_screenshot="",
                    latest_screenshot="", failed=1, reason_for_failure="No JSON data")
        continue

    print("Now working on", company_id)

    # Read company JSON data
    json_data = pd.read_csv(os.path.join(
        script_path, f"../data/raw-json/{file_id}"))

    # Only text/html files & status-code == 200
    subset_json_data = json_data[(json_data["mimetype"] == "text/html")
                                 & (json_data["statuscode"] == '200')]

    # Read 'timestamp' column as a string
    timestamp_string = subset_json_data['timestamp'].astype(str)
    format_string = "%Y%m%d%H%M%S"
    # Convert all rows in the column to a datetime object
    timestamps = pd.to_datetime(
        timestamp_string, format=format_string, errors='coerce')
    # Drops any timestamps that did not match format (specified in format_string)
    timestamps.dropna()

    # If the company has no start date, we can't use it
    if pd.isna(row.startdate):
        if pd.isna(row.lastVC):
            add_log_row(company_id, domain, start_date=row.startdate, end_date=row.exit_date, earliest_screenshot="",
                        latest_screenshot="", failed=1, reason_for_failure="Missing start date and LastVC")
            continue
        else:
            # Use lastVC as startdate
            s_date = pd.to_datetime(row.lastVC) - \
                pd.Timedelta(days=START_DATE_BUFFER)
    else:
        # Add buffer
        s_date = pd.to_datetime(row.startdate) - \
            pd.Timedelta(days=START_DATE_BUFFER)
    if pd.isnull(row.exit_date):
        # Hardcoded to last time I ran the JSON search
        e_date = pd.Timestamp(year=2023, month=6, day=6)
    else:
        # Add buffer
        e_date = pd.to_datetime(row.exit_date) + \
            pd.Timedelta(days=END_DATE_BUFFER)

    # Select only timestamps that fit within company life-span
    timestamps = timestamps[(timestamps >= s_date)
                            & (timestamps <= e_date)]

    # If no timestamps found, move on to next company
    if timestamps.size == 0:
        add_log_row(company_id, domain, start_date=s_date, end_date=e_date, earliest_screenshot="",
                    latest_screenshot="", failed=1, reason_for_failure="No timestamps within company life span")
        continue

    # Create 6-month intervals
    # Goal is to start at start date
    if timestamps[(timestamps >= s_date) & (timestamps <= s_date + pd.Timedelta(days=START_DATE_BUFFER))].size != 0:
        intervals = pd.Series(s_date)
    else:
        # But if there is not one within 6 months after that date,
        # then start with first available
        intervals = pd.Series(timestamps.min())

    # Create date range series that go in 6-month increments. Goal is to find a date for each interval
    intervals = pd.Series(pd.date_range(
        start=s_date, end=e_date, freq='6M').union(pd.Index([s_date, e_date])))

    # Create an empty series that will contain datetime objects
    # This will contain final timestamps for use on "GET" script
    optimal_intervals = pd.Series(dtype="datetime64[ns]")

    # Iterate through each 6-month interval...
    for index, value in intervals.items():
        # If we're NOT at the final interval
        # (Else statement unnecessary due to method of finding timestamps)
        if index != (intervals.size - 1):
            # Find timestamps that fall within current interval date and next interval
            sub_interval = timestamps[(timestamps >= intervals.iloc[index]) & (
                timestamps <= intervals.iloc[index + 1])]
            # If sub_interval isn't empty...
            if sub_interval.size != 0:
                # If we're at the beginning of the interval series
                # AND we don't just have one date in the sub_interval
                # Also add the minimum of the sub_interval
                if optimal_intervals.size == 0 and sub_interval.size > 1:
                    optimal_intervals = optimal_intervals.append(
                        pd.Series(sub_interval.min()))
                # In any case, add the max of the interval
                optimal_intervals = optimal_intervals.append(
                    pd.Series(sub_interval.max()))

    # If we don't have an empty series of optimal intervals...
    if optimal_intervals.size != 0:
        # Convert to string to format that matches internet archive format
        optimal_intervals_str = optimal_intervals.dt.strftime(
            '%Y%m%d%H%M%S')
        # Export this as a CSV file
        optimal_intervals_str.to_csv(os.path.join(
            script_path, f"../data/optimal-timestamps/{company_id}_timestamps.csv"), index=False, header=["timestamp"])
        # Finally, add company to the log report
        add_log_row(company_id, domain,  s_date, e_date, earliest_screenshot=optimal_intervals.iloc[
                    0], latest_screenshot=optimal_intervals.iloc[-1], failed=0, file_path=f"optimal_timestamps/{company_id}_timestamps.csv")

# Export log report
log_report.to_csv(os.path.join(
    script_path, '../log-reports/optimal_timestamp_log_report_finale_2.csv'), index=False)
