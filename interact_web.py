import time
import json
import requests
from termcolor import cprint
from data.src.helpers import clean, parse

class model_api():
    def __init__(self, url: str, port: int, model: str):
        self.url = f"http://{url}:{port}/v1/models/"
        self.model = model
    
    def set_model(self, model: str):
        self.model = model.strip()

    def query(self, input: str, batches: int, debug: bool=False) -> dict:
        data = {"inputs": [clean(input)]*batches}
        if debug: 
            cprint(f"{self.url}{self.model}:predict", 'grey')
            cprint(data, 'grey')
        start = time.perf_counter()
        response = requests.post(f"{self.url}{self.model}:predict", data=json.dumps(data))
        if response.status_code == 200:
            response = response.json()['outputs']
            for label in response:
                response[label] = [parse(entry) for entry in response[label]]
            if debug: cprint(response, 'grey')
            return response, time.perf_counter() - start
        else: raise RuntimeError(f"Server returned {response.status_code}\nInfo: {response.content}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Interact with tf-serving')
    parser.add_argument('-url', type=str, required=True,
                        help='Main url, without any params')
    parser.add_argument('-port', type=int, default=3000,
                        help='Port the model is hosted on')
    parser.add_argument('-model', type=str, required=True,
                        help='Model name')
    args = parser.parse_args()

    remote = model_api(args.url, args.port, args.model)
    while True:
        inp = input("> ")
        if inp.startswith("cd "):
            inp = inp[3:]
            remote.set_model(inp)
            cprint(f'Set model to {inp}', 'cyan', attrs=['bold'])
        elif inp.startswith("cat "):
            inp = inp[4:]
            cprint(f'Querying {remote.model} from text file {inp}', 'blue', attrs=['bold'])
            inp = open(inp, 'r').read()
            out = remote.query(inp, 1)
            print('\n\n'.join(out[0]['outputs']))
            cprint(f"Done in {out[1]}s", "cyan")