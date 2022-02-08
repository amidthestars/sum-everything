'''
Ideas:
	- If file empty & errmsg showing do nothing? (i.e don't refresh) - no actually update to edit mode and do not update contents
'''
import re
import os
import requests
import httpimport
from flask_socketio import SocketIO
from flask import Flask, render_template, request, make_response

# Dynamically import from main branch
cleaner_module = 'https://raw.githubusercontent.com/JEF1056/sum-everything/main/data/src'
with httpimport.remote_repo(["helpers"], cleaner_module):
    from helpers import clean, parse

class ModelAPI():
    def __init__(self, url: str, port: int, model: str=None):
        self.url = f"http://{url}:{port}/v1/models/"
        self.model = model

    def set_model(self, model: str):
        self.model = model

    def query(self, inputs: str, batches: int) -> dict:
        data = {"inputs": [clean(inputs)]*batches}
        response = requests.post(f"{self.url}{self.model}:predict", json=data)
        if response.status_code == 200:
            # Response cleanup
            response = response.json()['outputs']
            app.logger.info(response)
            for label in response:
                response[label] = [parse(entry) for entry in response[label]]

            # Prepare flask return
            ret = make_response(response, 200)
            ret.mimetype = "application/json"
            return ret
        else:
            ret = make_response(f"Model server returned {response.status.code}\nInfo: {response.content}",response.status_code)
            ret.mimetype = "text/plain"
            return ret

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}

# Flask instance; allows for instance (database) outside folder
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.urandom(12)
socketio = SocketIO(app)
model_api = ModelAPI("155.248.202.186", 3000)

@app.route('/', methods = ['GET'])
def index():
	return render_template("index.html")

@app.route("/v1/models", methods = ['GET'])
def get_models():
	# TODO: do not hardcode urls
	url = "https://storage.googleapis.com/sum-exported/models.config"
	models = re.findall(r"name: '(.*?)'", requests.get(url).text)
	return {"models": models}

@app.route("/v1/query", methods=['POST'])
def query():
    data = request.json
    model_api.set_model(data["model"])
    response = model_api.query(data["input"], 1)
    return response

@socketio.on('message')
def handle_message(data):
    app.logger.info(f'received message: {data}')
    print(f'received message: {data}')

if __name__ == "__main__":
    app.run(port=7000)
