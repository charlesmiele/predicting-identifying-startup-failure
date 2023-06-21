import pandas as pd
import os
from bs4 import BeautifulSoup
import pprint as pp

# Read in data
url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = os.listdir('data/optimal-timestamps')
timestamp_list = [int(file[:-15]) for file in timestamp_list]

# Only select companies that are already finished
# (This list is hardcoded for now to prevent any bugs)
already_finished_crude = [int(f) for f in os.listdir(
    'data/html') if not f.startswith('.')]
url_list = url_list[(url_list.entityid.isin(timestamp_list)) & (
    url_list.entityid.isin(already_finished_crude) == True)]

# Select founding year
url_list['startyear'] = url_list.startdate.str.slice(start=0, stop=4)
# Which years have a lot of companies?
url_list['startyear'].value_counts()

# Filter on popular founding year


# Create empty df
columns = ['entityid', 'domain', 'capture_yr', 'capture_m', 'time_from_start_m',
           'website_size_kb', 'title', 'num_a_tags', 'a_innertext', 'meta_description', 'meta_keywords']
webpage_metadata = pd.DataFrame(columns=columns)

# Master function
# TODO: Split this up into seperate sub-functions


def get_htmls(company, base_path):
    global webpage_metadata
    entityid = company['entityid']
    domain = company['weburl']
    start_date = pd.to_datetime(company['startdate'])
    htmls = []
    co_directory = os.path.join(base_path, entityid)
    years = [f for f in os.listdir(co_directory) if not f.startswith('.')]
    for year in years:
        yr_directory = os.path.join(co_directory, year)
        for month in os.listdir(yr_directory):
            index_path = os.path.join(yr_directory, month, "index.html")
            if os.path.isfile(index_path):
                # Get time from start date (in months)
                time_from_start_m = 12 * \
                    (year - start_date.year) + (month - start_date.month)
                # Get file size (kb)
                website_size_kb = os.stat(index_path).st_size / 1024
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    # Call a bunch of functions that give this more data
                    a_tags = soup.find_all('a')
                    num_a_tags = len(a_tags)
                    a_inner_texts = []
                    for a_tag in a_tags:
                        at_txt = str(a_tag.text)
                        at_txt = at_txt.replace("\n", "")
                        if at_txt != "":
                            a_inner_texts.append(at_txt)
                    page_title = soup.title.text
                    htmls.append(soup)
                    has_meta_description_tag = (
                        soup.find('meta', attrs={'name': 'description'}) is not None)
                    has_meta_keywords_tag = (
                        soup.find('meta', attrs={'name': 'keywords'}) is not None)
                    data_to_add = {
                        'entityid': entityid,
                        'domain': domain,
                        'capture_yr': year,
                        'capture_m': month,
                        'time_from_start_m': time_from_start_m,
                        'website_size_kb': website_size_kb,
                        'title': page_title,
                        'num_a_tags': num_a_tags,
                        'a_innertext': a_inner_texts,
                        'meta_description': int(has_meta_description_tag),
                        'meta_keywords': int(has_meta_keywords_tag)
                    }
                    print("Adding:", pp.pprint(data_to_add))
                    webpage_metadata = webpage_metadata.append(
                        data_to_add, ignore_index=True)


base_path = "data/html"
companies = url_list.entityid.astype(str)

for index, row in url_list.iterrows():
    get_htmls(row, base_path)
