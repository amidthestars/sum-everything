'''
Ideas:
    - If file empty & errmsg showing do nothing? (i.e don't refresh)
    - no actually update to edit mode and do not update contents
'''

import os
import nltk
import requests
import httpimport
from bs4 import BeautifulSoup
from flask_socketio import SocketIO, emit
from src.model import get_models, query_model
from flask import Flask, render_template, request, jsonify

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


# TODO: update route name to something that better represents endpoint purpose
@app.route('/get-route', methods=['GET', 'POST'])
def get_js_link():  # TODO: function name should match route name
    # TODO: create new file for this in /src. write unit tests for it.
    adStuff = ['Advertisement', "Supported by"]
    url = request.get_json()
    try:
        page = requests.get(url)
    except Exception as e:
        print(e)
        # Return if error in getting to link
        return "0"

    # TODO: is this chacked? if not, consider checking if it is already downloaded
    nltk.download('punkt')

    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all('p', attrs={'class': 'css-axufdj evys1bk0'})

    article = ''

    for e in links:
        m = e.getText()

        if m in adStuff:
            continue

        # If less, then add it
        if len(article + m) <= 5000:
            article = article + m
        else:
            sentences = nltk.tokenize.sent_tokenize(m)
            for sent in sentences:
                if len(article + ' ' + sent) <= 5000:
                    article = article + ' ' + sent
                else:
                    break

            break

    message = {'article': article}
    # TODO: no need for jsonify, flask already does this if dict is returned
    return jsonify(message)


@socketio.on('query')
def query(data):
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


if __name__ == "__main__":
    app.run(port=7000)
