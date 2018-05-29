from bokeh.models.widgets import Slider, Select, RadioGroup
from bokeh.plotting import figure
from bokeh.models import TextInput, ColumnDataSource, CustomJS
# ---
from read import read_main_df, read_metadata
from sources import get_img, get_city_select_options, get_filename

meta = read_metadata()
cities_meta = get_city_select_options(meta)
df = read_main_df()
tokyo_source = get_img('Tokyo_S1.jpg')
bordeaux_source = get_img('Bordeaux_S2.jpg')


def test():

    # _.-*-._ Setting up data sources _.-*-._

    meta = read_metadata()
    df = read_main_df()
    tokyo_source = get_img('Tokyo_S1.jpg')
    bordeaux_source = get_img('Bordeaux_S2.jpg')

    stimulus_select_ds = get_city_select_options(meta)

    # --- Traces

    plot2 = figure(x_range=(0, 10), y_range=(0, 10))
    plot2.image_rgba(image='image', x=0, y=0, dw=10, dh=10,
                     source=bordeaux_source)

    # _.-*-._ Widgets _.-*-._

    # Selecting stimulus, filter options through ti
    stimulus_select = Select(options=stimulus_select_ds.data['options'])
    ti = TextInput(placeholder='Enter filter', title='Stimulus',
                   callback=CustomJS(args=dict(ds=stimulus_select_ds, s=stimulus_select),
                                     code="s.options = ds.data['options'].filter(i => i.includes(cb_obj.value));"))

    color_scheme = Select(title="Color Scheme", value="----", options=[
        "Inferno"])

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

    # --- called by city_select

    def plot_new_stimuli(attrname, old, new, kwargs=plot_kwargs):
        # TODO also update background map and 'main' source
        print(stimulus_select.value)
        # Retrieve metadata of the stimulus
        f = get_filename(meta, stimulus_select.value)

        x_dim = int(meta[f]['x_dim'])
        y_dim = int(meta[f]['y_dim'])

        bordeaux_source.data = tokyo_source.data

        stimulus_meta = meta[f]

        plot_w = x_dim + kwargs['min_border_left'] + kwargs['min_border_right']
        plot_h = y_dim + kwargs['min_border_top'] + kwargs['min_border_bottom']

        city = stimulus_meta['txt_name']
        station_count = stimulus_meta['station_count']

        """
        plot_colour = figure(title=city,
                     x_range=(0, x_dim),
                     y_range=(0, y_dim),
                     # plot_width=plot_w,
                     # plot_height=plot_h,
                     **kwargs)

        plot_colour.image_rgba(image='image', x=0, y=0, dw=10, dh=10,
                               source=tokyo_source)
        """

    stimulus_select.on_change('value', plot_new_stimuli)

    # Set up layouts and add to document
    # widgets = widgetbox(city_select, stimulus_select)

    return ti, stimulus_select, \
            color_scheme, \
            plot2

#    layout = row(inputs, plot1, plot2)
#    curdoc().add_root(layout)
#    curdoc().title = str(url_params['layout'])
