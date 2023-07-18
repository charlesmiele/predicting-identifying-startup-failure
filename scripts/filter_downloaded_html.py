import os
import pdb
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def main():
    errortxt_429 = "429 Too Many Requests\nYou have sent too many requests in a given amount of time.\n\n"

    # TODO: Skipping this for now...this is harder than expected
    '''
    js_words = {'Date();', 's.createElement(o),', 's);', "_paq.push(['setTrackerUrl',", '{', '[];',
                '})(window,', "'auto');", "'UA-36441709-1',", 'var', '(i[r].q', 's.getElementsByTagName(o)[0];',
                'i[r].l', '(function', "_paq.push(['enableLinkTracking']);", '},', 'a.src', "'pageview');",
                'd', '()', 'a', 's.parentNode.insertBefore(g,', '=', 'm.parentNode.insertBefore(a,', 'document,',
                "'ga');", "'piwik.js';", 'a.async', "ga('create',", 'g.src', 'r;', '[]).push(arguments)',
                '_paq', 'm)', 's', '||', 'i[r].q', 'const', "_paq.push(['setSiteId',", '1]);',
                "i['GoogleAnalyticsObject']", 'g.type', "d.getElementsByTagName('script')[0];", "'text/javascript';",
                'g.defer', '})();', '1', "_paq.push(['trackPageView']);", "ga('send',", 'u', "'piwik.php']);",
                '+', "d.createElement('script'),", "'script',", 'g;', 'g.async', 'i[r]'
                }
    '''

    i = int(os.getenv('SGE_TASK_ID'))
    range_i = int(os.getenv('SGE_TASK_LAST')) - \
        int(os.getenv('SGE_TASK_FIRST')) + 1

    co_list = [f for f in os.listdir(
        '../data/html') if not f.startswith('.')]

    # Create interval
    intervals = np.linspace(0, len(co_list), range_i + 1)
    intervals = intervals.astype(int).tolist()
    start = intervals[i - 1]
    finish = intervals[i]
    co_list = co_list[start:finish]

    missed_timestamps = pd.DataFrame(
        columns=['entityid', 'timestamp', 'notes'])

    for company in co_list:
        if co_list.index(company) % 100 == 0:
            print(co_list.index(company))

        timestamps = pd.read_csv(
            f"../data/optimal-timestamps/{company}_timestamps.csv")
        timestamps = timestamps['timestamp'].astype(str).values.tolist()
        years = [t[:4] for t in timestamps]
        months = [t[4:6] for t in timestamps]

        company_directory = f"../data/html/{company}"

        for time in range(len(timestamps)):
            index_path = os.path.join(
                company_directory, f"{years[time]}/{months[time]}/index.html")
            data = {
                'entityid': company,
                'timestamp': timestamps[time],
                'notes': ""
            }
            if os.path.isfile(index_path):
                with open(index_path, 'r') as file:
                    html_content = file.read()
                    file_size = int(os.stat(index_path).st_size / 1024)
                    if file_size == 0:
                        data['notes'] = 'emptyFile'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
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
                        if num_inside_body < 5:
                            data['notes'] = 'SmallBody'
                            missed_timestamps = missed_timestamps.append(
                                data, ignore_index=True)
                            continue
                    soup_str = soup.get_text()
                    if soup_str == errortxt_429:
                        data['notes'] = '429Error'
                        missed_timestamps = missed_timestamps.append(
                            data, ignore_index=True)
                        continue
            else:
                data['notes'] = 'MissingFile'
            missed_timestamps = missed_timestamps.append(
                data, ignore_index=True)

    # 4. How many companies have we downloaded partially?
    missed_timestamps.to_csv(f"/missed-timestamps/{i}.csv", index=False)


if __name__ == "__main__":
    main()
