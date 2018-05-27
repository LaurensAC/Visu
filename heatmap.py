from pre import *

from math import pi
import pandas as pd
import numpy as np

from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
)
from bokeh.plotting import figure


# setup data
def create_heat_matrix(og_df, city, count_duration):
    # initialize empty matrix
    xdim = stimuli_meta[city]['x_dim']
    ydim = stimuli_meta[city]['y_dim']
    result = np.zeros((int(ydim), int(xdim)))

    # select rows from the original dataframe
    df_city = og_df[(og_df['StimuliName'] == city) & (og_df['FixationOOB'] == False)]

    if count_duration:  # sum over the fixation durations for every pixel on the map
        for row in df_city.iterrows():
            x = row[1]['MappedFixationPointX']
            y = row[1]['MappedFixationPointY']
            result[y][x] += row[1]['FixationDuration']
    else:  # count of the number of fixations for every pixel on the map
        for row in df_city.iterrows():
            x = row[1]['MappedFixationPointX']
            y = row[1]['MappedFixationPointY']
            result[y][x] += 1
    return result


def create_heat_df(og_df, city, count_duration):
    fixation_counts = create_heat_matrix(og_df, city, count_duration)
    heat_dict = {'x': [], 'y': [], 'heat': []}  #

    for i in range(len(fixation_counts)):
        for j in range(len(fixation_counts[i])):
            heat_dict['x'].append(j)
            heat_dict['y'].append(i)
            heat_dict['heat'].append(fixation_counts[i][j])
    return pd.DataFrame(data=heat_dict, columns=['x', 'y', 'heat'])


def show_heatmap(heat_df, title):
    # this is the colormap from the original NYTimes plot
    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    mapper = LinearColorMapper(palette=colors, low=0, high=heat_df.heat.max())

    source = ColumnDataSource(heat_df)

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    p = figure(title=title,
               x_range=range(len(df['x'])), y_range=range(len(df['y'])),
               x_axis_location="above", plot_width=len(df['x']), plot_height=len(df['y']),
               tools=TOOLS, toolbar_location='below')

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(x="x", y="y", width=1, height=1,
           source=source,
           fill_color={'field': 'heat', 'transform': mapper},
           line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d%%"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    p.select_one(HoverTool).tooltips = [
        ('date', '@Month @Year'),
        ('rate', '@rate%'),
    ]

    show(p)  # show the plot


# -----
city = "20_Paris_S1.jpg"

# only count the number of times people look at a spot
countDuration = False
heatCountsDf = create_heat_df(df, city, countDuration)
show_heatmap(heatCountsDf, city + ' count')

'''
# Add up all fixation durations each time someone looks at a spot
countDuration = True
heatDurationsDf = heat_df(df, city, countDuration)

# mean fixation duration per look
heatAvgDf = heatDurationsDf.copy()
heatAvgDf['heat'] = [heatDurationsDf['heat'][i] / heatCountsDf['heat'][i]
                     if heatCountsDf['heat'][i] > 0 else 0
                     for i in range(len(heatDurationsDf['heat']))]
'''

'''
EXAMPLE CODE

from math import pi
import pandas as pd

from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
)
from bokeh.plotting import figure
from bokeh.sampledata.unemployment1948 import data

data['Year'] = data['Year'].astype(str)
data = data.set_index('Year')
data.drop('Annual', axis=1, inplace=True)
data.columns.name = 'Month'

years = list(data.index)
months = list(data.columns)

# reshape to 1D array or rates with a month and year for each row.
df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()

# this is the colormap from the original NYTimes plot
colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())

source = ColumnDataSource(df)

TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

p = figure(title="US Unemployment ({0} - {1})".format(years[0], years[-1]),
           x_range=years, y_range=list(reversed(months)),
           x_axis_location="above", plot_width=900, plot_height=400,
           tools=TOOLS, toolbar_location='below')

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "5pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = pi / 3

p.rect(x="Year", y="Month", width=1, height=1,
       source=source,
       fill_color={'field': 'rate', 'transform': mapper},
       line_color=None)

color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%d%%"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p.add_layout(color_bar, 'right')

p.select_one(HoverTool).tooltips = [
     ('date', '@Month @Year'),
     ('rate', '@rate%'),
]

show(p)      # show the plot
'''
