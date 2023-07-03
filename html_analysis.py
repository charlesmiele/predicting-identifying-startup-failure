import pandas as pd
import os
from bs4 import BeautifulSoup
import pdb
import numpy as np


# Read environment variables
i = int(os.getenv('SGE_TASK_ID'))
range_i = int(os.getenv('SGE_TASK_LAST')) - \
    int(os.getenv('SGE_TASK_FIRST')) + 1

OUTPUT_PATH = f"data/{i}_revised_webpage_metadata.csv"

# Read data
url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = os.listdir('data/optimal-timestamps')
timestamp_list = [int(file[:-15]) for file in timestamp_list]

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

# Only select companies founded after 1996
url_list = url_list[url_list['startyear'] >= 1996]
# Calculate given interval
num_urls = len(url_list.index)
intervals = np.linspace(0, num_urls, range_i + 1)
intervals = intervals.astype(int).tolist()
start = intervals[i - 1]
finish = intervals[i]
url_list = url_list.iloc[start:finish]
print("Scraping indicies", start, "to", finish)

# Create empty df
columns = [
    'entityid',
    'capture_yr',
    'capture_m',
    'file_path',
    'file_exists',
    'is_429',
    'is_parsable',
    'website_size_kb',
    'text_array',
    'a_dict',
    'careers',
    'blog',
    'login',
    'contact',
    'team',
    'about',
    'news',
    'faq',
    'call_to_action',
    'testimonial',
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

# These are used later
section_indicators = {
    'careers': ["job", "jobs", "career", "careers", "join our team", "join us", "employment opportunities", "career opportunities"],
    'blog': ["blog", "our blog", "latest articles", "blog posts", "news and updates", "insights", "insights and opinions"],
    'login': ["login", "log in", "forgot password", "sign in ", "signin", "member login"],
    'contact': ["contact", "contact us", "get in touch", "reah out", "contact information"],
    'team': ["team", "our team", "meet the team", "team members", "our staff"],
    'about': ["about us", "about", "our story", "about our company", "mission and vision"],
    'news': ["news", "stories", "in the press", "press", "press releases", "media coverage", "company updates"],
    'faq': ["faq", "frequently asked questions", "questions", "help and support", "common queries", "common questions"],
    'call_to_action': ["sign up today", "sign up", "join", "request a demo", "download", "try for free", "learn more", "get started"],
    'testimonial': ["testimonials", "what people say", "what our clients say", "client testimonials", "customer reviews", "reviews", "success stories"]
}
errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"


def add_big(soup, data):
    # General text array
    # TODO: Removing this for now because it takes up too much space...
    text_array = [text for text in soup.stripped_strings]
    data['text_array'] = text_array
    remaining_section_indicators = section_indicators

    # <a> dictionary
    a_dict = {}
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        href = a_tag.get('href')
        text = a_tag.text.strip(' */,.?!')
        for s in list(remaining_section_indicators):
            if text.lower() in remaining_section_indicators[s]:
                data[s] = 1
                del remaining_section_indicators[s]
        a_dict[href] = text

    data['a_dict'] = a_dict
    return data


def small_qualitative(soup, data):
    # title
    title = soup.find('title')
    if title:
        try:
            data['title'] = title.string
        except KeyError:
            data['title'] = None
    # meta description
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        try:
            data['description'] = description['content']
        except KeyError:
            data['description'] = None
    # meta keywords
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords:
        try:
            data['keywords'] = keywords['content']
        except KeyError:
            data['keywords'] = None
    # author
    author = soup.find('meta', attrs={'name': 'author'})
    if author:
        try:
            data['author'] = author['content']
        except KeyError:
            data['author'] = None
    # language
    html_tag = soup.find('html')
    if html_tag:
        try:
            data['language'] = html_tag.get('lang')
        except KeyError:
            data['language'] = None
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
    # A HTML page is a "success" if all of these get filled out with some value...
    data = {
        'entityid': str(company['entityid']),
        'capture_yr': None,
        'capture_m': None,
        'file_path': "",
        'file_exists': 1,
        'is_429': 0,
        'is_parsable': 1,

        'website_size_kb': 0,
        'text_array': None,
        'a_dict': None,

        'careers': 0,
        'blog': 0,
        'login': 0,
        'contact': 0,
        'team': 0,
        'about': 0,
        'news': 0,
        'faq': 0,
        'call_to_action': 0,
        'testimonial': 0,

        'title': "",
        'description': "",
        'keywords': "",
        'author': "",
        'language': "",

        'p_count': 0,
        'h_count': 0,
        'img_count': 0,
        'a_count': 0,
        'table_count': 0,
        'form_count': 0,
        'script_count': 0,

        'embedded_js': 0,
        'external_js': 0
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

                # (Finally) open the file
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        data['is_parsable'] = 0
                        continue
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        data['is_429'] = 1
                        continue

                    # Parse HTML, produce more variables
                    # TODO: This is getting commented out for now...come up with a solution later.
                    data = add_big(soup, data)
                    data = small_qualitative(soup, data)
                    data = small_quant(soup, data)
                    data = misc_boolean(soup, data)
            else:
                data['file_exists'] = 0
            # Append data
            webpage_metadata = webpage_metadata.append(data, ignore_index=True)

            webpage_metadata.to_csv(OUTPUT_PATH, index=False)


base_path = "data/html"


for index, row in url_list.iterrows():
    get_htmls(row, base_path)
    print(row.entityid)


webpage_metadata = webpage_metadata.sort_values(
    by=['entityid', 'capture_yr', 'capture_m'])

# FINAL STEP
# TODO: Fix this bug
# webpage_metadata = pd.merge(webpage_metadata, url_list, on='entityid')

webpage_metadata.to_csv(OUTPUT_PATH, index=False)
