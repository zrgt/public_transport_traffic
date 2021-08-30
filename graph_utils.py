import bokeh
from bokeh.io import curdoc
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, CARTODBPOSITRON

#Plot settings
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 800
GRAPH_MAP_PROVIDER = get_provider(CARTODBPOSITRON)
GRAPH_TITLE = "Ulan-Ude"
GRAPH_TOOLS = "hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save"
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
    hover.tooltips = {"Number": "@num", "Route": "@route", "Kmh": "@speed", "Time": "@time", "x": "@x", "y": "@y"}
    for tool in graph.toolbar.tools:
        if isinstance(tool, bokeh.models.WheelZoomTool):
            graph.toolbar.active_scroll = tool
            break
    graph.add_tile(GRAPH_MAP_PROVIDER)
    graph.grid.visible = False
    graph.axis.visible = False
    graph.title.text = title
    return graph