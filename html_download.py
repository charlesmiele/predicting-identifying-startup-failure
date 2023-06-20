import pandas as pd
import datetime
import time
import os
import requests
import codecs
import pdb
import sys
import filter_downloaded_html as fdh
import downloaded_6_20 as downloaded
import numpy as np


# Read environment variables
# i = int(os.getenv('SGE_TASK_ID'))
i = 5
# range_i = int(os.getenv('SGE_TASK_LAST') -
#   int(os.getenv('SGE_TASK_FIRST'))) + 1
range_i = 5 - 1 + 1

# Read data
url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = os.listdir('data/optimal-timestamps')
timestamp_list = [int(file[:-15]) for file in timestamp_list]

# Find already finished, take them out
# --This is hardcoded for now to prevent any bugs--
already_finished = downloaded.companies
url_list = url_list[(url_list.entityid.isin(timestamp_list)) & (
    url_list.entityid.isin(already_finished) == False)]

# Calculate given interval
num_urls = len(url_list.index)
intervals = np.linspace(0, num_urls, range_i + 1)
intervals = intervals.astype(int).tolist()

start = intervals[i - 1]
finish = intervals[i]

url_list = url_list.iloc[start:finish]


lr_path = f"log-reports/lp_p_{i}.csv"

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
        # TODO: Clean this up...I shouldn't have to add that exist_ok argument...
        os.makedirs(base_directory, exist_ok=True)

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
            response = requests.get(url, timeout=10)
            # Store HTML contents
            html = response.text
            # Store page
            file_path = store_page(company_id, year, month)
            # Add to log file as success
            print("Downloaded", t)
            add_log_row(company_id, domain, t, url, file_path=file_path)
        except requests.exceptions.ConnectionError as e:
            # Add to log file as a failure
            print("Could not download", t, ": ConnectionError")
            add_log_row(company_id, domain, t, url, failed=1,
                        reason_for_failure="Connection Error", failure_description=e)
        except requests.exceptions.Timeout as e:
            print("Could not download", t, ": Timout")
            add_log_row(company_id, domain, t, url, failed=1,
                        reason_for_failure="Timeout Error", failure_description=e)
        except requests.exceptions.ChunkedEncodingError as e:
            print("Could not download", t, ": CEE")
            add_log_row(company_id, domain, t, url, failed=1,
                        reason_for_failure="Chunked Encoding Error", failure_description=e)
            time.sleep(10)
        except Exception as e:
            print("Could not download", t, ": Unknown")
            add_log_row(company_id, domain, t, url, failed=1,
                        reason_for_failure="Chunked Encoding Error", failure_description=e)
            time.sleep(10)

    print("Finished", company_id)

# Export log report to CSV
log_report.to_csv(lr_path, index=False)

print("Exported log report")
