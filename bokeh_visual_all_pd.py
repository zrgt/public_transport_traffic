# importing the modules
import datetime
import json

from bokeh.layouts import column, row
from bokeh.models import Slider, CustomJS, ColumnDataSource, Button, WheelZoomTool, CheckboxGroup, \
    CustomJSFilter, CDSView, Spinner
from bokeh.plotting import show
import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
import bokeh.models as bmo

from graph_utils import init_map_graph
from utils import lon_to_x_mercator, lat_to_y_mercator, pd_speed_color

start_time = datetime.datetime.now()
FILE = f"all_pos_8_9.json"
ROUTES_LIST = ["Тр-1", "Тр-2", "Тр-4"]
TIMESTAMPS = 180

#init graph
graph = init_map_graph(title="Средняя скорость трамвая в понедельник 19 апреля 2021 между 8-9ч")

with open(FILE, "r") as file:
    geo_marker_dicts_lists = list(json.load(file).values())
geo_markers = []
for lst in geo_marker_dicts_lists:
    geo_markers.extend(lst)
df = pd.DataFrame(geo_markers)
df.drop_duplicates(inplace=True)
df.drop(["low_floor"], axis=1, inplace=True)
indexNotTrams = df[df["rtype"] != "Тр"].index
df.drop(index=indexNotTrams, inplace=True)
df["lon"] = lon_to_x_mercator(df["lon"])
df["lat"] = lat_to_y_mercator(df["lat"])
df["route"] = df["rtype"]+"-"+df["rnum"]
def fix_time(row):
    time = datetime.datetime.strptime(row.lasttime, "%d.%m.%Y %H:%M:%S")
    time = time.replace(hour=time.hour + 8)
    row.lasttime = time.strftime("%H:%M:%S")
    return row
df = df.apply(fix_time, axis="columns")
df["color"] = ""
df = df.apply(pd_speed_color, axis="columns")

pos = df[(df.speed < 8)][["lat", "lon"]]
sf = squareform(pdist(pos))
pos["num_near_points"] = (sf < 100).sum(axis=1) / 2.5
df["size"] = pos["num_near_points"]
df["size"].fillna(7, inplace=True)
df["size"] = df["size"].astype("int32")

df.rename(columns={"lon":"x", "lat":"y", "lasttime":"time", "rnum":"num"}, inplace=True)
print(df.head)

end_time = datetime.datetime.now()
print(end_time - start_time)

source_visible = ColumnDataSource(df)

# routes checkboxes
speeds = [">18Kmh", "8-18Kmh", "<8Kmh"]
speed_checkboxes = CheckboxGroup(labels=speeds, active=list(range(len(speeds))))

speed_filter = CustomJSFilter(code='''
var selected = checkboxes.active.map(i=>checkboxes.labels[i]);
var indices = [];
var column = source.data['speed'];

// iterate through rows of data source and see if each satisfies some constraint
for (var i = 0; i < column.length; i++){
    if(selected.includes('>18Kmh') && column[i]>18){
        indices.push(true);
    } else if (selected.includes('8-18Kmh') && column[i]>8 && column[i]<18) {
        indices.push(true);
    } else if (selected.includes('<8Kmh') && column[i]<8) {
        indices.push(true);
    } else {
        indices.push(false);
    }
}
console.log("filter completed");
return indices;
''', args={'checkboxes': speed_checkboxes})
speed_checkboxes.js_on_change("active", CustomJS(code="source.change.emit();", args=dict(source=source_visible)))

# routes checkboxes
routes_checkboxes = CheckboxGroup(labels=ROUTES_LIST, active=list(range(len(ROUTES_LIST))))

routes_filter = CustomJSFilter(code='''
var selected = checkboxes.active.map(i=>checkboxes.labels[i]);
var indices = [];
var column = source.data['route'];

// iterate through rows of data source and see if each satisfies some constraint
for (var i = 0; i < column.length; i++){
    if(selected.includes(column[i])){
        indices.push(true);
    } else {
        indices.push(false);
    }
}
console.log("filter completed");
return indices;
'''
                               , args={'checkboxes': routes_checkboxes})
routes_checkboxes.js_on_change("active", CustomJS(code="source.change.emit();", args=dict(source=source_visible)))

view = CDSView(source=source_visible, filters=[speed_filter, routes_filter])
# plotting the graph
points = graph.scatter("x", "y", source=source_visible, fill_color="color", size="size",
                       fill_alpha=0.3, line_color=None, view=view)
spinner = Spinner(title="Points size", low=1, high=40, step=1, value=7, width=80)
# spinner.js_link('value', points.glyph, 'size')

layout = row(graph, column(spinner, speed_checkboxes, routes_checkboxes))
# displaying the model
show(layout)
