import pandas as pd
from waybackmachine_crawler import waybackmachine_crawler
import datetime
from dateutil.relativedelta import relativedelta
import time
import dateparser
today = datetime.date.today()

BASE_PATH = '/Users/charlesmiele/Dropbox/miele/measuring-founding-strategy-main/crawler/'
URL_LIST_PATH = BASE_PATH + 'url_sample_2.csv'
OUTPUT_FOLDER = 'Jun_5_out_2'
LOG_REPORT = 'Jun_5_Report_2.csv'

cur_year = today.year

url_list = pd.read_csv(URL_LIST_PATH)


finished_cos = []

already_crawled = []

for index, row in url_list.iterrows():
    domain = row['weburl']
    company_id = int(row['entityid'])

    if company_id in finished_cos:
        continue

    co_crawler = waybackmachine_crawler(
        domain, company_id, output_folder=OUTPUT_FOLDER, year_folder=True)

    print("Checkpoint 1")

    # This begins at the start date
    cur_date = dateparser.parse(row['startdate'])

    end_date = row['exit_date']
    if pd.isna(end_date):
        end_yr = cur_year
    else:
        end_yr = dateparser.parse(end_date).year

    log_report = None

    print("Cur date", cur_date.year)
    print("End date", end_yr)

    while cur_date.year < end_yr:
        snapshot = co_crawler.list_closest_snapshot(
            cur_date.year, cur_date.month, cur_date.day)
        if snapshot != None and snapshot['url'] not in already_crawled:
            already_crawled.append(snapshot['url'])
            snap_t = snapshot['timestamp']
            snap_t = datetime.datetime.strptime(snap_t, "%Y%m%d%H%M%S")

            co_crawler.crawled_year = snap_t.year
            co_crawler.crawled_month = snap_t.month

            # ---LOG REPORT---
            # TODO: Make this more efficient

            # the crawl function saves the html, but it returns the log report
            print("Crawling")
            log_report = co_crawler.crawl(snapshot['url'], snap_t)
            print("Crawled")

            cur_date = snap_t + relativedelta(months=6)
        elif snapshot is None:
            print(f"Snapshot is none. {company_id} isn't in the system")
            break
        elif snapshot['url'] in already_crawled:
            # TODO: Clean this up
            snap_t = snapshot['timestamp']
            snap_t = datetime.datetime.strptime(snap_t, "%Y%m%d%H%M%S")
            print(
                f"Already crawled. Current date is {cur_date} and snapshot date is {snap_t}")
            cur_date += relativedelta(months=6)
            continue

        print(f"{company_id}: {cur_date.month}/{cur_date.year}")

        time.sleep(.25)

    finished_cos.append(company_id)
    print("Finished:", finished_cos)

print("Creating final log report")
# Create DataFrame from the dictionary
df = pd.DataFrame.from_dict(log_report, orient='index')
# Explode the list values into separate columns
df_expanded = df.apply(lambda x: pd.Series(
    x), axis=1).stack().reset_index(level=1, drop=True)

# Split the exploded values into separate columns
df_final = pd.DataFrame(
    df_expanded.values.tolist(), index=df_expanded.index)
df_final.columns = ['month', 'timestamp', 'entityid',
                    'input_url', 'wayback_url', 'failed', 'fail_reason', 'output_path']

# Export DataFrame to CSV
df_final.to_csv(LOG_REPORT, index_label='Year')
print("Exported log report")
