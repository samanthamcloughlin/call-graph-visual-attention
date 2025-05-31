import csv
import glob
import sqlite3

from constants import DATA_DIR

cols = ["fixation_id",
        "fixation_run_id",
        "fixation_start_event_time",
        "fixation_order_number",
        "x",
        "y",
        "fixation_target",
        "source_file_line",
        "source_file_col",
        "token",
        "syntactic_category",
        "xpath",
        "left_pupil_diameter",
        "right_pupil_diameter",
        "duration"]

def db3_to_csv(file_name):
    try:
        conn = sqlite3.connect(file_name)
        cur = conn.cursor()
        data = cur.execute("SELECT * FROM fixation").fetchall()
        if len(data) > 0:
            if "_" not in file_name:
                output = f'{file_name[:-4].replace("-T", "_T")}.csv'
            else:
                output = file_name[:-6].upper() + file_name[-6:].replace("_", ".")
                output = f'{output[:-4]}.csv'
            with open(output, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(data)
    except:
        print("error ", file_name)

for f in glob.glob(f"{DATA_DIR}/P*/P*/**.db3"):
    db3_to_csv(f)
    ## Note - have to manually split combined data