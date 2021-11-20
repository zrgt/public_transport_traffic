import datetime

from bokeh.layouts import column, row
from bokeh.models import Slider, CustomJS, ColumnDataSource, CustomJSFilter, CDSView, Spinner, RangeSlider, \
    DateRangeSlider, Paragraph, TableColumn, DataTable

from bokeh.plotting import show
from scipy.spatial.distance import pdist, squareform
import bokeh.models as bmo

from dataframe import get_dataframe
from graph_utils import init_map_graph, get_checkboxes_with_filter, get_checkbox_btn_with_filter

#TODO посчитать правильные ли скорости
#TODO

start_time = datetime.datetime.now()
FILE = f"all_pos.json"

#init graph
graph = init_map_graph(title="Скорость трамвая в среду 1 сентября 2021")

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

# in jam checkbox
in_jam_list = list(df.in_jam.unique())
in_jam_checkboxes, in_jam_filter = get_checkbox_btn_with_filter(labels=["В пробке"], column_label="in_jam", source=source_visible)

# range slider for speeds
min_speed = df.speed.min()
max_speed = df.speed.max()
speed_slider = RangeSlider(
    title="Скорость транспорта (км/ч)",
    start=min_speed,
    # end=max_speed,
    end=55,
    step=1,
    value=(min_speed, 55),
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
        s2.data = {
            "lon":[],
            "lat":[],
            "gos_num":[],
            "num":[],
            "speed":[],
            "time":[],
            "timestamp":[],
            "secs_frm_lst_pos":[],
            "meters_frm_lst_pos":[],
            "secs_in_jam":[],
            "mins_in_jam":[],
            };
        var d2 = s2.data;
        d2['gos_num'] = [];
        d2['num'] = [];
        for (var i = 0; i < inds.length; i++) {
            d2['gos_num'].push(d1['gos_num'][inds[i]]);
            d2['num'].push(d1['num'][inds[i]]);
            d2['speed'].push(d1['speed'][inds[i]]);
            d2['time'].push(d1['time'][inds[i]]);
            d2['timestamp'].push(d1['timestamp'][inds[i]]);
            d2['secs_frm_lst_pos'].push(d1['secs_frm_lst_pos'][inds[i]]);
            d2['secs_in_jam'].push(null);
            d2['mins_in_jam'].push(null);
            d2['meters_frm_lst_pos'].push(d1['meters_frm_lst_pos'][inds[i]]);
            d2['lon'].push(d1['lon'][inds[i]]);
            d2['lat'].push(d1['lat'][inds[i]]);
        }
        
        var gos_nums = new Set(d2['gos_num']);
        console.log(gos_nums);
        gos_nums = Array.from(gos_nums)
        console.log(gos_nums);
        console.log(gos_nums.length);
        for (var i = 0; i < gos_nums.length; i++) {
            console.log(i);
            var curr_gos_num = gos_nums[i];
            console.log(curr_gos_num);
            var firsttime_veh = d2['gos_num'].indexOf(curr_gos_num);
            console.log(firsttime_veh);
            var lasttime_veh = d2['gos_num'].lastIndexOf(curr_gos_num);
            console.log(lasttime_veh);
            var duration = d2['timestamp'][lasttime_veh] - d2['timestamp'][firsttime_veh]
            d2['secs_in_jam'][firsttime_veh] = duration;
            d2['mins_in_jam'][firsttime_veh] = (duration/60).toFixed(2);
            
        }
        
        s2.change.emit();
    """)
)
columns = [
        TableColumn(field="gos_num", title="Номер"),
        TableColumn(field="num", title="Маршрут"),
        TableColumn(field="time", title="Время"),
        TableColumn(field="speed", title="Ск-сть"),
        TableColumn(field="secs_in_jam", title="Интервал(Сек)"),
        TableColumn(field="mins_in_jam", title="Интерв.(Минут)"),
        # TableColumn(field="secs_frm_lst_pos", title="Промежуток(Сек)"),
        # TableColumn(field="meters_frm_lst_pos", title="Промежуток(М)"),
    ]
text_banner = Paragraph(text="Выбранные геометки", width=200, height=20)
data_table = DataTable(source=source_table, columns=columns, width=600, height=700, aspect_ratio="auto")


view = CDSView(source=source_visible, filters=[time_filter, speed_filter, routes_filter, gos_num_filter, in_jam_filter])

# plotting the graph
points = graph.scatter("x", "y", source=source_visible, fill_color="color", size="size",
                       fill_alpha=0.5, line_color=None, view=view)
spinner = Spinner(title="Размер точек", low=1, high=40, step=1, value=7, width=80)
spinner.js_link('value', points.glyph, 'size')


# displaying the model
layout = row(column(graph, time_slider,  speed_slider, row(spinner, in_jam_checkboxes)), column(routes_checkboxes, width=60), column(gos_num_checkboxes, width=60), column(text_banner, data_table))
show(layout)
