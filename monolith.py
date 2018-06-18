import numpy as np
import time
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure
from bokeh.models import TextInput, CustomJS, Rect
from bokeh.models.tools import HoverTool, CrosshairTool
from bokeh.layouts import row, column, widgetbox
from bokeh.palettes import all_palettes
from bokeh.io import curdoc
from more_itertools import unique_everseen
from read import read_main_df, read_metadata, flippit
from utils import strack, get_functions_dict

from sources import (get_filename, get_matrix_cds, get_img,
                     get_stim_select_options, get_fixation_points)

import orders
import metrics

FLASK_ARGS = curdoc().session_context.request.arguments

#  COMPONENTS
#################
# 1 # 2 2 # 3 3 #
# 1 # 2 2 # 4 4 #
#################

PRESENTING = True

# _.-*-._ Default settings _.-*-._

META = read_metadata()  # Keys are names of stimuli files (stim.jpg)
DF = read_main_df()
# Flipped upside down
DF['MappedFixationPointY'] = DF.apply(flippit, args=(META,), axis=1)
USERS = list(DF.user.unique())
# Ordering algorithms
ORDERS = get_functions_dict(orders)
# Similarity algorithms
METRICS = get_functions_dict(metrics)

STIM = '03_Bordeaux_S1.jpg'
COLOR = 'Inferno'
ORDER = 'seriationMDS'
METRIC = 'simple_bbox'
GAZE_COLORS = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c',
               '#fabebe', '#008080', '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
               '#000080', '#808080', '#000000', '#71e441']

if not PRESENTING:
    USERS = USERS[:10]

# _.-*-._ Data sources _.-*-._ (sources.py)

# 1st component
stim_select_cds = get_stim_select_options(META)

# 2nd component
matrix_cds = get_matrix_cds(STIM, USERS, DF, COLOR, METRICS[METRIC])

# 3rd component

# 4th component
image_cds = get_img(STIM)

fixation_cds = get_fixation_points(matrix_cds.data['MappedFixationPointX'],
                                   matrix_cds.data['MappedFixationPointY'])

# _.-*-._ Widgets _.-*-._

# Selecting stimulus, filter options through TextInput widget ti
stim_select = Select(options=stim_select_cds.data['options'], value=STIM)
text_input = TextInput(placeholder='Enter filter', title='Stimulus',
                       callback=CustomJS(args=dict(ds=stim_select_cds, s=stim_select),
                                         code="s.options = ds.data['options'].filter(i => i.includes(cb_obj.value));"))

# Select color scheme for matrix
color_select = Select(title="Color Scheme", value=COLOR,
                      options=['SteelBlue', 'Tomato', 'MediumSeaGreen', 'Inferno', 'Magma', 'Plasma', 'Viridis'])

# Select ordering for matrix
order_select = Select(title='Ordering', value=ORDER, options=list(ORDERS.keys()))

# Select metric for matrix
metric_select = Select(title='Metric', value=METRIC, options=list(METRICS.keys()))

# Widgets will show on the dashboard in this order
widgets = [text_input, stim_select, color_select, order_select, metric_select]

# --- Plotting variables
plot_kwargs = dict()

# Plot borders
plot_kwargs.update({'min_border_left': 10,
                    'min_border_right': 40,
                    'min_border_top': 40,
                    'min_border_bottom': 0,
                    'border_fill_color': 'mistyrose'})

# Used to respond to window resizes (maintaining original aspect ratio)
plot_kwargs.update({'sizing_mode': 'scale_both'})

# Built-in Bokeh tools
plot_kwargs.update({'tools': 'crosshair, pan, reset, save, wheel_zoom'})

# _.-*-._ Callbacks _.-*-._

# Note some variable names are used in the JavaScript string
matrix_cds.callback = CustomJS(args=dict(fixation_cds=fixation_cds), code="""
       var inds = cb_obj.selected['1d'].indices;
       var d1 = cb_obj.data;
       var d2 = fixation_cds.data;
       
       d2['MappedFixationPointX'] = [[]]        
       d2['MappedFixationPointY'] = [[]]
       for (var i = 0; i < inds.length; i++) {
           d2['MappedFixationPointX'][i] = d1['MappedFixationPointX'][inds[i]]
           d2['MappedFixationPointY'][i] = d1['MappedFixationPointY'][inds[i]]
       }
       d2['MappedFixationPointX'] = [].concat.apply([], d2['MappedFixationPointX']);
       d2['MappedFixationPointY'] = [].concat.apply([], d2['MappedFixationPointY']);

       d2['MappedFixationPointX'] = d2['MappedFixationPointX'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) 
       d2['MappedFixationPointY'] = d2['MappedFixationPointY'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) 
        
       console.log(d2['MappedFixationPointX'])
       console.log(d2['MappedFixationPointY'])
       
       fixation_cds.data = d2
       fixation_cds.change.emit();
    """)


