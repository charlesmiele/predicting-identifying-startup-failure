import requests
import pandas as pd
import time
import csv
import os
import numpy as np
import pdb
import datetime


np.set_printoptions(suppress=True)


BASE_PATH = '/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/get_timestamps/'
URL_LIST_PATH = BASE_PATH + 'startup_url_list.csv'


url_list = pd.read_csv(URL_LIST_PATH)
# url_list = url_list[72814:]

# Find not yet downloaded
timestamp_list = os.listdir(
    '/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/get_timestamps/out')
timestamp_list = [int(file_name[:-4]) for file_name in timestamp_list]
not_downloaded = [x for x in url_list.entityid if x not in timestamp_list]

url_list = url_list[url_list['entityid'].isin(not_downloaded)]

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
    log_report.to_csv(
        '/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/get_timestamps/log_report.csv')


for index, row in url_list.iterrows():
    domain = row['weburl']
    company_id = int(row['entityid'])
    url = f"https://web.archive.org/web/timemap/json?url={domain}/"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        timestamps = response.json()

        # Define the CSV file path
        directory_path = "/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/get_timestamps/out/"
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
    '/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/get_timestamps/log_report.csv')
