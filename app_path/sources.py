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
    # --- Metadata with city names as keys
    cities_meta = dict()
    for stimulus, values in meta.items():
        city_name = values['txt_name']
        if city_name in cities_meta.keys():
            cities_meta[city_name].update({stimulus: values})
        else:
            cities_meta[city_name] = dict()
            cities_meta[city_name].update({stimulus: values})

    return cities_meta


# TODO
def load_matrix(stimulus, metric):
    pass

