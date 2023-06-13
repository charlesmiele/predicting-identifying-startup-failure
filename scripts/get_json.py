import requests
import pandas as pd
import time
import csv
import os
import numpy as np
import pdb
import datetime
import subprocess


# Used for easier compatibility w/ remote server
script_path = os.path.abspath(__file__)
script_path = os.path.dirname(script_path)


# Import master url list
url_list_path = os.path.join(script_path, '../data/startup_url_list.csv')
url_list = pd.read_csv(url_list_path)

# Find not yet downloaded
json_log = pd.read_csv(os.path.join(
    script_path, '../log-reports/archive/json-log-report.csv'))
json_log = json_log[json_log.reason_for_failure != "NoJSON"]
missing_ids = json_log.entityid

url_list = url_list[url_list['entityid'].isin(missing_ids)]

could_not_connect = []
no_json = []
timed_out = []

log_report = pd.DataFrame(columns=[
                          'entityid', 'domain', 'time_of_run', 'failed', 'reason_for_failure', 'file_path'])


def add_log_row(entityid, domain, failed=0, reason_for_failure="", file_path=""):
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
        'file_path': file_path
    }
    log_report = log_report.append(new_row, ignore_index=True)


for index, row in url_list.iterrows():
    domain = row['weburl']
    company_id = int(row['entityid'])
    url = f"https://web.archive.org/web/timemap/json?url={domain}/"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        timestamps = response.json()

        # Define the CSV file path
        directory_path = "/Users/charlesmiele/Dropbox/miele/data/raw-json/"
        file_name = f"{company_id}.csv"
        csv_file_path = os.path.join(directory_path, file_name)

        if timestamps != []:
            # Write the timestamps to the CSV file
            with open(csv_file_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(timestamps)
            print(company_id, "success")
        else:
            add_log_row(company_id, domain, 1, "NoJSON")
    except requests.exceptions.HTTPError as E:
        add_log_row(company_id, domain, 1, E)
    except requests.exceptions.ChunkedEncodingError:
        add_log_row(company_id, domain, 1, "ChunkedEncodingError")
    except requests.exceptions.ConnectionError:
        add_log_row(company_id, domain, 1, "ConnectionError")
    except requests.exceptions.Timeout:
        add_log_row(company_id, domain, 1, "Timeout")


log_report.to_csv(
    '/Users/charlesmiele/Dropbox/miele/log-reports/json-log-report-06-13.csv')

subprocess.call(["python3", os.path.join(
    script_path, "get_optimal_timestamps.py")])
