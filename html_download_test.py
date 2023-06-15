import pandas as pd
import datetime
import time
import os
import requests
import codecs
import pdb
from requests.exceptions import ConnectionError

url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = os.listdir('data/optimal-timestamps')
timestamp_list = [int(file[:-15]) for file in timestamp_list]
url_list = url_list[url_list.entityid.isin(timestamp_list)]
url_list = url_list.sample(3)

finished_cos = []

already_crawled = []

# TODO: Think more about this

lr_columns = [
    'entityid',
    'domain',
    'time_of_run',
    'download_timestamp',
    'download_url',
    'failed',
    'reason_for_failure',
    'failure_description',
    'file_path'
]

lr_path = 'log-reports/html_master_log_report.csv'
if os.path.isfile(lr_path):
    log_report = pd.read_csv(lr_path)
else:
    log_report = pd.DataFrame(columns=lr_columns)


def add_log_row(entityid, domain, download_timestamp, download_url, failed=0, reason_for_failure="", failure_description="", file_path=""):
    global log_report
    # Create a date/time object for the current moment
    current_datetime = datetime.datetime.now()
    # Convert the date/time object to a string
    datetime_string = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    new_row = {
        'entityid': entityid,
        'domain': domain,
        'time_of_run': datetime_string,
        'download_timestamp': int(download_timestamp),
        'download_url': download_url,
        'failed': failed,
        'reason_for_failure': reason_for_failure,
        'failure_description': failure_description,
        'file_path': file_path
    }
    log_report = log_report.append(new_row, ignore_index=True)


def store_page(entityid, year, month):
    base_directory = f"data/html/{entityid}/{year}/{month}"

    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    file_path = f"{base_directory}/index.html"

    outfile = codecs.open(file_path, "w", 'utf-8')
    outfile.write(html)
    outfile.close()
    return file_path


# For every company...
for index, row in url_list.iterrows():
    # Meta data
    domain = row['weburl']
    company_id = int(row['entityid'])

    print(company_id, "is up")

    # Load in optimal timestamps for current company
    timestamps = pd.read_csv(
        f"data/optimal-timestamps/{company_id}_timestamps.csv")
    timestamps = timestamps['timestamp'].values
    # Convert to string (easier to work with, and they all have the same format)
    timestamps = [str(t) for t in timestamps]

    for t in timestamps:
        # Create more metadata
        year = t[:4]
        month = t[4:6]
        url = f"https://web.archive.org/web/{t}/{domain}"

        try:
            # GET request
            response = requests.get(url)
            # Store HTML contents
            html = response.text
            # Store page
            file_path = store_page(company_id, year, month)
            # Add to log file as success
            print("Downloaded", t)
            add_log_row(company_id, domain, t, url, file_path=file_path)
        except ConnectionError as e:
            print(e)
            # Add to log file as a failure
            print("Could not download", t)
            add_log_row(company_id, domain, t, url, failed=1,
                        reason_for_failure="Connection Error", failure_description=e)

    print("Finished", company_id)


# Export log report to CSV
log_report.to_csv(lr_path, index=False)

print("Exported log report")
