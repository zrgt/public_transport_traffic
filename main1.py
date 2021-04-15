import os
import bokeh.plotting as bp
from bokeh.models.tiles import WMTSTileSource
import datashader as ds
import datashader.transfer_functions as tf
from datashader.bokeh_ext import InteractiveImage
from datashader.utils import export_image
import colorcet as cc
from datashader.utils import lnglat_to_meters
import pandas as pd
import json

with open("positions.json", "r") as file:
    a=json.load(file)
    trams = a["anims"]

lons = tuple(tram["lon"] for tram in trams)
lats = tuple(tram["lat"] for tram in trams)

x_coords, y_coords = lnglat_to_meters(lons, lats)
gps_data = pd.DataFrame({'coord_x': x_coords, 'coord_y': y_coords})

bp.output_notebook()

# x_range = (11974009, 11986891)
# y_range = (6764588, 6775033)
x_range=(2.101e6, 2.155e6)
y_range=(5.994e6, 6.052e6)

if not os.path.exists('./img'):
    os.mkdir('./img')

p = bp.figure(tools='pan,wheel_zoom,reset',
              plot_width=int(600),
              plot_height=int(600),
              x_range=x_range,
              y_range=y_range)

# p.axis.visible = False
# p.xgrid.grid_line_color = None
# p.ygrid.grid_line_color = None

url = "https://cartodb-basemaps-b.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png"
# url = "http://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
tile_renderer = p.add_tile(WMTSTileSource(url=url))
tile_renderer.alpha = 1


def image_callback(x_range, y_range, w, h, color_fn=tf.shade):
    cvs = ds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
    agg = cvs.points(gps_data, 'coord_x', 'coord_y', agg=ds.count())
    image = tf.shade(agg, cmap=cc.fire, how='eq_hist')
    return tf.dynspread(image, threshold=0.1, max_px=20)


export_image(image_callback(x_range=x_range, y_range=y_range, w=2000, h=2000),
             filename="UU_traffic", background='black')
InteractiveImage(p, image_callback)
