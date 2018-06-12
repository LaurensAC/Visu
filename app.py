import subprocess
import re
import os
import signal
import sys
sys.path.insert(0, './app_path')
from flask import Flask, render_template, Response
from bokeh.embed import server_document
from utils import find_path

# FOR DEVELOPMENT PURPOSES, TESTED ON UBUNTU 16.04

# Running on 127.0.0.1:5000 by default
SOCKET = "127.0.0.1:5000"
app = Flask(__name__)

# Storing ports/process ids of bokeh scripts, name of script as key
# --- Ensures URLS embedding a bokeh app embed the most up-to-date bokeh server
SERVING = dict()


# Spins up a bokeh server for <script> on <port>
@app.route('/<string:script>/<string:port>')
def serve(script, port):
    assert re.match(r'^[a-zA-Z._-]+$', script)

    # Killing old version
    if script in SERVING:
        try:
            os.kill(SERVING[script]['bokeh_pid'], signal.SIGKILL)
        except ProcessLookupError:
            print("{} is already deddo".format(script))

    def inner():
        # Location of bokeh script
        exec_path = find_path(script + '.py')
        # Serve script on specified port
        cmd = "bokeh serve {} --port {} ".format(exec_path, port)
        # Whitelist cross site connections e.g. this flask application
        cmd += "--allow-websocket-origin {} ".format(SOCKET)

        cmd += "--log-level info "
        # Log memory usage, frequency in ms
        cmd += "--mem-log-frequency=30000"

        # Spawn
        proc = subprocess.Popen(
            [cmd],
            shell=True,
            stderr=subprocess.PIPE,
            # stdout=open('out.txt', 'w'),
            universal_newlines=True
        )

        # Streaming stderr of bokeh serve to webpage
        for line in iter(proc.stderr.readline, ''):
            yield line.rstrip() + '<br/>\n'

            # Update globals if newer version is up and running
            bokeh_pid = re.findall(r'process id: (\d+)', line)
            if bokeh_pid:
                SERVING[script] = dict(port=port,
                                       shell_pid=proc.pid,
                                       bokeh_pid=int(bokeh_pid.pop())
                                       )

    return Response(inner(), mimetype='text/html')

# Grabs and embeds
@app.route("/plots/<string:script>")
def hello(script):
    bokeh_file = server_document("http://localhost:{}/{}"
                                 .format(SERVING[script]['port'], script),
                                 # Pass around (global) params
                                 arguments={'layout': 'single'})

    return render_template('dashboard.html', bokehScript=bokeh_file,
                           title=script)


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
