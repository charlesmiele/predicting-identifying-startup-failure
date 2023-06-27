import pandas as pd
import os

# How many failed?
# How many succeeded?
# How may total

list_of_logs = [f for f in os.listdir('log-reports') if f[:4] == "lp_p"]


for log in list_of_logs:
    df = pd.read_csv(f"log-reports/{log}")
    failed = len(df[df['failed'] == 1].index)
    print(list_of_logs.index(log) + 1)
    print("Failed:", failed)
    # Reasons for failure
    # fr = df[df['failed'] == 1]['reason_for_failure'].value_counts
    # print("Reasons:")
    # print(fr.to_string())
    print("Successes:", len(df.index) - failed)
    print("Total:", len(df.index))
