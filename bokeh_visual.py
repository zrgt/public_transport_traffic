# importing the modules
import json
from collections import defaultdict

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Slider, CustomJS, ColumnDataSource, Button
from bokeh.plotting import figure, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

from utils import lon_to_x_mercator, lat_to_y_mercator

TIMESTAMPS = 120
tile_provider = get_provider(CARTODBPOSITRON)
# instantiating the figure object
# graph = figure(x_range=(10754000, 10770000), y_range=(5178000, 5189000),
graph = figure(x_range=(11000000, 13000000), y_range=(6000000, 7000000),
               plot_width=600, plot_height=600)
graph.add_tile(tile_provider)

graph.scatter([0, 6200000], [0, 11700000])


with open(f"all_pos.json", "r") as file:
    all_pos = list(json.load(file).values())
    all_pos_x = []
    all_pos_y = []
    for pos in all_pos:
        pos_x = [lon_to_x_mercator(auto["lon"]) for auto in pos]
        pos_y = [lat_to_y_mercator(auto["lat"]) for auto in pos]
        all_pos_x.append(pos_x)
        all_pos_y.append(pos_y)

x_0 = all_pos_x[0]
y_0 = all_pos_y[0]

source_visible = ColumnDataSource(data=defaultdict(x=x_0, y=y_0))
source_available = ColumnDataSource(data=defaultdict(all_pos_x=all_pos_x, all_pos_y=all_pos_y))

# plotting the graph
graph.scatter("x", "y", source=source_visible)

time_slider = Slider(start=0, end=TIMESTAMPS-1, value=0, step=1, title="Time stamps")

callback = CustomJS(args=dict(source_visible=source_visible, source_available=source_available,
                              time_num=time_slider),
                    code="""
    const n = time_num.value;
    var vis_data = source_visible.data;
    var data = source_available.data;
    vis_data['x'] = data['all_pos_x'][n];
    vis_data['y'] = data['all_pos_y'][n];
    source_visible.change.emit();
""")

def animate_update():
    timestamp = time_slider.value + 1
    if timestamp > TIMESTAMPS-1:
        timestamp = 0
    time_slider.value = timestamp

def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)

button = Button(label='► Play', width=60)
# button.on_click(animate)

time_slider.js_on_change("value", callback)

layout = column(graph, time_slider, button)
# displaying the model
show(layout)
