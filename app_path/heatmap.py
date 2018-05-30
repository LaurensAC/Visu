from read import *

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

#
# class Heatmap:
#
#
#     def __init__(self, stimulus, resolution_resize=1, count_duration=False, smoothing_range=0, weight_centre=1):
#         self.stimulus = stimulus
#         self.resolution_resize = resolution_resize
#         self.count_duration = count_duration
#         self.smoothing_range = smoothing_range
#         self.weight_centre = weight_centre
#
#         # df = pd.read_csv('up.csv', sep='\t', index_col=0)
#         # # df = read_main_df()
#         #
#         # run_heatmap(stimulus, resolution_resize, count_duration, smoothing_range, weight_centre)
#         self.test()
#
#     def test(self):
#         print(self.resolution_resize)
#
#

"""
og_df: original dataframe with alle data
city_name: city name as string
rounds_coords_to: divide all coordinates by this number to have less unique coordinate pairs 
count_duration: True if fixation duration is important, False if only counting number of fixations
smoothing_range: the value of a pixel(block) is the the mean value of the submatrix containing this many pixel(blocks) 
                to every side of the concerning pixel(block)
weight_centre: the value of the centre pixel(block) is multiplied by this number. Only makes sense when smoothing_range > 0 
"""


def run_heatmap(stimulus, resolution_resize=1, count_duration=False, smoothing_range=0, weight_centre=1):
    # df = pd.read_csv('up.csv', sep='\t', index_col=0)
    df = read_main_df()
    df = df[(df['StimuliName'] == stimulus) & (df['FixationOOB'] == False)]
    df['MappedFixationPointX'] = df['MappedFixationPointX'] / resolution_resize
    df['MappedFixationPointY'] = df['MappedFixationPointY'] / resolution_resize

    stimuli_meta = read_metadata()
    xdim_og = int(stimuli_meta[stimulus]['x_dim'])
    ydim_og = int(stimuli_meta[stimulus]['y_dim'])
    xdim = int(xdim_og / resolution_resize) + 1
    ydim = int(ydim_og / resolution_resize) + 1

    # create matrix with fixation counts. smoothing may be applied
    heat_matrix = create_heat_matrix(df, xdim, ydim, count_duration)
    if smoothing_range > 0:
        heat_matrix = apply_smoothing(heat_matrix, smoothing_range, weight_centre)

    heat_counts_df = create_heat_df(heat_matrix)
    show_heatmap(heat_counts_df, xdim_og, ydim_og)


# TODO: write update functions for each of the parameters
# def subset_dataframe_by_stimulus(df, stimulus):
#     data['MappedFixationPointX'] = data['MappedFixationPointX'] /

# def set_resolution(resolution_resize):
#

# def toggle_duration(count_duration):


def create_heat_df(heat_matrix):
    heat_dict = {'x': [], 'y': [], 'heat': []}  #

    for i in range(len(heat_matrix)):
        for j in range(len(heat_matrix[i])):
            heat_dict['x'].append(j)
            heat_dict['y'].append(i)
            heat_dict['heat'].append(heat_matrix[i][j])
    print("dataframe completed")
    return pd.DataFrame(data=heat_dict, columns=['x', 'y', 'heat'])


def create_heat_matrix(df, xdim, ydim, count_duration=False):
    # initialize empty matrix
    result = np.zeros((int(ydim), int(xdim)))

    if count_duration:  # sum over the fixation durations for every pixel on the map
        for row in df.iterrows():
            x = int(row[1]['MappedFixationPointX'])
            y = int(row[1]['MappedFixationPointY'])
            result[y][x] += row[1]['FixationDuration']
    else:  # count of the number of fixations for every pixel on the map
        for row in df.iterrows():
            x = int(row[1]['MappedFixationPointX'])
            y = int(row[1]['MappedFixationPointY'])
            result[y][x] += 1
    print('matrix completed')
    return result


def apply_smoothing(matrix, smoothing_range, weight_centre):
    smoothed_matrix = []
    for i in range(len(matrix)):  # y
        new_row = []
        for j in range(len(matrix[i])):  # x
            matrix_subset = subset_matrix(matrix, j, i, smoothing_range)

            # calculate mean value of the elements in the submatrix, giving extra weight to the centre
            N = matrix_subset.shape[0] * matrix_subset.shape[1]
            sum_matrix = matrix_subset.sum()  # including the centre value
            sum_matrix += (weight_centre - 1) * matrix[i][
                j]  # add extra weight to the centre, excluding the one we've already added before

            new_row.append(
                sum_matrix / (N - 1 + weight_centre))  # divide by N including the extra additions of weight_centre
        smoothed_matrix.append(new_row)
    print('smoothing completed')
    return smoothed_matrix


def subset_matrix(matrix, x, y, smoothing_range):
    x_min = max(x - smoothing_range, 0)
    x_max = min(x + smoothing_range, len(matrix[y]))
    y_min = max(y - smoothing_range, 0)
    y_max = min(y + smoothing_range, len(matrix))
    return matrix[y_min: y_max, x_min: x_max]


def show_heatmap(df, xdim, ydim):
    # this is the colormap from the original NYTimes plot
    colors = ["#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027"]
    max_heat = df.heat.max()
    mapper = LinearColorMapper(palette=colors, low=0, high=max_heat, nan_color=None)
    df['alphas'] = [0 if x < max_heat / len(colors) else 1 for x in df['heat']]

    source = ColumnDataSource(df)

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    p = figure(title='{} count'.format(stimulus),
               # x_range=(0, xdim), y_range=(0, ydim),
               x_axis_location="above",
               plot_width=int(xdim*0.7), plot_height=int(ydim*0.7),
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
           alpha='alphas',
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


def extract_city_name(stimuli_name):
    return stimuli_name.rsplit('_', 1)[0].split('_', 1)[-1]



##############################
### ------> INPUT <------- ###
##############################
stimulus = '11_Bologna_S1.jpg'
run_heatmap(stimulus=stimulus,
            resolution_resize=2,
            count_duration=False,
            smoothing_range=10,
            weight_centre=4)

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

'''
    def RdYlGn3(self):  return ["#91cf60", "#ffffbf", "#fc8d59"]
    def RdYlGn4(self):  return ["#1a9641", "#a6d96a", "#fdae61", "#d7191c"]
    def RdYlGn5(self):  return ["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c"]
    def RdYlGn6(self):  return ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027"]
    def RdYlGn7(self):  return ["#1a9850", "#91cf60", "#d9ef8b", "#ffffbf", "#fee08b", "#fc8d59", "#d73027"]
    def RdYlGn8(self):  return ["#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#fee08b", "#fdae61", "#f46d43", "#d73027"]
    def RdYlGn9(self):  return ["#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027"]
    def RdYlGn10(self): return ["#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"]
    def RdYlGn11(self): return ["#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"]
white: #FFFFFF
'''