import pandas as pd

from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

# define a method to generate x, y, z values
import random
def generate(x):
    return int(x) + random.random()

# generate data to use
df = pd.DataFrame(index=[str(i) for i in range(20)])
x = df.index.map(generate)
y = df.index.map(generate)
z = df.index.map(generate)

data = ColumnDataSource(dict(x=x.values, y=y.tolist(), z=z.values))

# plot and show
plot = figure(width=350, height=350)
plot.circle(x='x', y='y', size='z', source=data)
curdoc().add_root(layout([plot]))