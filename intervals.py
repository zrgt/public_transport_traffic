from datetime import datetime

from bokeh.io import show, curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral11, Set1_9
from bokeh.plotting import figure

from dataframe import get_dataframe
from graph_utils import init_map_graph, THEME, init_interval_graph
from utils import lon_to_x_mercator, lat_to_y_mercator

FILE = f"all_pos.json"


def detect_directions(group, x1, x2, p, name, color):  # TODO: use
     group["direction"] = "A"
     group.loc[group.x > (x1 + x2) / 2, "direction"] = "B"
     groupA = group[group.direction == "A"]
     groupB = group[group.direction == "B"]
     group["route"] = group["route"] + group["direction"]
     if not groupA.empty:
        source = ColumnDataSource(groupA)
        p.scatter(x="lasttime", y="route_interval", legend_label=str(name)+"A", color=color, size=9, source=source)
     if not groupB.empty:
        source = ColumnDataSource(groupB)
        p.scatter(x="lasttime", y="route_interval", legend_label=str(name)+"B", color=color, size=9, source=source)


def intervals_graph_in_rect(lon1=107586778, lon2=107599903, lat1=51812255, lat2=51824591):
    x1 = lon_to_x_mercator(lon1)
    x2 = lon_to_x_mercator(lon2)
    y1 = lat_to_y_mercator(lat1)
    y2 = lat_to_y_mercator(lat2)

    df = get_dataframe(FILE)
    df = df[["gos_num", "lon", "lat", "x", "y", "timestamp", "time", "route", "lasttime"]]
    df = df[(df.x > x1) & (df.x < x2) & (df.y > y1) & (df.y < y2)]

    df = df.sort_values(["gos_num", "timestamp"])
    p = init_interval_graph()
    rows = 0
    for (name, group), color in zip(df.groupby('route'), Set1_9):
        group['wagon_interval'] = group['timestamp'].diff().fillna(0)
        group = group[(group.wagon_interval > 600) | (group.wagon_interval <= 0)]  # keep first wagon points in the area

        group = group.sort_values(["route", "timestamp"])
        group['route_interval'] = group['timestamp'].diff() / 60
        source = ColumnDataSource(group)

        p.scatter(x="lasttime", y="route_interval", legend_label=str(name), color=color, size=9, source=source)
        rows = rows + len(group.index)
    print("Rows: ", rows)
    p.legend.click_policy = "hide"
    layout = column(p)
    show(layout)


if __name__ == "__main__":
    intervals_graph_in_rect()
