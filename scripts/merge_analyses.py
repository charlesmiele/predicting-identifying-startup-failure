import pandas as pd
import os
import pdb

columns = ['entityid',
           'capture_yr',
           'capture_m',
           'file_path',
           'file_exists',
           'is_429',
           'is_parsable',
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
           'external_js']

df = pd.read_csv('../data/1_revised_webpage_metadata.csv',
                 usecols=[i for i in columns])
for i in range(2, 401):
    try:
        dfi = pd.read_csv(
            f"../data/{i}_revised_webpage_metadata.csv", usecols=[i for i in columns])
        df = pd.concat([df, dfi], ignore_index=True)
        print(i, "has been concated")
        print(df['entityid'].nunique(), "companies")
        print(len(df.index), "rows")
        print("---")
    except pd.errors.EmptyDataError:
        print(i, "is empty.")
df.to_csv('../data/2_final_webpage_metadata.csv')
