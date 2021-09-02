import datetime

from bokeh.layouts import column, row
from bokeh.models import Slider, CustomJS, ColumnDataSource, CustomJSFilter, CDSView, Spinner, RangeSlider, DateRangeSlider, Paragraph, TableColumn, DataTable

from bokeh.plotting import show
from scipy.spatial.distance import pdist, squareform
import bokeh.models as bmo

from dataframe import get_dataframe
from graph_utils import init_map_graph, get_checkboxes_with_filter

start_time = datetime.datetime.now()
FILE = f"all_pos.json"

#init graph
graph = init_map_graph(title="Средняя скорость трамвая в понедельник 19 апреля 2021 между 8-9ч")

df = get_dataframe(FILE)

source_visible = ColumnDataSource(df)

# routes checkboxes
routes_list = list(df.route.unique())
routes_list.sort()
routes_checkboxes, routes_filter = get_checkboxes_with_filter(labels=routes_list, column_label="route", source=source_visible,
                                                              select_all_btn=False, clear_all_btn=False)
# gos num checkboxes
gos_num_list = list(df.gos_num.unique())
gos_num_list.sort()
gos_num_checkboxes, gos_num_filter = get_checkboxes_with_filter(labels=gos_num_list, column_label="gos_num", source=source_visible)

# range slider for speeds
min_speed = df.speed.min()
max_speed = df.speed.max()
speed_slider = RangeSlider(
    title="Скорость транспорта (км/ч)",
    start=min_speed,
    end=max_speed,
    step=1,
    value=(min_speed, max_speed),
)
speed_filter = CustomJSFilter(code='''
var min_speed = speed_slider.value[0]
var max_speed = speed_slider.value[1]

var indices = [];
var column = source.data['speed'];

// iterate through rows of data source and see if each satisfies some constraint
for (var i = 0; i < column.length; i++){
    if(column[i]>min_speed && column[i]<max_speed){
        indices.push(true);
    } else {
        indices.push(false);
    }
}
console.log("filter completed");
return indices;
''', args={'speed_slider': speed_slider})
speed_slider.js_on_change("value", CustomJS(code="source.change.emit();", args=dict(source=source_visible)))

# range slider for time
start = datetime.datetime.fromtimestamp(df.timestamp.min())
end = datetime.datetime.fromtimestamp(df.timestamp.max())
time_slider = DateRangeSlider(title="Промежуток времени", value=(start, end), start=start, end=end, format="%H:%M", step=10*60*1000)
time_filter = CustomJSFilter(code='''
var min_timestamp = time_slider.value[0]/1000 - 7200
var max_timestamp = time_slider.value[1]/1000 - 7200
console.log(min_timestamp, max_timestamp);

var indices = [];
var column = source.data['timestamp'];

// iterate through rows of data source and see if each satisfies some constraint
for (var i = 0; i < column.length; i++){
    if(column[i]>min_timestamp && column[i]<max_timestamp){
        indices.push(true);
    } else {
        indices.push(false);
    }
}
console.log("filter completed");
return indices;
''', args={'time_slider': time_slider})
time_slider.js_on_change("value", CustomJS(code="source.change.emit();", args=dict(source=source_visible)))





source_table = ColumnDataSource()

source_visible.selected.js_on_change('indices', CustomJS(args=dict(s1=source_visible, s2=source_table), code="""
        var inds = cb_obj.indices;
        var d1 = s1.data;
        s2.data = {"gos_num":[],"num":[],"speed":[],"time":[],"secs_frm_lst_pos":[],"meters_frm_lst_pos":[]};
        var d2 = s2.data;
        d2['gos_num'] = [];
        d2['num'] = [];
        for (var i = 0; i < inds.length; i++) {
            d2['gos_num'].push(d1['gos_num'][inds[i]]);
            d2['num'].push(d1['num'][inds[i]]);
            d2['speed'].push(d1['speed'][inds[i]]);
            d2['time'].push(d1['time'][inds[i]]);
            d2['secs_frm_lst_pos'].push(d1['secs_frm_lst_pos'][inds[i]]);
            d2['meters_frm_lst_pos'].push(d1['meters_frm_lst_pos'][inds[i]]);
        }
        s2.change.emit();
    """)
)
columns = [
        TableColumn(field="gos_num", title="Госномер"),
        TableColumn(field="num", title="Маршрут"),
        TableColumn(field="time", title="Время"),
        TableColumn(field="speed", title="Скорость"),
        TableColumn(field="secs_frm_lst_pos", title="Промежуток (Сек)"),
        TableColumn(field="meters_frm_lst_pos", title="Промежуток (М)"),
    ]
text_banner = Paragraph(text="Выбранные геометки", width=200, height=40)
data_table = DataTable(source=source_table, columns=columns, width=600, height=600)


view = CDSView(source=source_visible, filters=[time_filter, speed_filter, routes_filter, gos_num_filter])

# plotting the graph
points = graph.scatter("x", "y", source=source_visible, fill_color="color", size="size",
                       fill_alpha=0.5, line_color=None, view=view)
spinner = Spinner(title="Размер точек", low=1, high=40, step=1, value=7, width=80)
spinner.js_link('value', points.glyph, 'size')


# displaying the model
layout = row(column(graph, time_slider,  speed_slider), column(spinner), column(routes_checkboxes, width=60), column(gos_num_checkboxes, width=60), column(text_banner, data_table))
show(layout)
