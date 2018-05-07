from flask import Flask, flash, redirect, render_template, request, session, abort
from bokeh.embed import server_document
# import bokeh
app = Flask(__name__)


@app.route("/")
def hello():
    
    script = server_document("http://localhost:5006/bokeh-sliders",
                             arguments={'foo': 'bar'})
    
    return render_template('dashboard.html', bokehScript=script)


if __name__ == "__main__":
    app.run()
