import pandas as pd
import os
from bs4 import BeautifulSoup
import pdb
import numpy as np


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
url_list = url_list.sample(100)

# Calculate given interval
num_urls = len(url_list.index)

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


def add_big(soup):
    global section_indicators
    remaining_section_indicators = section_indicators.copy()
    # <a> dictionary
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        text = a_tag.text.strip(' */,.?!')
        if text == "":
            continue
        for s in list(remaining_section_indicators):
            if text.lower() in remaining_section_indicators[s]:
                print(text.lower(), "is in", remaining_section_indicators[s])
                del remaining_section_indicators[s]


def get_htmls(company, base_path):
    print("On company", company.entityid)

    # A HTML page is a "success" if all of these get filled out with some value...

    co_directory = os.path.join(base_path, str(company.entityid))

    years = [f for f in os.listdir(co_directory) if not f.startswith('.')]
    for year in years:

        yr_directory = os.path.join(co_directory, year)
        for month in os.listdir(yr_directory):
            index_path = os.path.join(yr_directory, month, "index.html")
            if os.path.isfile(index_path):
                # (Finally) open the file
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        print("Encountered bug")
                        continue
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        print("Encountered bug")
                        continue

                    # Parse HTML, produce more variables
                    # TODO: This is getting commented out for now...come up with a solution later.
                    add_big(soup)


base_path = "data/html"


for index, row in url_list.iterrows():
    get_htmls(row, base_path)
    print(row.entityid)
