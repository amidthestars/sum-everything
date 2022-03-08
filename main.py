'''
Ideas:
    - If file empty & errmsg showing do nothing? (i.e don't refresh)
    - no actually update to edit mode and do not update contents
'''

import os
import httpimport
from flask_socketio import SocketIO, emit
from src.model import get_models, query_model
from src.parse_url import parse_url
from flask import Flask, render_template, request

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}
MODEL_IP = "155.248.202.186"
MODEL_PORT = 3000
MODEL_URL = f"http://{MODEL_IP}:{MODEL_PORT}/v1/models/"

# Flask instance; allows for instance (database) outside folder
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.urandom(12)
socketio = SocketIO(app)

# Dynamically import from main branch
cleaner_module = 'https://raw.githubusercontent.com/JEF1056/sum-everything/main/data/src'
with httpimport.remote_repo(["helpers"], cleaner_module):
    from helpers import clean, parse

acks = {
    "received": {
        "message": "Request received! - Processing!",
        "color": "yellow",
        "icon": ["fa-hammer"]
    },
    "cleaned": {
        "message": "Processing Done. - Creating a summary!",
        "color": "blue",
        "icon": ['shake-constant', 'shake-slow', 'fa-dumpster']
    },
    "success": {
        "message": "Here you go! *high five*",
        "color": "green",
        "icon": ["fa-cat"]
    },
    "error": {
        "message": "Ohno... the model couldn't figure it out... (check js console for the deets)",
        "color": "red",
        "icon": ["fa-dumpster-fire"]
    }
}


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route("/v1/models", methods=['GET'])
def models():
    return get_models()


@app.route('/parse-js-link', methods=['GET', 'POST'])
def parse_js_link():
    return parse_url(request.get_json())

occupied_sockets = set()
@socketio.on('query')
def query(data):
    currentid = request.sid
    if currentid not in occupied_sockets:
        # Grab varaibles
        model, inputs = data["model"], data["input"]
        emit('model_ack', dict(status="received", **acks["received"]))

        # Clean text
        inputs = clean(inputs)
        emit('model_ack', dict(status="cleaned", inputs=parse(inputs), **acks["cleaned"]))

        # Model query
        try:
            response = query_model(model, inputs)
            # Emit response
            emit('model_response', dict(status="success", **response, **acks["success"]))
        except RuntimeError as e:
            emit('model_response', dict(status="error", info=e.__repr__, **acks["error"]))
        occupied_sockets.remove(currentid)


if __name__ == "__main__":
    app.run(port=7000)
