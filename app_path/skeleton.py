"""
The following skeleton may fill itself with _three_ bokeh figures by calling

"""
import os, sys

# Adding parent directory for relative imports
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from utils import find_path
from importlib import import_module

import bokeh.models
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox, layout

FLASK_PARAMS = curdoc().session_context.request.arguments
SCRIPTS = {  # TODO "input_panel": 1,
    #  "adjacency_matrix": 2,
    # TODO "descriptives": 3,
    "stimuli_img": 4
}


###############
# 1 | 2 2 | 3 #
# 1 | 2 2 | 4 #
###############

class Skeleton(object):

    def __init__(self):
        self.figures = list()
        self.bokehs = list()
        self.import_bokehs()
        # Users give input through a box of widgets
        self.widgets = list()

    @staticmethod
    def import_bokehs():
        for script in SCRIPTS.keys():
            try:
                path = find_path(script + '.py')
                sys.path.insert(0, path)
                SCRIPTS.update({script: import_module(script)})
            except ImportError as e:
                SCRIPTS.update({script: None})
                raise e

    def load_figures(self):
        for name, module in SCRIPTS.items():
            try:
                bokehy = module.test()
                self.bokehs.append(bokehy)

            except NotImplementedError as e:
                raise e

        # figures = SCRIPTS['stimuli_img'].test()

        for figury in self.bokehs:
            for figure in figury:
                if isinstance(figure, bokeh.models.Widget):
                    print(str(figure))
                    print(type(figure))
                    self.widgets.append(figure)
                else:
                    self.figures.append(figure)

        # dashboard = layout([[], []])
        # dashboard.children[0] = self.input_panel
        # dashboard.children[1] = column([figures[2], figures[3]])

        sizing_mode = 'fixed'
        inputs = widgetbox(*self.widgets, sizing_mode=sizing_mode)

        right = column([self.figures[0]])
        l = row(inputs, right)

        curdoc().add_root(l)
        curdoc().title = 'aye'


dshb = Skeleton()
dshb.load_figures()
