from PIL import Image
import numpy as np
from bokeh.models import ColumnDataSource
# ---
from utils import find_path, track

# Use this module to construct ColumnDataSources (in memory)


def get_img(stimulus):
    # Loading with PIL
    raw_img = Image.open(find_path(stimulus)).convert('RGBA')
    # Its dimensions
    xdim, ydim = raw_img.size
    # Its array representation, 8-bit
    img = np.empty((ydim, xdim), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
    # Copy the RGBA image into view, flipping it so it comes right-side up
    # with a lower-left origin
    view[:,:,:] = np.flipud(np.asarray(raw_img))

    return ColumnDataSource({'image': [img], 'xw': [xdim], 'yw': [ydim]})


def get_city_select_options(meta):
    options = list()
    for filename, values in meta.items():
        options.append(values['widget_name'])
    return ColumnDataSource(data=dict(options=options))


# Get a filename given a selected option
def get_filename(meta, option):
    for f, values in meta.items():
        if values['widget_name'] == option:
            return f
    return NotImplementedError


@track
def scanpaths_dict(stim, users, df):

    # dictionary to store x/y max/min values
    bounding = {}
    # dictionary to store similarity scores
    adjacency = {}

    bounding[stim] = {}
    adjacency[stim] = {}

    for user in users:
        adjacency[stim][user] = {}
        temp = df[(df['StimuliName'] == stim) & (df[
                                                     'user'] == user)]  # create small temporary dataset containing the entire scanpath of an user
        bounding[stim][user] = {'x_max': temp['MappedFixationPointX'].max(),
                                'y_max': temp['MappedFixationPointY'].max(),
                                'x_min': temp['MappedFixationPointX'].min(),
                                'y_min': temp['MappedFixationPointY'].min(), }

    counter = 0 #
    for i in users:
        for j in users[counter:len(users)]:
            if np.isnan(bounding[stim][i]['x_max']) or np.isnan(bounding[stim][j]['x_max']):
                continue
            A = abs(bounding[stim][i]['x_max'] - bounding[stim][i]['x_min']) *\
                abs(bounding[stim][i]['y_max'] - bounding[stim][i]['y_min'])
            B = abs(bounding[stim][j]['x_max'] - bounding[stim][j]['x_min']) *\
                abs(bounding[stim][j]['y_max'] - bounding[stim][j]['y_min'])

            C = abs(max(bounding[stim][i]['x_min'], bounding[stim][j]['x_min']) -\
                    min(bounding[stim][i]['x_max'], bounding[stim][j]['x_max'])) *\
                abs(max(bounding[stim][i]['y_min'], bounding[stim][j]['y_min']) - \
                    min(bounding[stim][i]['y_max'], bounding[stim][j]['y_max']))

            #fill in the matrix
            adjacency[stim][i][j] = C / (A + B - C)
            adjacency[stim][j][i] = C / (A + B - C)
        counter += 1

    print(adjacency)
    return adjacency


from read import read_main_df

df = read_main_df()
stimuli_names = df.StimuliName.unique()

scanpaths_dict('11_Bologna_S1.jpg', df.user.unique(), df)
