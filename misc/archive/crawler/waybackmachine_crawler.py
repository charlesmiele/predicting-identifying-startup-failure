import data_reader
import codecs
import re
import requests
import time
import datetime
import pdb
import os
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath('../download'))


class waybackmachine_crawler:
    def __init__(self, website, company_id, output_folder="out", year_folder=False):
        print("Looking at new website {0}...".format(website))
        self.website = website
        self.company_id = company_id
        self.output_folder = output_folder
        self.year_folder = year_folder

    def split_wayback_url(self, wayback_url):
        original_url = re.sub(
            r'http://web.archive.org/web/\d+/', "", wayback_url)
        website_piece = re.sub(r"http(s?)\://", "", original_url)

        try:
            (domain, address) = website_piece.split("/", 1)
        except ValueError:
            domain = website_piece
            address = ""

        domain = data_reader.clean_domain_url(domain)

        return (domain, address)

    def store_page(self, wayback_url, html):
        (domain, address) = self.split_wayback_url(wayback_url)

        if self.year_folder:
            base_directory = "{0}/{1}/{2}/{3}".format(
                self.output_folder, self.company_id, self.crawled_year, self.crawled_month)
        else:
            base_directory = self.output_folder + "/" + self.company_id

        if not os.path.exists(base_directory):
            os.makedirs(base_directory)

        # Used to be "homepage.html"
        if address == "":
            address = "index.html"

        if address[-5:] != ".html":
            address += ".html"

        file_path = base_directory + "/" + address.replace("/", "_")
        outfile = codecs.open(file_path, "w", 'utf-8')
        outfile.write(html)
        outfile.close()
        # print("\t .Stored in: {0}".format(file_path))
        return file_path

    def is_valid_url(self, url):
        if url.endswith('.pdf') or ("godaddy" in url) or ("bobparsons" in url):
            return False

        if url == "." or url == "..":
            return False

        return True

    def crawl(self, wayback_url, timestamp, levels=1):
        # Recursive algorithm
        # print("\t .Crawl [L={0}].. {1}".format(levels, wayback_url))

        clean_url = re.sub("\?.*", "", wayback_url)
        clean_url = re.sub(r"\#.*", "", clean_url)

        # TODO: Add more text failure conditions

        try:
            response = requests.get(clean_url)
            html = response.text
            # Store_page stores the html, but it also returns the filepath
            # which we will add to the descriptor in done_urls
            file_path = self.store_page(clean_url, html)
            done_urls = self.add_done_url(
                clean_url, 0, done_urls, timestamp, fp=file_path)
            return True
        except ConnectionError as e:
            # Be careful with this...how do we know for sure...
            # log
            print("Connection Error: Skipping")
            return False

    # Notes: If no year.. then stored under key value 0

    def add_done_url(self, wayback_url, isFailed, done_urls, timestamp, fail_reason="", fp="", ):

        if self.year_folder is True and self.crawled_year not in done_urls:
            done_urls[self.crawled_year] = []

        elif self.year_folder is False and done_urls == {}:
            done_urls[0] = []

        ix = self.crawled_year if self.year_folder is True else 0

        done_urls[ix].append(
            [self.crawled_month, timestamp, self.company_id,
                self.website, wayback_url, isFailed, fail_reason, fp]
        )

        return done_urls

    def url_done(self, url, done_urls):
        ix = self.crawled_year if self.year_folder is True else 0

        if url in done_urls.get(ix, {}):
            return True

        if url.replace("www.", "") in done_urls.get(ix, {}):
            return True

        return False

    def crawl_from_date(self, year, month, day):
        # We want the distance to be disciplined
        # Don't look more than one year from either side
        snapshot = self.list_closest_snapshot(year, month, day)
        self.crawled_year = year

        if snapshot is not None:
            return self.crawl(snapshot['url'])

    def is_valid_url(self, url):
        if "mailto" in url:
            return False

        if len(url) > 200:
            return False

        return True

    def list_closest_snapshot(self, year, month, day):
        timestamp = datetime.date(
            year=year, month=month, day=day).strftime("%Y%m%d")
        # print("\t .Getting snapshots.  Timestamp = {0}".format(timestamp))
        url = "http://archive.org/wayback/available?url={0}&timestamp={1}".format(
            self.website, timestamp)

        response = requests.get(url)
        snapshots = response.json()["archived_snapshots"]

        if len(snapshots) > 0:
            return snapshots["closest"]
        else:
            return None
