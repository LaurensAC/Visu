import numpy as np
import json
import numpy as np
from PIL import Image
from utils import *
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure


# Kwargs passed by flask
url_params = curdoc().session_context.request.arguments

# Open image, and make sure it's RGB*A*
tokyo_img = Image.open('Tokyo.jpg').convert('RGBA')
xdim, ydim = tokyo_img.size
print("Dimensions: ({xdim}, {ydim})".format(**locals()))
# Create an array representation for the image `img`, and an 8-bit "4
# layer/RGBA" version of it `view`.
img = np.empty((ydim, xdim), dtype=np.uint32)
view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
# Copy the RGBA image into view, flipping it so it comes right-side up
# with a lower-left origin
view[:,:,:] = np.flipud(np.asarray(tokyo_img))

# Display the 32-bit RGBA image
dim = max(xdim, ydim)


# _.-*-._ Setting up data sources _.-*-._

# --- Metadata
with open('stimuli_meta.json', 'r') as f:
    metadata = json.load(f)

# Filenames are used to select a certain stimuli (see stimulus_select widget)
stimuli = list(metadata.keys())

# --- Metadata with city names as keys
cities_meta = dict()
for stimulus, values in metadata.items():
    city_name = values['txt_name']
    if city_name in cities_meta.keys():
        cities_meta[city_name].update({stimulus: values})
    else:
        cities_meta[city_name] = dict()
        cities_meta[city_name].update({stimulus: values})

# Ordered list of cities, used to select groups of stimuli
cities = list(cities_meta.keys())

# --- Traces

# Path to csv
path = find_path('up.csv')
# find_encoding(path) returns ISO-8859-1
encoding = 'ISO-8859-1'

# Set up data
N = 2000
x = np.linspace(0, 4 * np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))

# Set up plots

plot1 = figure(title="my sine wave",
               tools="crosshair,pan,reset,save,wheel_zoom",
               id='left_plot', sizing_mode="scale_both")

plot1.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

plot2 = figure(title="my sine wave",
               tools="crosshair,pan,reset,save,wheel_zoom",
               id='right_plot', sizing_mode="scale_both")

plots = [plot1, plot2]

"""
The code below will add 'widgets' from which we can access values.

To get interactive feedback from the widgets, run bokeh in server mode:

    In your terminal:
    bokeh serve ./bokeh_plots.py --allow-websocket-origin=127.0.0.1:5000
    
    Note './bokeh_plots.py' is the <path to this script>
    
    
We define a widget's interaction by setting its 'on_change'
>>> widget.on_change('value', function_to_call)
and implementing the function this widget will call. 

Finally add the widgets/plots to the 'Document'
>>> curdoc().add_root(widget)
    
    (Document instances collect Bokeh models (plots, layouts, widgets, etc.) 
    so that they may be reflected into JavaScript client runtime)
    
"""

# _.-*-._ Widgets _.-*-._

city_select = Select(title="City", value="---", options=sorted(cities))
stimulus_select = Select(title="Stimulus", value="---", options=[])

offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0)
phase = Slider(title="phase", value=0.0, start=0.0, end=2 * np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1)

# _.-*-._ Some constants _.-*-._

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


# Axes
# plot_kwargs.update({})

# --- called by city_select


def update_stimuli_widget(attrname, old, new):
    """
    Updates stimulus_select widget to display stimuli of selected city
    """
    # Get city metadata
    stimuli = cities_meta[city_select.value]
    # Update stimulus_select widget
    stimulus_select.options = list(stimuli.keys())


city_select.on_change('value', update_stimuli_widget)


# --- called by stimulus_select

def plot_new_stimuli(attrname, old, new, kwargs=plot_kwargs):
    # TODO also update background map and 'main' source

    # Retrieve metadata of the stimulus
    stimulus_meta = metadata[stimulus_select.value]

    x_dim = int(stimulus_meta['x_dim'])
    y_dim = int(stimulus_meta['y_dim'])

    plot_w = x_dim + kwargs['min_border_left'] + kwargs['min_border_right']
    plot_h = y_dim + kwargs['min_border_top'] + kwargs['min_border_bottom']

    city = stimulus_meta['txt_name']
    station_count = stimulus_meta['station_count']

    plot_colour = figure(title=city,
                         x_range=(0, x_dim),
                         y_range=(0, y_dim),
                         plot_width=plot_w,
                         plot_height=plot_h,
                         **kwargs)

    plot_colour.image_rgba(image=[img], x=0, y=0, dw=xdim, dh=ydim)

    plot_grey = figure(title=str(city + " grey"),
                       x_range=(0, x_dim),
                       y_range=(0, y_dim),
                       plot_width=plot_w,
                       plot_height=plot_h,
                       **kwargs)

    curdoc().clear()
    curdoc().add_root(row(inputs, plot_colour, plot_grey))


stimulus_select.on_change('value', plot_new_stimuli)


def update_data(attrname, old, new):
    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4 * np.pi, N)
    y = a * np.sin(k * x + w) + b

    source.data = dict(x=x, y=y)


for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = widgetbox(city_select, stimulus_select,
                   offset, amplitude, phase, freq)
layout = row(inputs, plot1, plot2)
curdoc().add_root(layout)
curdoc().title = str(url_params['layout'])
