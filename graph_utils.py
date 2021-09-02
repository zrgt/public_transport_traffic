from typing import List

import bokeh
from bokeh.io import curdoc
from bokeh.models import HoverTool, CheckboxGroup, CustomJSFilter, CustomJS, Button, Column
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, CARTODBPOSITRON

#Plot settings
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 800
GRAPH_MAP_PROVIDER = get_provider(CARTODBPOSITRON)
GRAPH_TITLE = "Ulan-Ude"
GRAPH_TOOLS = "hover,pan,wheel_zoom,zoom_in,zoom_out,box_select, lasso_select, reset,save"
THEME = "dark_minimal"

UU_LON_RANGE = (11975000, 11987000)
UU_LAT_RANGE = (6764000, 6775000)


# instantiating the figure object
def init_map_graph(title=GRAPH_TITLE, lon_range=UU_LON_RANGE, lat_range=UU_LAT_RANGE,
                   width=GRAPH_WIDTH, height=GRAPH_WIDTH, tools=GRAPH_TOOLS):
    curdoc().theme = THEME

    graph = figure(x_range=lon_range, y_range=lat_range,
                   plot_width=width, plot_height=height, tools=tools)
    hover = graph.select(dict(type=HoverTool))
    hover.tooltips = {"Госномер": "@gos_num", "Маршрут": "@route", "Скорость(км/ч)": "@speed", "Время": "@time", "x": "@x", "y": "@y"}
    for tool in graph.toolbar.tools:
        if isinstance(tool, bokeh.models.WheelZoomTool):
            graph.toolbar.active_scroll = tool
            break
    graph.add_tile(GRAPH_MAP_PROVIDER)
    graph.grid.visible = False
    graph.axis.visible = False
    graph.title.text = title
    return graph


def get_checkboxes_with_filter(labels: List[str], column_label: str, source, select_all_btn=True, clear_all_btn=True):
    """
    :param labels: names for checkbox labels as list (dataframe must contain it as value to filter)
    :param column_label: name of column in dataframe
    :param source: dataframe
    :return: checkboxes and filter for graph
    """
    # routes checkboxes
    checkboxes = CheckboxGroup(labels=labels, active=list(range(len(labels))))
    filter = CustomJSFilter(code='''
    var selected = checkboxes.active.map(i=>checkboxes.labels[i]);
    var indices = [];
    var column = source.data[column_label];

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
    ''', args=dict(checkboxes=checkboxes, column_label=column_label))
    checkboxes.js_on_change("active", CustomJS(code="source.change.emit();", args=dict(source=source)))

    widgets = [checkboxes]

    if select_all_btn:
        select_all = Button(label="выбрать все", width=65, height=30)
        select_all.js_on_click(CustomJS(args=dict(checkboxes=checkboxes, all_active=list(range(len(labels)))), code="""
            checkboxes.active = all_active
        """))
        widgets.append(select_all)

    if clear_all_btn:
        clear_all = Button(label="отчистить", width=65, height=30)
        clear_all.js_on_click(CustomJS(args=dict(checkboxes=checkboxes), code="""
            checkboxes.active = []
        """))
        widgets.append(clear_all)

    return Column(*widgets), filter
