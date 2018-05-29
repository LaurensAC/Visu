from PIL import Image
import numpy as np
from bokeh.models import ColumnDataSource
# ---
from utils import find_path, track

# Use this module to construct ColumnDataSources (in memory)


@track
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

    return ColumnDataSource({'image': [img]})


@track
def get_city_select_options(meta):
    options = list()
    for filename, values in meta.items():
        print(values)
        options.append(values['widget_name'])
    return options


# TODO
def load_matrix(stimulus, metric):
    pass

