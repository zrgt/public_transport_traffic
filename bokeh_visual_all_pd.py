import datetime
import json

from bokeh.layouts import column, row
from bokeh.models import Slider, CustomJS, ColumnDataSource, Button, WheelZoomTool, CheckboxGroup, \
    CustomJSFilter, CDSView, Spinner, RangeSlider
from bokeh.plotting import show
from scipy.spatial.distance import pdist, squareform
import bokeh.models as bmo

from dataframe import get_dataframe
from graph_utils import init_map_graph, get_checkboxes_with_filter

start_time = datetime.datetime.now()
FILE = f"all_pos_8_9.json"
TIMESTAMPS = 180

#init graph
graph = init_map_graph(title="Средняя скорость трамвая в понедельник 19 апреля 2021 между 8-9ч")

df = get_dataframe(FILE)

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
routes_list = list(df.route.unique())
routes_list.sort()
routes_checkboxes, routes_filter = get_checkboxes_with_filter(labels=routes_list, column_label="route", source=source_visible,
                                                              select_all_btn=False, clear_all_btn=False)
# gos num checkboxes
gos_num_list = list(df.gos_num.unique())
gos_num_list.sort()
gos_num_checkboxes, gos_num_filter = get_checkboxes_with_filter(labels=gos_num_list, column_label="gos_num", source=source_visible)

view = CDSView(source=source_visible, filters=[speed_filter, routes_filter, gos_num_filter])
# plotting the graph
points = graph.scatter("x", "y", source=source_visible, fill_color="color", size="size",
                       fill_alpha=0.3, line_color=None, view=view)
spinner = Spinner(title="Points size", low=1, high=40, step=1, value=7, width=80)
# spinner.js_link('value', points.glyph, 'size')

layout = row(graph, column(spinner, speed_checkboxes, routes_checkboxes))
# displaying the model
layout = row(column(graph, range_slider), column(spinner, speed_checkboxes), routes_checkboxes, gos_num_checkboxes)
show(layout)
