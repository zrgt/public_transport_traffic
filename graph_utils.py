import bokeh

#Plot settings
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 800
GRAPH_MAP_PROVIDER = bokeh.tile_providers.get_provider(bokeh.tile_providers.CARTODBPOSITRON)
GRAPH_TITLE = "Ulan-Ude"
GRAPH_TOOLS = "hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save"
THEME = "dark_minimal"

UU_LON_RANGE = (11975000, 11987000)
UU_LAT_RANGE = (6764000, 6775000)


# instantiating the figure object
def init_map_graph(title=GRAPH_TITLE, lon_range=UU_LON_RANGE, lat_range=UU_LAT_RANGE,
                   width=GRAPH_WIDTH, height=GRAPH_WIDTH, tools=GRAPH_TOOLS):
    bokeh.io.curdoc().theme = THEME

    graph = bokeh.plotting.figure(x_range=lon_range, y_range=lat_range,
                   plot_width=width, plot_height=height, tools=tools)
    hover = graph.select(dict(type=bokeh.models.HoverTool))
    hover.tooltips = {"Number": "@num", "Route": "@route", "Kmh": "@speed", "Time": "@time"}
    for tool in graph.toolbar.tools:
        if isinstance(tool, bokeh.models.WheelZoomTool):
            graph.toolbar.active_scroll = tool
            break
    graph.add_tile(GRAPH_MAP_PROVIDER)
    graph.grid.visible = False
    graph.axis.visible = False
    graph.title.text = title
    return graph