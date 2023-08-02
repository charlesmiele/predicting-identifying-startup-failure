# Identifying and predicting startup failure

This project uses historical website data from the IA (Internet Archive) to predict if and when a startup failed.

There are four functions of this directory:

1. Collect data
2. Store data
3. Process data
4. Analyze data.

## 1. Data Collection & Storage

We start with a list of 78,000 companies from the "input file", `data/startup_url_list.csv`. This is a private commercial VC data set. The input file contains unique IDs for each company, which is used all throughout the project, and a website link for each company. There are additional columns used later in the project.

Next, we iterate through each company and use an IA API endpoint to download a JSON file. Each JSON contains a list of timestamps corresponding to _all_ the captures the IA got for that domain. **They can be found at `data/raw-json`.** We later filter each file to have only contain timestamps with HTTP status code 200. (The JSONs also contain more columns that we haven't used yet.)

- I created a simpler version that merges all of the JSONs for each company into one CSV file with only HTTP-200 screenshots and the entityID, which you can find as `data/simple_json.csv`. This makes it easier to run regressions with the timestsamp data, which may be useful down the road (we can talk about this more in-depth later).

It would be too much to download every IA snapshot for every company, so we decided to limit ourselves to: for each company, download one screenshot every 6 months between its start date and exit date (if it has no exit date, we did it up until 2023).

`scripts/get_optimal_timestamps.py` takes in the company's JSONs and exports a corresponding CSV containing the most optimal set of timestamps to download. Those CSVs can be found in `data/optimal-timestamps`.

- It would have been a better idea to just merge these CSVs into one file since they're all quite small. We could easily do this, we'll just have to make corresponding adjustments to the download script.

---

Finally, at this point we're ready to download the HTML files. `html_download.py` iterates through each optimal timestamp file and makes a GET request to an internet archive link of that company's snapshot. We then download the file and store it in `data/html`.

- **Our current method of file organization / storage is problematic for the research GRID because it creates an excessive amount of directories. We have about 850K HTML files, but the GRID counts directories as files, so it says HTML folder contains over 2 million files, which is above our limit.**

  - **The plan moving forward is to embed the meta-information about the snapshot into the filename. For instance, instead of storing a snapshot like `data/html/{entityid}/{year}/{month}/index.html`, we'd have it be like `data/html/{entityid}_{year}_{month}.html` (and then use `.split('_')` to find all the relevant information.)**

_(Downloading the JSONs and HTMLs took a long time (10-30+ hours), so I parrallel-ized it to speed things up. You can't split it too much or else the IA server would time us out. I kept it to 3-5.)_

## 2. Data processing

In order to make our job easier for analyzing these HTML files, we parse each file, effectively making each snapshot a row in one big CSV file which we call the "analysis file". The "analysis file" is created with `html_analysis.py`. It parses every file using the BeautifulSoup library. (Whenever I run this, I also parallel-ize it in the GRID.)

Take a look at `data/07_27_analysis.csv`, that's the "current state" of our analysis file. _Just to be clear, this is the output of html_analysis.py._

Okay, here's where it gets more confusing. (I plan on re-organizing this so its easier to use in the future.) I run `data/07_27_analysis.csv` through one last script, `analysis/07_27_merge_add_cols.ipynb`. This joins the output of `html_analysis.py` with the output from (1) `scripts/filter_html_downloads.py`, which identifies any files that weren't downloaded properly, and (2) the input file (`startup_url_list.csv`).

The working result is `07_28_merged_analysis.csv`. This is a panel data set, with each entityID containing multiple observations, and then 40+ dependent variables to use for regressions (some are entity-fixed (which are given by the input file), others are unique to each snapshot).

This might help make things simpler:

- html_analysis.py
  - In: HTML files
  - Out: 07_27_analysis.csv (AKA the "analysis file")
- scripts/filter_html_download.py
  - In: HTML files, optimal_timestamp list
  - Out: HTMLReport.csv (contains "red flags" about HTML files)
- analysis/07_27_merge_add_cols.ipynb
  - In: 07_27_analysis.csv, HTMLReport.csv, startup_url_list
  - Out: 07_28_merged_analysis.csv (AKA the "final analysis file")

Some important notes on the "final analysis file":

- There are 63,000 unique companies in this data set. Why not 78,000? (1) We couldn't get HTML from some companies, and (2) we're only looking at companies founded after 1996.

- `notes` tells us if a screenshot is unusable for the regressions. I suspect the main reason this occurs is that we downloaded files using a GET request, which doesn't allow sites using JS frameworks to "entirely" load. **This is definitely a problem for our more recent snapshots since these frameworks are becoming more and more common. One potential (albeit slow) workaround is to use a library like Selenium to load the website, wait some time, and then download.**

- `exit_date` is missing for 80% of our companies (>90% of failed companies). This can be problematic for the regressions that make models predicting _time_ of failure. Our current workaround is create an `end_yr` 2 years after the company's last VC funding (this only applies to failed companies, of course).

- **The dependent variables for our snapshots are always subject to change.** Feel free to add another column if you think it could be a signal! But I advise that you look through the analysis script to see the nuts and bolts for how these columns are calculated.

## 3. Data Analysis
