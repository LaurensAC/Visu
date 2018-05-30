from bokeh.models.widgets import Slider, Select, RadioGroup
from bokeh.plotting import figure
from bokeh.models import TextInput, ColumnDataSource, CustomJS
from bokeh.layouts import row, column, widgetbox
from bokeh.io import curdoc
# ---
from read import read_main_df, read_metadata
from sources import get_img, get_city_select_options, get_filename
# _.-*-._ Data sources _.-*-._

#curdoc().session_context.request.arguments

meta = read_metadata()
df = read_main_df()

image_source = get_img('Bordeaux_S2.jpg')

stimulus_select_ds = get_city_select_options(meta)

# _.-*-._ Widgets _.-*-._

# Selecting stimulus, filter options through ti
stimulus_select = Select(options=stimulus_select_ds.data['options'])
ti = TextInput(placeholder='Enter filter', title='Stimulus',
               callback=CustomJS(args=dict(ds=stimulus_select_ds, s=stimulus_select),
                                 code="s.options = ds.data['options'].filter(i => i.includes(cb_obj.value));"))
# Select color scheme
color_scheme = Select(title="Color Scheme", value="----", options=[
    "Inferno"])

# TODO metric_select, sorting_select,
widgets = [ti, stimulus_select, color_scheme]

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

box_4 = figure(plot_width=800, plot_height=800)

box_4.image_rgba(image='image', x=0, y=0, dw='xw', dh='yw',
                 source=image_source)


# _.-*-._ Callbacks _.-*-._

# --- called by stimulus_select
def plot_new_stimuli(attrname, old, new, kwargs=plot_kwargs):
    f = get_filename(meta, stimulus_select.value)

    x_dim = int(meta[f]['x_dim'])
    y_dim = int(meta[f]['y_dim'])

    image_source.data = get_img(f).data

    stimulus_meta = meta[f]

    box_4.x_range.start = 0
    box_4.y_range.start = 0
    box_4.x_range.end = x_dim
    box_4.y_range.end = y_dim

    plot_w = x_dim + kwargs['min_border_left'] + kwargs['min_border_right']
    plot_h = y_dim + kwargs['min_border_top'] + kwargs['min_border_bottom']

    city = stimulus_meta['txt_name']
    station_count = stimulus_meta['station_count']



stimulus_select.on_change('value', plot_new_stimuli)

sizing_mode = 'fixed'
inputs = widgetbox(widgets, sizing_mode=sizing_mode)

right = column([box_4])
l = row(inputs, right)

curdoc().add_root(l)
curdoc().title = 'aye'

# Set up layouts and add to document
# widgets = widgetbox(city_select, stimulus_select)



#    layout = row(inputs, plot1, plot2)
#    curdoc().add_root(layout)
#    curdoc().title = str(url_params['layout'])
