import pandas as pd
import os
from bs4 import BeautifulSoup
import pdb
import numpy as np


# Read environment variables
i = int(os.getenv('SGE_TASK_ID'))
range_i = int(os.getenv('SGE_TASK_LAST')) - \
    int(os.getenv('SGE_TASK_FIRST')) + 1

OUTPUT_PATH = f"data/analysis-3/{i}_revised_webpage_metadata.csv"


# Read data
url_list = pd.read_csv('data/startup_url_list.csv')
timestamp_list = [f for f in os.listdir(
    'data/optimal-timestamps') if not f.startswith('.')]
timestamp_list = [int(file[:-15]) for file in timestamp_list]

already_finished_crude = [int(f) for f in os.listdir(
    'data/html') if not f.startswith('.')]
url_list = url_list[(url_list.entityid.isin(timestamp_list)) & (
    url_list.entityid.isin(already_finished_crude) == True)]
url_list['missing_startdate'] = url_list['startdate'].isna()
url_list['startdate'] = url_list['startdate'].fillna(url_list['lastVC'])
url_list['startyear'] = url_list.startdate.str.slice(
    start=0, stop=4)
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


# Create empty dataframe
columns = [
    'entityid',
    'yr_from_start',
    'capture_yr',
    'capture_m',
    'file_path',
    'file_exists',
    'website_size_kb',

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

    'p_count',
    'h_count',
    'img_count',
    'a_count',
    'table_count',
    'form_count',
    'script_count',
]
webpage_metadata = pd.DataFrame(columns=columns)

# These are used later in add_big()
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

# Used in identifying "empty" HTML pages
errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"


def add_big(soup, data):
    global section_indicators

    remaining_section_indicators = section_indicators.copy()

    # Fill in any indicators
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        href = a_tag.get('href')
        text = a_tag.text.strip(' */,.?!')
        for s in list(remaining_section_indicators):
            if text.lower() in remaining_section_indicators[s]:
                data[s] = 1
                del remaining_section_indicators[s]

    return data


def small_qualitative(soup, data):
    # title
    title = soup.find('title')
    description = soup.find('meta', attrs={'name': 'description'})
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    data['title'] = int(title != None)
    data['description'] = int(description != None)
    data['keywords'] = int(keywords != None)
    # TODO: Not including for now...Only doing quantitative variables
    '''
    author = soup.find('meta', attrs={'name': 'author'})
    html_tag = soup.find('html')
    if title:
        try:
            data['title'] = title.string
        except KeyError:
            data['title'] = None
    # meta description
    if description:
        try:
            data['description'] = description['content']
        except KeyError:
            data['description'] = None
    # meta keywords
    if keywords:
        try:
            data['keywords'] = keywords['content']
        except KeyError:
            data['keywords'] = None
    # author
    if author:
        try:
            data['author'] = author['content']
        except KeyError:
            data['author'] = None
    # language
    if html_tag:
        try:
            data['language'] = html_tag.get('lang')
        except KeyError:
            data['language'] = None
    '''
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


def get_htmls(company, base_path):
    # A HTML page is a "success" if all of these get filled out with some value...
    data = {
        'entityid': str(company['entityid']),
        'yr_from_start': "",
        'capture_yr': None,
        'capture_m': None,
        'file_path': "",
        'file_exists': 1,

        'website_size_kb': 0,

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

        'title': 0,
        'description': 0,
        'keywords': 0,

        'p_count': 0,
        'h_count': 0,
        'img_count': 0,
        'a_count': 0,
        'table_count': 0,
        'form_count': 0,
        'script_count': 0,
    }
    global webpage_metadata

    # Needed to calculate the year from start
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
                # Get time from start date (in years)
                yr_from_start = (int(year) - start_date.year) + \
                    ((int(month) - start_date.month) / 12)
                # Round to nearest half-year
                data['yr_from_start'] = round(yr_from_start * 2) / 2

                # Get file size (kb)
                data['website_size_kb'] = os.stat(
                    index_path).st_size / 1024

                # Open the file, parse HTML
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        # This is an error where BeautifulSoup is unable to parse the HTML
                        continue
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        # If the HTML text is an error text
                        continue

                    # Parse HTML, produce more variables
                    data = add_big(soup, data)
                    data = small_qualitative(soup, data)
                    data = small_quant(soup, data)
            else:
                # File doesn't exist
                continue
            # Append data
            webpage_metadata = webpage_metadata.append(data, ignore_index=True)

            webpage_metadata.to_csv(OUTPUT_PATH, index=False)


base_path = "data/html"


for index, row in url_list.iterrows():
    get_htmls(row, base_path)
    print(row.entityid)


webpage_metadata = webpage_metadata.sort_values(
    by=['entityid', 'yr_from_start'])

webpage_metadata.to_csv(OUTPUT_PATH, index=False)
