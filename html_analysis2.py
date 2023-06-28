# This is the second analysis, where we wrangle
# the dataset provided by html_analysis.py some more.

# PART 2

import pandas as pd
import pdb

df = pd.read_csv('data/revised_webpage_metadata.csv')

# --DATE BASED---
df["founded_yr"] = df["startdate"].str.slice(start=0, stop=4)
df["founded_yr"] = df["founded_yr"].fillna(
    df["lastVC"].str.slice(start=0, stop=4))
df["real_exit"] = df["exit_date"].isna() == False
df["end_yr"] = df["exit_date"].str.slice(start=0, stop=4)
df["end_yr"] = df["end_yr"].fillna(2023)
df["end_yr"] = df["end_yr"].astype(int)
df["life_span_yrs"] = df["end_yr"] - df["founded_yr"]
# Has the company been around for 5+ years?
# Has the company been around for 10+ years?
# Does the company have a “real” exit, or did we just put it as June 2023?
# One interesting observation is that 78% of the companies in our original dataset
# of 78K companies have no exit date. With my current "sample" of HTML files, this
# number is much higher (around 90%).
# Was the first timestamp taken within 2 years of the founding date?

# ---ANALYSIS Qs---
# How old are companies when we first see their website?
# What's the average number of links throughout the company's life-span?
