import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure, output_file
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import all_palettes


from boundingbox import *

#flask magic
url_params = curdoc().session_context.request.arguments

user_list = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14', 'p15', 'p16',
             'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p25', 'p26', 'p27', 'p28', 'p29', 'p30', 'p31',
             'p32', 'p33', 'p34', 'p35', 'p36', 'p37', 'p38', 'p39', 'p40']


#setup empty ColumnDataSource
source = ColumnDataSource(data=dict(
    xname=[],
    yname=[],
    alphas=[],
    colors=[],
))

#initiate plot
p = figure(title="Bounding box",
           x_axis_location="above", tools="hover,save",
           x_range=list(reversed(user_list)), y_range=list(user_list))

#set some plot parameters
p.plot_width = 800
p.plot_height = 800
p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = np.pi/3

#plotting the actual rectangles
p.rect('xname', 'yname', 0.9, 0.9, source=source, color='colors',
       alpha='alphas', line_color=None,
       hover_line_color='black', hover_color='black')

#Configure Hover tool
p.select_one(HoverTool).tooltips = [
    ('names', '@yname, @xname'),
    ('Similarity score', '@count')]

#set up widgets lists
cities = list(stimuli_names)
colorSchemes = ['SteelBlue', 'Tomato', 'MediumSeaGreen', 'Inferno', 'Magma', 'Plasma', 'Viridis']

#Set up widgets
city_select = Select(title="City", options=cities)
colorScheme_select = Select(title="Color Scheme", value = "SteelBlue", options=colorSchemes)

#Set up callbacks
def update_title(attrname, old, new):
    p.title.text = city_select.value

#updates title of plot
city_select.on_change('value', update_title)

def update_data(attrname, old, new):
    
    # Get the current slider values
    city = city_select.value
    colorScheme = colorScheme_select.value

    # Generate the new adjacency matrix
    alpha = []
    color = []
    xname = []
    yname = []
    count = []

    gradient = 0

    if colorScheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
        colormap = all_palettes[colorScheme][256]
        gradient = 1

    #retrieve similarity score from dictionary and add color
    for i in range(0, len(user_list)):
        for j in range(0, len(user_list)):
            value = adjacency[city][user_list[i]].get(user_list[j], 'Key not present')
            if value == 'Key not present':
                continue
            xname.append(user_list[i])
            yname.append(user_list[j])
            count.append(value)

            if gradient == 1:
                color.append(colormap[255 - int(round(255 * value))])
                alpha.append(1.0)
            else:
                alpha.append(value)
                color.append(colorScheme)




    #swap out the old data for the new data
    source.data = dict(
        xname=xname,
        yname=yname,
        alphas=alpha,
        colors=color,
        count=count,
    )

    #update the x and y labels
    p.x_range.factors = list(reversed(np.unique(xname)))
    p.y_range.factors = list(np.unique(yname))

    #log to console
    print('Updated Plot')


#updates plot data on_change
city_select.on_change('value', update_data)
colorScheme_select.on_change('value', update_data)

# Set up layouts and add to document
inputs = widgetbox([city_select, colorScheme_select])

#Flask/Bokeh magic
curdoc().add_root(row(inputs, p))
