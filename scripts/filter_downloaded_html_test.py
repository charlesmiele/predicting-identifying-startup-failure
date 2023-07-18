import os
import pdb
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def main():
    errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"

    # TODO: Skipping this for now...this is harder than expected
    # js_words = ['Date();', 's.createElement(o),', 's);', "_paq.push(['setTrackerUrl',",
    #             '})(window,', "'auto');", "'UA-36441709-1',", '(i[r].q', 's.getElementsByTagName(o)[0];',
    #             'i[r].l', '(function', "_paq.push(['enableLinkTracking']);", 'a.src', "'pageview');",
    #             '()', 's.parentNode.insertBefore(g,', 'm.parentNode.insertBefore(a,',
    #             "'ga');", "'piwik.js';", 'a.async', "ga('create',", 'g.src', 'r;', '[]).push(arguments)',
    #             '_paq', 'i[r].q', 'const', "_paq.push(['setSiteId',", '1]);',
    #             "i['GoogleAnalyticsObject']", 'g.type', "d.getElementsByTagName('script')[0];", "'text/javascript';",
    #             'g.defer', '})();', "_paq.push(['trackPageView']);", "ga('send',", "'piwik.php']);",
    #             "d.createElement('script'),", "'script',", 'g;', 'g.async', 'i[r]']

    co_list = [f for f in os.listdir(
        '../data/SubsetHTML') if not f.startswith('.')]

    missed_timestamps = pd.DataFrame(
        columns=['entityid', 'timestamp', 'notes'])

    for company in co_list:
        print(company)

        # TODO: Fix
        timestamps = pd.read_csv(
            f"../data/SubsetTimestamps/{company}_timestamps.csv")
        timestamps = timestamps['timestamp'].astype(str).values.tolist()
        years = [t[:4] for t in timestamps]
        months = [t[4:6] for t in timestamps]

        for time in range(len(timestamps)):
            # TODO: Fix
            index_path = os.path.join(
                f"../data/SubsetHTML/{company}/{years[time]}/{months[time]}/index.html")
            data = {
                'entityid': company,
                'timestamp': timestamps[time],
                'notes': ""
            }
            # Open file
            if os.path.isfile(index_path):
                with open(index_path, 'r') as file:
                    # Read file
                    html_content = file.read()
                    file_size = int(os.stat(index_path).st_size / 1024)
                    # Empty file
                    if file_size == 0:
                        data['notes'] = 'emptyFile'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # Try to parse
                    try:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    except UnboundLocalError:
                        data['notes'] = 'unparsable'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    body_tag = soup.body
                    if body_tag:
                        num_inside_body = len(body_tag.find_all())
                        # Not a lot of elements in the webpage (suspect)
                        if num_inside_body < 3:
                            data['notes'] = 'SmallBody'
                            missed_timestamps = missed_timestamps.append(
                                data, ignore_index=True)
                            continue
                    else:
                        # No body tag
                        data['notes'] = 'NoBody'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    soup_str = soup.get_text()
                    # 429 Text
                    if soup_str == errortxt_429:
                        data['notes'] = '429Error'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # Includes JavaScript in the visible text (suspect)
                    txt_list = soup_str.strip().split()
                    js_list = [i for i in txt_list if i in js_words]
                    if js_list != []:
                        data['notes'] = js_list
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
                    # It's good now
                    data['notes'] = 'Good'
                    missed_timestamps = missed_timestamps.append(
                        data, ignore_index=True)
            else:
                # Couldn't find the file
                data['notes'] = 'MissingFile'
                missed_timestamps = missed_timestamps.append(
                    data, ignore_index=True)

    # 4. How many companies have we downloaded partially?
    missed_timestamps.to_csv(f"missed_timestamps_sample.csv", index=False)


if __name__ == "__main__":
    main()
