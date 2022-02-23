'''
Ideas:
    - If file empty & errmsg showing do nothing? (i.e don't refresh)
    - no actually update to edit mode and do not update contents
'''

import re
import os
import requests
import httpimport
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from bs4 import BeautifulSoup
import nltk

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}
MODEL_CONFIG = "https://storage.googleapis.com/sum-exported/models.config"
MODEL_URL = "155.248.202.186"
MODEL_PORT = 3000
MODEL_URL = f"http://{MODEL_URL}:{MODEL_PORT}/v1/models/"

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

@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")

@app.route("/v1/models", methods = ['GET'])
def get_models():
    # TODO: do not hardcode urls
    models = re.findall(r"name: '(.*?)'", requests.get(MODEL_CONFIG).text)
    # Check which ones are enabled
    ret = {}
    for model in models:
        model_status = requests.get(f"{MODEL_URL}{model}").json()
        if "error" in model_status:
            ret[model] = False
        else:
            ret[model] = True
    return ret

@app.route('/get-route', methods=['GET', 'POST'])
def get_js_link():
    adStuff = ['Advertisement', "Supported by"]

    url = request.get_json()
    
    try:
        page = requests.get(url)
    except Exception as e:
        error_type, error_obj, error_info = sys.exc_info()

        print("Error for link:", URL)

        print(error_type, 'Line:', error_info.tb_lineno)
        # Return if error in getting to link
        return "0"

    nltk.download('punkt')

    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all('p', attrs={'class':'css-axufdj evys1bk0'})

    article = ''

    for e in links:
        m = e.getText()

        if m in adStuff:
            continue

        # If less, then add it
        if len(article+m) <= 5000:
            article = article + m
        else:
            sentences = nltk.tokenize.sent_tokenize(m)
            for sent in sentences:
                if len(article + ' ' + sent) <= 5000:
                    article = article + ' ' + sent
                else:
                    break

            break

    message = {'article':article}
    return jsonify(message)

@socketio.on('query')
def query(data):
    model, inputs = data["model"], data["input"]
    emit('model_ack', dict(status="received", **acks["received"]))
    inputs = clean(inputs)
    emit('model_ack', dict(status="cleaned", inputs=inputs.replace("/n", "\n"), **acks["cleaned"]))
    data = {"inputs": [inputs]}
    response = requests.post(f"{MODEL_URL}{model}:predict", json=data)
    if response.status_code == 200:
        # Response cleanup
        response = response.json()['outputs']
        for label in response:
            response[label] = [parse(entry) for entry in response[label]]

        # Prepare socket emit
        emit('model_response', dict(status="success", **response, **acks["success"]))
    else:
        emit(
            'model_response',
            dict(
                status="error",
                info=f"Model server returned {response.status_code}\nInfo: {response.content}",
                **acks["error"]
            )
        )

if __name__ == "__main__":
    app.run(port=7000)
