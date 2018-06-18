import numpy as np
from PIL import Image
from bokeh.models import Range1d, ColumnDataSource as Cds
from bokeh.palettes import all_palettes

from utils import find_path, track, strack

# Use this module to construct new data at runtime ('on the go')


@strack
def get_img(stimulus):
    """
    Cds for fourth component given a :param: stimulus (file name)
    """
    # Loading with PIL
    raw_img = Image.open(find_path(stimulus)).convert('RGBA')
    # Its dimensions
    xdim, ydim = raw_img.size
    # Its array representation, 8-bit
    img = np.empty((ydim, xdim), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
    # Copy the RGBA image into view, flipping it upside down
    # with a lower-left origin
    view[:, :, :] = np.flipud(np.asarray(raw_img))

    return Cds({'image': [img],
                'width': [xdim],
                'height': [ydim],
                })

@strack
def get_fixation_points(x, y, duration):
    return Cds({'MappedFixationPointX': x,
                'MappedFixationPointY': y,
                'FixationDuration': duration
                })

@strack
def get_stim_select_options(meta):
    """
    Cds for first component given the :param: metadata (a loaded meta.json)
    """
    options = list()
    for filename, values in meta.items():
        options.append(values['widget_name'])
    return Cds(data=dict(options=options))


# Get a filename given a selected option
@strack
def get_filename(meta, option):
    for f, values in meta.items():
        if values['widget_name'] == option:
            return f
    return NotImplementedError


@strack
def get_matrix_cds(stim, users, df, color_scheme, metric):


    # Generate the new adjacency matrix
    alpha = []
    color = []
    xname = []
    yname = []
    count = []
    MappedFixationPointY = []
    MappedFixationPointX = []
    duration = []

    temp = df[(df['StimuliName'] == stim)]

    gradient = 0

    if color_scheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
        colormap = all_palettes[color_scheme][256]
        gradient = 1

    adjacency = metric(stim, users, df)

    # retrieve similarity score from dictionary and add color
    for i in range(0, len(users)):
        for j in range(0, len(users)):
            value = adjacency[stim][users[i]].get(users[j],
                                                      'Key not present')
            if isinstance(value, str):
                continue

            assert value <= 1
            assert value >= 0

            xname.append(users[i])
            yname.append(users[j])
            count.append(value)

            MappedFixationPointX.append([temp[temp['user'] == users[i]]['MappedFixationPointX'],
                                        temp[temp['user'] == users[j]]['MappedFixationPointX']])
            MappedFixationPointY.append([temp[temp['user'] == users[i]]['MappedFixationPointY'],
                                        temp[temp['user'] == users[j]]['MappedFixationPointY']])

            duration.append([temp[temp['user'] == users[i]]['FixationDuration'],
                                         temp[temp['user'] == users[j]]['FixationDuration']])

            if gradient == 1:
                color.append(colormap[255 - int(round(255 * value))])
                alpha.append(1.0)
            else:
                alpha.append(value)
                color.append(color_scheme)

    zeros = np.zeros(pow(len(np.unique(xname)), 2))

    # swap out the old data for the new data
    return Cds(data=dict(
        xname=xname,
        yname=yname,
        alphas=alpha,
        colors=color,
        count=count,
        zeros=zeros,
        MappedFixationPointY=MappedFixationPointY,
        MappedFixationPointX=MappedFixationPointX,
        FixationDuration=duration
    ))


