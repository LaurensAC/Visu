from sys import getsizeof

# from pre import *

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
import json


def run_heatmap(city_name, resolution_resize=10):
    read_main_df(city_name)


def preprocess_dataframe():

# TODO
def set_resolution(resolution_resize):


def show_heatmap(stimulus):
    df = pd.read_csv("up.csv")
    with open("stimuli_meta.json", 'r') as f:
        stimuli_meta = json.load(f)

    # key: city name, value: (x,y) coordinates
    map_sizes = {extractCityName(stim): (stimuli_meta[stim]['x_dim'], stimuli_meta[stim]['y_dim'])
                 for stim in df['StimuliName'].unique()}

    """
    og_df: original dataframe with alle data
    city_name: city name as string
    rounds_coords_to: divide all coordinates by this number to have less unique coordinate pairs 
    count_duration: True if fixation duration is important, False if only counting number of fixations
    smoothing_range: the value of a pixel(block) is the the mean value of the submatrix containing this many pixel(blocks) 
                    to every side of the concerning pixel(block)
    weight_centre: the value of the centre pixel(block) is multiplied by this number. Only makes sense when smoothing_range > 0 
    """
    heatCountsDf = create_heat_df(og_df=df,
                                  city_name=stimulus,
                                  round_coords_to=100,
                                  count_duration=False,
                                  smoothing_range=5,
                                  weight_centre=4)

    # this is the colormap from the original NYTimes plot
    colors = ["#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027"]
    mapper = LinearColorMapper(palette=colors, low=0, high=heatCountsDf.heat.max())

    source = ColumnDataSource(heatCountsDf)

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    xdim = map_sizes[stimulus][0]
    ydim = map_sizes[stimulus][1]
    p = figure(title='{} count'.format(stimulus),
               # x_range=(0, xdim), y_range=(0, ydim),
               x_axis_location="above",
               # plot_width=xdim, plot_height=ydim,
               tools=TOOLS)

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(x="x", y="y",
           width=1, height=1,
           source=source,
           fill_color={'field': 'heat', 'transform': mapper},
           line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d%%"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    # hover tool
    p.select_one(HoverTool).tooltips = [
        ('x, y', '@x, @y'),
        ('#', '@heat%'),
    ]

    show(p)  # show the plot


def create_heat_df(og_df, city_name, round_coords_to=1, count_duration=False, smoothing_range=0, weight_centre=1):
    # create matrix with fixation counts. smoothing may be applied
    if smoothing_range <= 0:
        fixation_counts = create_heat_matrix(og_df, city_name, count_duration, round_coords_to)
    else:  # smoothing_range > 0
        fixation_counts = create_heat_matrix(og_df, city_name, count_duration, round_coords_to)
        fixation_counts = applySmoothing(fixation_counts, smoothing_range, weight_centre)

    heat_dict = {'x': [], 'y': [], 'heat': []}  #

    for i in range(len(fixation_counts)):
        for j in range(len(fixation_counts[i])):
            heat_dict['x'].append(j)
            heat_dict['y'].append(i)
            heat_dict['heat'].append(fixation_counts[i][j])
    print("dataframe completed")
    return pd.DataFrame(data=heat_dict, columns=['x', 'y', 'heat'])


def create_heat_matrix(og_df, city_name, count_duration=False, round_coords_to=1):
    # initialize empty matrix
    xdim_og = map_sizes[city_name][0]
    ydim_og = map_sizes[city_name][1]
    xdim = int(xdim_og / round_coords_to) + 1
    ydim = int(ydim_og / round_coords_to) + 1
    result = np.zeros((int(ydim), int(xdim)))

    # key: city name, value: list of strings from StimuliName that contain the city name
    map_names = {extractCityName(stim): [x for x in og_df['StimuliName'].unique() if extractCityName(stim) in x]
                 for stim in og_df['StimuliName'].unique()}

    # select rows from the original dataframe
    df_city = og_df[(og_df['StimuliName'].isin(map_names[city_name])) & (og_df['FixationOOB'] == False)]

    if count_duration:  # sum over the fixation durations for every pixel on the map
        for row in df_city.iterrows():
            x = int(row[1]['MappedFixationPointX'] / round_coords_to)
            y = int(row[1]['MappedFixationPointY'] / round_coords_to)
            result[y][x] += row[1]['FixationDuration']
    else:  # count of the number of fixations for every pixel on the map
        for row in df_city.iterrows():
            x = int(row[1]['MappedFixationPointX'] / round_coords_to)
            y = int(row[1]['MappedFixationPointY'] / round_coords_to)
            result[y][x] += 1
    print('matrix completed')
    return result


def applySmoothing(matrix, smoothing_range, weight_centre):
    smoothed_matrix = []
    print('total length:', len(matrix))
    for i in range(len(matrix)):  # y
        if i % 100 == 0:
            print(i, end=' ')
        new_row = []
        for j in range(len(matrix[i])):  # x
            matrix_subset = subsetMatrix(matrix, j, i, smoothing_range)

            # calculate mean value of the elements in the submatrix, giving extra weight to the centre
            N = matrix_subset.shape[0] * matrix_subset.shape[1]
            sum_matrix = matrix_subset.sum()  # including the centre value
            sum_matrix += (weight_centre - 1) * matrix[i][j]  # add extra weight to the centre, excluding the one we've already added before

            new_row.append(sum_matrix / (N - 1 + weight_centre))  # divide by N including the extra additions of weight_centre
        smoothed_matrix.append(new_row)
    print('\nsmoothing completed')
    return smoothed_matrix


def subsetMatrix(matrix, x, y, smoothing_range):
    x_min = max(x - smoothing_range, 0)
    x_max = min(x + smoothing_range, len(matrix[y]))
    y_min = max(y - smoothing_range, 0)
    y_max = min(y + smoothing_range, len(matrix))
    return matrix[y_min: y_max, x_min: x_max]


def print_vars(var_dict):
    variables = ["{}: {}".format(key, getsizeof(value)) for key, value in var_dict.items()]
    for x in variables:
        print(x)
    sizes = [getsizeof(x) for x in var_dict.values()]
    print("total space: {}".format(sum(sizes)))


# useful (global) dictionaries
def extractCityName(stimuli_name):
    return stimuli_name.rsplit('_', 1)[0].split('_', 1)[-1]


stimulus = '01_Antwerpen_S2.jpg'
show_heatmap(stimulus)




'''
# Add up all fixation durations each time someone looks at a spot
heatDurationsDf = create_heat_df(og_df=df,
                                city_name=cityName,
                                round_coords_to=1,
                                count_duration=True,
                                smoothing_range=5,
                                weight_centre=4)
show_heatmap(heatDurationsDf, '{} duration'.format(cityName))

# mean fixation duration per look
heatAvgDf = heatDurationsDf.copy()
heatAvgDf['heat'] = [heatDurationsDf['heat'][i] / heatCountsDf['heat'][i]
                     if heatCountsDf['heat'][i] > 0 else 0
                     for i in range(len(heatDurationsDf['heat']))]
show_heatmap(heatAvgDf, '{} average'.format(cityName))
'''