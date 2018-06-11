import numpy as np
from bokeh.models.widgets import Slider, Select, RadioGroup
from bokeh.plotting import figure
from bokeh.models import TextInput, ColumnDataSource, CustomJS, Rect, Title
from bokeh.models.tools import HoverTool, CrosshairTool
from bokeh.layouts import row, column, widgetbox
from bokeh.palettes import all_palettes
from bokeh.io import curdoc

from read import read_main_df, read_metadata
from sources import get_filename, get_matrix_cds, get_img, get_stim_select_options
from metrics import simple_bbox

FLASK_ARGS = curdoc().session_context.request.arguments

#  COMPONENTS
#################
# 1 # 2 2 # 3 3 #
# 1 # 2 2 # 4 4 #
#################

# _.-*-._ Default settings _.-*-._

META = read_metadata()  # Keys are names of stimuli files (stim.jpg)
DF = read_main_df()
USERS = list(DF.user.unique())

STIM = '03_Bordeaux_S1.jpg'
COLOR = 'Inferno'
METRIC = simple_bbox

# _.-*-._ Data sources _.-*-._ (sources.py)

# 1st component
stim_select_cds = get_stim_select_options(META)

# 2nd component
matrix_cds = get_matrix_cds(STIM, USERS, DF, COLOR, METRIC)

# 3rd component

# 4th component
image_cds = get_img(STIM, [0], [0])

# _.-*-._ Widgets _.-*-._

# Selecting stimulus, filter options through TextInput widget ti
stim_select = Select(options=stim_select_cds.data['options'])
text_input = TextInput(placeholder='Enter filter', title='Stimulus',
                       callback=CustomJS(args=dict(ds=stim_select_cds, s=stim_select),
                                         code="s.options = ds.data['options'].filter(i => i.includes(cb_obj.value));"))

# Select color scheme for matrix
color_select = Select(title="Color Scheme", value=COLOR,
                      options=['SteelBlue', 'Tomato', 'MediumSeaGreen', 'Inferno', 'Magma', 'Plasma', 'Viridis'])

# TODO metric_select, sorting_select, heatmap_tunes
widgets = [text_input, stim_select, color_select]


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

matrix_cds.callback = CustomJS(args=dict(source=image_cds), code="""
       var inds = cb_obj.selected['1d'].indices;
       var d1 = cb_obj.data;
       var d2 = image_cds.data;
       d2['MappedFixationPointX'] = [[]]
       d2['MappedFixationPointY'] = [[]]
       for (var i = 0; i < inds.length; i++) {
           d2['MappedFixationPointX'][[i]] = d1['MappedFixationPointX'][inds[i]]
           d2['MappedFixationPointY'][[i]] = d1['MappedFixationPointY'][inds[i]]
       }
       d2['MappedFixationPointX'] = d2['MappedFixationPointX'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) //
       d2['MappedFixationPointY'] = d2['MappedFixationPointY'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) //

       d2['MappedFixationPointX'] = [].concat.apply([], d2['MappedFixationPointX']);
       d2['MappedFixationPointY'] = [].concat.apply([], d2['MappedFixationPointY']);
       image_cds.change.emit();
    """)


# --- called by stimulus_select
def stim_select_callback(attr, old, new, kwargs=plot_kwargs):
    # Values from widget are not exact stimuli names
    stim = get_filename(META, stim_select.value)

    x_dim = int(META[stim]['x_dim'])
    y_dim = int(META[stim]['y_dim'])
    station_count = META[stim]['station_count']
    city = META[stim]['txt_name']

    # New title
    t = Title()
    t.text = stim_select.value + '- ('+ str(station_count) + 'stations)'
    matrix_plot.title = t

    # Retaining other settings
    color = color_select.value
    # TODO
    # metric = metric.select.value

    image_cds.data = get_img(stim, [0], [0]).datasource

    matrix_cds.data = get_matrix_cds(stim, USERS, DF, color, METRIC).data


    # Updating
    image_plot.x_range.start = 0
    image_plot.y_range.start = 0
    image_plot.x_range.end = x_dim
    image_plot.y_range.end = y_dim

    plot_w = x_dim + kwargs['min_border_left'] + kwargs['min_border_right']
    plot_h = y_dim + kwargs['min_border_top'] + kwargs['min_border_bottom']



def color_select_callback(attr, old, new):
    alpha = []
    color = []
    color_scheme = color_select.value
    gradient = 0

    if color_scheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
        colormap = all_palettes[color_scheme][256]
        gradient = 1

    for i in range(0, len(matrix_cds.data["count"])):
        value = matrix_cds.data["count"][i]
        if gradient == 1:
            color.append(colormap[255 - int(round(255 * value))])
            alpha.append(1.0)
        else:
            alpha.append(value)
            color.append(color_scheme)

    matrix_cds.data["colors"] = color
    matrix_cds.data["alphas"] = alpha



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
matrix_plot.axis.major_label_orientation = np.pi / 3
matrix_plot.rect('xname', 'yname', 0.9, 0.9, source=matrix_cds,
                 fill_color='colors', alpha='alphas')

matrix_plot.select_one(HoverTool).tooltips = [
    ('names', '@yname, @xname'),
    ('Similarity score', '@count')]

unselect_rectangle = Rect(line_alpha=0, fill_alpha=0)

# Color bar
color_bar = figure(
   tools="box_select, crosshair", width=80, height=600, title=None,
   y_range=(0, 1),
   y_axis_label="Similarity score", toolbar_location=None)

color_bar.rect(
   'zeros', 'count', 0.5, 0.0005, name='color_bar',
   source=matrix_cds, color='colors', alpha='alphas')

render = color_bar.select(name='color_bar')
render.nonselection_glyph = unselect_rectangle

crosshair = color_bar.select(type=CrosshairTool)
crosshair.dimensions = 'width'

color_bar.yaxis.axis_label_text_font_size = '12pt'
color_bar.xaxis.major_label_text_font_size = '0pt'

image_plot = figure(plot_width=800, plot_height=800)

image_plot.image_rgba(image='image', x=0, y=0, dw='width', dh='height',
                      source=image_cds)


# _.-*-._ Callbacks _.-*-._


stim_select.on_change('value', stim_select_callback)
color_select.on_change('value', color_select_callback)

sizing_mode = 'fixed'

inputs = widgetbox(widgets, sizing_mode=sizing_mode)

right = column([image_plot])
l = row(inputs, color_bar, matrix_plot, right)

curdoc().add_root(l)
curdoc().title = 'aye'

# Set up layouts and add to document
# widgets = widgetbox(city_select, stimulus_select)



#    layout = row(inputs, plot1, plot2)
#    curdoc().add_root(layout)
#    curdoc().title = str(url_params['layout'])
