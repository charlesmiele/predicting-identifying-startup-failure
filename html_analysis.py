import pandas as pd
import os
from bs4 import BeautifulSoup

errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"

# Read data
url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = os.listdir('data/optimal-timestamps')
timestamp_list = [int(file[:-15]) for file in timestamp_list]
faulty_htmls = pd.read_csv('data/missing_429s.csv')
faulty_htmls = faulty_htmls[faulty_htmls.error == 0.0]['filepath']
already_finished_crude = [int(f) for f in os.listdir(
    'data/html') if not f.startswith('.')]
url_list = url_list[(url_list.entityid.isin(timestamp_list)) & (
    url_list.entityid.isin(already_finished_crude) == True)]
url_list['startyear'] = url_list.startdate.str.slice(
    start=0, stop=4)
url_list['startyear'] = url_list['startyear'].fillna(
    url_list['lastVC'].str.slice(start=0, stop=4))
url_list['startyear'] = url_list['startyear'].astype('int16')
url_list = url_list.sort_values('startyear')

# Create empty df
columns = [
    'entityid',
    'capture_yr',
    'capture_m',
    'file_path',
    'file_exists',
    'is_429',
    'website_size_kb',
    'text_array',
    'a_dict',
    'title',
    'description',
    'keywords',
    'author',
    'language',
    'p_count',
    'h_count',
    'img_count',
    'a_count',
    'table_count',
    'form_count',
    'script_count',
    'embedded_js',
    'external_js'
]
webpage_metadata = pd.DataFrame(columns=columns)


def add_big(soup, data):
    # General text array
    text_array = [text for text in soup.stripped_strings]
    data['text_array'] = text_array

    # <a> dictionary
    a_dict = {}
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        href = a_tag.get('href')
        text = a_tag.text.strip()
        a_dict[href] = text

    data['a_dict'] = a_dict
    return data


def small_qualitative(soup, data):
    # title
    title = soup.find('title')
    data['title'] = title.string if title else None
    # meta description
    description = soup.find('meta', attrs={'name': 'description'})
    data['description'] = description['content'] if description else None
    # meta keywords
    keywords = soup.find('meta', attrs={'name': 'description'})
    data['keywords'] = keywords['content'] if keywords else None
    # author
    author = soup.find('meta', attrs={'name': 'author'})
    data['author'] = author['content'] if author else None
    # language
    html_tag = soup.find('html')
    data['language'] = html_tag.get('lang') if html_tag else None
    return data


def small_quant(soup, data):
    x = {
        'p_count': ['p'],
        'h_count': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        'img_count': ['img'],
        'a_count': ['a'],
        'table_count': ['table'],
        'form_count': ['form'],
        'script_count': ['script'],
    }
    for i in x:
        count = 0
        for y in x[i]:
            count += len(soup.find_all(y))
        data[i] = count

    return data


def misc_boolean(soup, data):
    script_tags = soup.find_all('script')

    # TODO: This is inefficient...
    for script in script_tags:
        src = script.get('src')
        if src:
            data['embedded_js'] = True
        else:
            data['external_js'] = True

    return data


def get_htmls(company, base_path):
    data = {
        'entityid': str(company['entityid']),
        'capture_yr': None,
        'capture_m': None,
        'file_path': None,
        'file_exists': True,
        'is_429': False,

        'website_size_kb': None,
        'text_array': None,
        'a_dict': None,

        'title': None,
        'description': None,
        'keywords': None,
        'author': None,
        'language': None,

        'p_count': None,
        'h_count': None,
        'img_count': None,
        'a_count': None,
        'table_count': None,
        'form_count': None,
        'script_count': None,

        'embedded_js': None,
        'external_js': None
    }
    global webpage_metadata

    start_date = pd.to_datetime(company['startdate'])

    co_directory = os.path.join(base_path, data['entityid'])

    years = [f for f in os.listdir(co_directory) if not f.startswith('.')]
    for year in years:
        data['capture_yr'] = int(year)
        yr_directory = os.path.join(co_directory, year)
        for month in os.listdir(yr_directory):
            data['capture_m'] = int(month)
            index_path = os.path.join(yr_directory, month, "index.html")
            if os.path.isfile(index_path):
                data['file_path'] = index_path
                # Get time from start date (in months)
                data['time_from_start_m'] = 12 * \
                    (int(year) - start_date.year) + \
                    (int(month) - start_date.month)
                # Get file size (kb)
                data['website_size_kb'] = os.stat(
                    index_path).st_size / 1024

                # Finally open the file
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        data['is_429'] = True
                        continue

                    # Parse HTML, produce more variables
                    data = add_big(soup, data)
                    data = small_qualitative(soup, data)
                    data = small_quant(soup, data)
                    data = misc_boolean(soup, data)
            else:
                data['file_exists'] = False
            webpage_metadata = webpage_metadata.append(
                data, ignore_index=True)
            print("Analyzed", data['file_path'])


base_path = "data/html"


for index, row in url_list.iterrows():
    get_htmls(row, base_path)
    print(row.entityid)


webpage_metadata = webpage_metadata.sort_values(
    by=['entityid', 'capture_yr', 'capture_m'])

# FINAL STEP!
# TODO: Fix this bug
# webpage_metadata = pd.merge(webpage_metadata, url_list, on='entityid')

# TODO: THIS FILE PATH IS TEMPORARY
webpage_metadata.to_csv('data/revised_webpage_metadata.csv', index=False)