# --- called by stimulus_select
def stim_select_callback(attr, old, new, kwargs=plot_kwargs):
    # Values from widget are not exact stimuli names
    stim = get_filename(META, stim_select.value)

    image_cds.data = get_img(stim).data
    print('got_here')

    x_dim = int(META[stim]['x_dim'])
    y_dim = int(META[stim]['y_dim'])
    station_count = META[stim]['station_count']
    city = META[stim]['txt_name']

    # Grab old title, set new text
    t = matrix_plot.title
    t.text = stim_select.value + ' - (' + str(station_count) + ' stations)'

    # Retaining other settings
    color = color_select.value
    metric = METRICS.get(metric_select.value)
    matrix_cds.data = get_matrix_cds(stim, USERS, DF, color, metric).data

    # Yields unique 'xname's, preserving order
    if PRESENTING:
        order = list(unique_everseen(matrix_cds.data['xname']))
        matrix_plot.x_range.factors = order
        matrix_plot.y_range.factors = list(reversed(order))

    image_plot.x_range.start = 0
    image_plot.y_range.start = 0
    image_plot.x_range.end = x_dim
    image_plot.y_range.end = y_dim

    plot_w = x_dim + kwargs['min_border_left'] + kwargs['min_border_right']
    plot_h = y_dim + kwargs['min_border_top'] + kwargs['min_border_bottom']

    X = [item for sublist in matrix_cds.data['MappedFixationPointX'] for item in sublist]
    Y = [item for sublist in matrix_cds.data['MappedFixationPointY'] for item in sublist]

    fixation_cds.data = get_fixation_points(X, Y).data


def color_select_callback(attr, old, new):
    alpha = []
    colors = []
    color_scheme = color_select.value
    gradient = 0

    if color_scheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
        colormap = all_palettes[color_scheme][256]
        gradient = 1

    for i in range(0, len(matrix_cds.data["count"])):
        value = matrix_cds.data["count"][i]
        if gradient == 1:
            colors.append(colormap[255 - int(round(255 * value))])
            alpha.append(1.0)
        else:
            alpha.append(value)
            colors.append(color_scheme)

    matrix_cds.data["colors"] = colors
    matrix_cds.data["alphas"] = alpha


def order_select_callback(attr, old, new):
    function_name = order_select.value
    f = ORDERS.get(function_name)
    new_order = f(matrix_cds.data)

    matrix_plot.x_range.factors = list(new_order)
    matrix_plot.y_range.factors = list(reversed(new_order))


def metric_select_callback(attr, old, new):
    function_name = metric_select.value
    f = METRICS.get(function_name)

    stim = get_filename(META, stim_select.value)
    color = color_select.value

    matrix_cds.data = get_matrix_cds(stim, USERS, DF, color, f).data


def image_plot_callback(attr, old, new):
    x = fixation_cds.data['MappedFixationPointX']
    y = fixation_cds.data['MappedFixationPointY']

    print(len(fixation_cds.data['MappedFixationPointX']))
    for i in range(0, len(fixation_cds.data['MappedFixationPointX'])):
        image_plot.circle(x[i], y[i], size=15, fill_color=GAZE_COLORS[i], alpha=0.5)
        image_plot.line(x[i], y[i], line_color=GAZE_COLORS[i], alpha=0.5)


stim_select.on_change('value', stim_select_callback)
color_select.on_change('value', color_select_callback)
order_select.on_change('value', order_select_callback)
metric_select.on_change('value', metric_select_callback)
matrix_cds.on_change('selected', image_plot_callback)

# _.-*-._ Plots _.-*-._


# --- Plotting variables
plot_kwargs = dict()

# Plot borders
plot_kwargs.update({'min_border_left': 10,
                    'min_border_right': 40,
                    'min_border_top': 40,
                    'min_border_bottom': 0,
                    'border_fill_color': 'mistyrose'})

# Used to respond to window resizes (maintaining original aspect ratio)
plot_kwargs.update({'sizing_mode': 'scale_both'})

# Built-in Bokeh tools
plot_kwargs.update({'tools': 'crosshair, pan, reset, save, wheel_zoom'})

# --- Second component

# Adjacency matrix
matrix_plot = figure(title="Matrix", x_axis_location='above',
                     x_range=list(reversed(USERS)), y_range=USERS,
                     tools="hover,save,pan,wheel_zoom,reset,tap,box_select")

matrix_plot.grid.grid_line_color = None
matrix_plot.axis.axis_line_color = None
matrix_plot.axis.major_tick_line_color = None
matrix_plot.axis.major_label_text_font_size = '10pt'
matrix_plot.axis.major_label_standoff = 0
matrix_plot.axis.major_label_orientation = np.pi / 4
matrix_plot.rect('xname', 'yname', 0.9, 0.9, source=matrix_cds,
                 color='colors', alpha='alphas', line_color=None,
                 hover_line_color='black', hover_color='black')

matrix_plot.select_one(HoverTool).tooltips = [
    ('names', '@yname, @xname'),
    ('Similarity score', '@count')]

# Color bar
color_bar = figure(
    tools="box_select, crosshair", width=80, height=600, title=None,
    y_range=(0, 1),
    y_axis_label="Similarity score", toolbar_location=None)

color_bar.rect(
    'zeros', 'count', 0.5, 0.0005, name='color_bar',
    source=matrix_cds, color='colors', alpha='alphas')

unselect_rectangle = Rect(line_alpha=0, fill_alpha=0)
render = color_bar.select(name='color_bar')
render.nonselection_glyph = unselect_rectangle

crosshair = color_bar.select(type=CrosshairTool)
crosshair.dimensions = 'width'

color_bar.xgrid.grid_line_color = None
color_bar.ygrid.grid_line_color = None
color_bar.yaxis.axis_label_text_font_size = '12pt'
color_bar.xaxis.major_label_text_font_size = '0pt'
color_bar.xaxis.major_tick_line_color = None
color_bar.xaxis.minor_tick_line_color = None

image_plot = figure(plot_width=800, plot_height=800)

image_plot.image_rgba(image='image', x=0, y=0, dw='width', dh='height',
                      source=image_cds)
sizing_mode = 'stretch_both'

inputs = widgetbox(widgets, sizing_mode=sizing_mode)

right = column([image_plot])
l = row(inputs, color_bar, matrix_plot, right)

curdoc().add_root(l)
curdoc().title = 'aye'
