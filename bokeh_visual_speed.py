# importing the modules
import json
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, CustomJS, ColumnDataSource, Button, WheelZoomTool, CheckboxGroup, \
    CustomJSFilter, CDSView, Spinner, IndexFilter
from bokeh.plotting import figure, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
import pandas as pd
import bokeh.models as bmo
from utils import lon_to_x_mercator, lat_to_y_mercator, speed_color

FILE = "all_pos_8_9.json"
TIMESTAMPS = 180

TOOLS="hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save"
curdoc().theme = 'dark_minimal'
tile_provider = get_provider(CARTODBPOSITRON)
# instantiating the figure object
graph = figure(x_range=(11960000, 12000000), y_range=(6750000, 6780000),
               plot_width=800, plot_height=800, tools=TOOLS)
for tool in graph.toolbar.tools:
    if isinstance(tool, WheelZoomTool):
        graph.toolbar.active_scroll = tool
        break
graph.add_tile(tile_provider)
graph.grid.visible = False

with open(FILE, "r", encoding='utf-8') as file:
    all_pos_data = list(json.load(file).values())
    all_pos_x, all_pos_y, all_speeds, all_colors, all_routes, all_angles = [], [], [], [], [], []
    for pos in all_pos_data:
        pos_x, pos_y, speed, color, route, angle = [], [], [], [], [], []
        for auto in pos:
            pos_x.append(lon_to_x_mercator(auto["lon"]))
            pos_y.append(lat_to_y_mercator(auto["lat"]))
            angle.append(auto["dir"])
            speed.append(auto["speed"])
            color.append(speed_color(auto["speed"]))
            route.append(f"{auto['rtype']}-{auto['rnum']}")
        all_pos_x.append(pos_x)
        all_pos_y.append(pos_y)
        all_angles.append(angle)
        all_speeds.append(speed)
        all_colors.append(color)
        all_routes.append(route)

df_visible = pd.DataFrame(
    {
        "x": all_pos_x[0],
        "y": all_pos_y[0],
        "speed": all_speeds[0],
        "color": all_colors[0],
        "route": all_routes[0],
        "angle": all_angles[0],
    }
)
source_visible = ColumnDataSource(df_visible)

df = pd.DataFrame(
    {
        "x": all_pos_x,
        "y": all_pos_y,
        "speed": all_speeds,
        "color": all_colors,
        "route": all_routes,
        "angle": all_angles,
    }
)
source_available = ColumnDataSource(df)

# routes checkboxes
routes_list = list({f"{auto['rtype']}-{auto['rnum']}" for auto in pos})
routes_list.sort()
routes_checkboxes = CheckboxGroup(labels=routes_list, active=list(range(len(routes_list))))
time_slider = Slider(start=0, end=TIMESTAMPS-1, value=0, step=1, title="Time stamps")

#FIXME indices are different each timestamp!
custom_filter = CustomJSFilter(code='''
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
,args={'checkboxes': routes_checkboxes})
routes_checkboxes.js_on_change("active", CustomJS(code="source.change.emit();", args=dict(source=source_visible)))

view = CDSView(source=source_visible, filters=[custom_filter])
# plotting the graph
points = graph.scatter("x", "y", source=source_visible, fill_color="color", size=10, view=view, line_color=None)
spinner = Spinner(title="Glyph size", low=1, high=40, step=1, value=10, width=80)
spinner.js_link('value', points.glyph, 'size')

slider_callback = CustomJS(args=dict(source_visible=source_visible, source_available=source_available,
                                     time_num=time_slider),
                           code="""
    const n = time_num.value;
    var vis_data = source_visible.data;
    var data = source_available.data;
    vis_data['x'] = data['x'][n];
    vis_data['y'] = data['y'][n];
    vis_data['color'] = data['color'][n];
    vis_data['angle'] = data['angle'][n];
    source_visible.change.emit();
""")


button = Button(label='► Play', width=60)
# button.on_click(animate)

time_slider.js_on_change("value", slider_callback)

layout = row(column(graph, time_slider, button), column(spinner, routes_checkboxes))
# displaying the model
show(layout)
