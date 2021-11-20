import datetime
import json

import pandas as pd
from scipy.spatial.distance import pdist, squareform

from utils import lon_to_x_mercator, lat_to_y_mercator, pd_speed_color

start_time = datetime.datetime.now()
FILE = f"all_pos_8_9.json"


def get_dataframe(file):
    # Open data file
    with open(file, "r", encoding='utf-8') as file:
        # List with lists for each parse iteration
        geo_marker_dicts_lists = list(json.load(file).values())

    # Export all lists in one big list
    geo_markers = []
    for lst in geo_marker_dicts_lists:
        geo_markers.extend(lst)

    df = pd.DataFrame(geo_markers)
    df.drop_duplicates(inplace=True)
    df.drop_duplicates(subset=["lon", "lat", "lasttime"], inplace=True)
    # drop useless data column
    df.drop(["low_floor"], axis=1, inplace=True)
    # drop all vehicles except trams
    indexNotTrams = df[df["rtype"] != "Тр"].index
    df.drop(index=indexNotTrams, inplace=True)
    # change geo data in standard for maps
    df["lon_mercator"] = lon_to_x_mercator(df["lon"])
    df["lat_mercator"] = lat_to_y_mercator(df["lat"])

    df["route"] = df["rtype"]+"-"+df["rnum"]

    # fix time: drop day data and change timezone
    def fix_time(row):
        lasttime = datetime.datetime.strptime(row.lasttime, "%d.%m.%Y %H:%M:%S")
        lasttime = lasttime+datetime.timedelta(hours=8)
        #lasttime = pytz.timezone("Asia/Irkutsk").localize(lasttime)
        row.lasttime = str(lasttime)
        row.time = lasttime.strftime("%H:%M:%S")
        row.timestamp = lasttime.timestamp()
        return row
    df["time"] = None
    df["timestamp"] = None
    df = df.apply(fix_time, axis="columns")

    # add column data for point color and fill it with data
    df["color"] = ""
    df = df.apply(pd_speed_color, axis="columns")

    # make red (slow) points bigger if there are slow points near
    pos = df[(df.speed < 8)][["lat", "lon"]]
    sf = squareform(pdist(pos))
    pos["num_near_points"] = (sf < 100).sum(axis=1) / 2.5
    df["size"] = pos["num_near_points"]
    df["size"].fillna(7, inplace=True)
    df["size"] = df["size"].astype("int32")

    df["size"] = 10 #FIXME

    # rename data columns in dataframe
    df.rename(columns={"lon_mercator":"x", "lat_mercator":"y", "rnum":"num"}, inplace=True)
    print(df.head)

    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return df

if __name__ == "__main__":
    get_dataframe(FILE)