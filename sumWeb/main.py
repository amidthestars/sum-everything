'''
Ideas:
	- If file empty & errmsg showing do nothing? (i.e don't refresh)
'''
import re
import os
import requests
import httpimport
from flask import Flask, render_template, request

# Dynamically import from main branch
cleaner_module = 'https://raw.githubusercontent.com/JEF1056/sum-everything/main/data/src/helpers.py'
with httpimport.remote_repo(["clean", "parse"], cleaner_module):
    import clean, parse

class ModelAPI():
    def __init__(self, url: str, port: int, model: str=None):
        self.url = f"http://{url}:{port}/v1/models/"
        self.model = model

    def set_model(self, model: str):
        self.model = model

    def query(self, input: str, batches: int) -> dict:
        data = {"inputs": [input]*batches}
        response = requests.post(f"{self.url}{self.model}:predict", json=data)
        return response.json()["outputs"]

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}

# Flask instance; allows for instance (database) outside folder
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.urandom(12)
model_api = ModelAPI("155.248.202.186", 3000)

@app.route('/', methods = ['GET'])
def index():
	return render_template("index-0.html")

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
    return {"output": response["outputs"][0]}

if __name__ == "__main__":
    app.run()
