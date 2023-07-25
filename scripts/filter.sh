#!/bin/bash

for x in {1..20}
do
    anapy3 --grid_submit=batch filter_download_html.py $x
done