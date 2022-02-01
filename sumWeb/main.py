'''
Ideas:
	- If file empty & errmsg showing do nothing? (i.e don't refresh)
'''
import re
import os
import json
import requests
from flask import Flask, render_template

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}

# Flask instance; allows for instance (database) outside folder
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.urandom(12)

@app.route('/', methods = ['GET'])
def index():
	return render_template("index-0.html")

@app.route("/v1/models", methods = ['GET'])
def get_models():
	# TODO: do not hardcode urls
	url = "https://storage.googleapis.com/sum-exported/models.config"
	models = re.findall(r"name: '(.*?)'", requests.get(url).text)
	return {"models": models}

if __name__ == "__main__":
    app.run()