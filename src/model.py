# This is the module responsible for calling the model backend
import re
import requests
import httpimport

cleaner_module = 'https://raw.githubusercontent.com/JEF1056/sum-everything/main/data/src'
with httpimport.remote_repo(["helpers"], cleaner_module):
    from helpers import parse

# Defaults
MODEL_CONFIG = "https://storage.googleapis.com/sum-exported/models.config"
MODEL_IP = "155.248.202.186"
MODEL_PORT = 3000
MODEL_URL = f"http://{MODEL_IP}:{MODEL_PORT}/v1/models/"


def get_models(model_url=MODEL_URL, model_config=MODEL_CONFIG):
    # query all names
    models = re.findall(r"name: '(.*?)'", requests.get(model_config).text)
    print(models)
    # Check which ones are enabled
    if models:
        ret = {}
        for model in models:
            try:
                model_status = requests.get(f"{model_url}{model}")
                if model_status.status_code != 200:
                    ret[model] = False
                else:
                    ret[model] = True
            except BaseException:
                ret[model] = False
        return ret
    else:
        raise RuntimeError("No models found.")


def query_model(model, inputs, model_url=MODEL_URL):
    data = {"inputs": [inputs]}
    query = requests.post(f"{model_url}{model}:predict", json=data)
    if query.status_code == 200:
        # Response cleanup
        response = query.json()['outputs']
        for label in response:
            response[label] = [parse(entry) for entry in response[label]]
        return response
    else:
        raise RuntimeError(f"Model server returned {query.status_code}\nInfo: {query.content}")
