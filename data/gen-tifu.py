import os
import io
import json
import sys
import tqdm
import gdown
import random
import subprocess
from src.helpers import clean

DATA_URL = "https://drive.google.com/uc?export=download&id=1swS7fuzE_UMhKtcWIJdOvbgBWl8cyGjd"
IN = "tifu"
OUT = "../datasets/tifu"
PREFIX = "tifu"
if len(sys.argv) == 1: random.seed(2022)
else: random.seed(int(sys.argv[1]))

if not os.path.exists("tifu_datasets.zip"):
    gdown.download(DATA_URL, "tifu_datasets.zip", quiet=False)
if not os.path.exists(IN):
    os.mkdir(IN)
    subprocess.call(['unzip', '-o', "tifu_datasets.zip", '-d', "../data/tifu"])

files = os.listdir(IN)
splits = ["train", "validation"]
try: os.makedirs(OUT)
except FileExistsError: pass
outputs={split:io.open(os.path.join(OUT,f"{PREFIX}.{split}"), mode="w", encoding="utf-8") for split in splits}

count = 0
for filename in tqdm.tqdm(files):
    with io.open(os.path.join(IN,filename), mode="r", encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            if data["tldr"]:
                tldr = data["tldr"]
                if data["selftext_without_tldr"]:
                    selftext = data["selftext_without_tldr"]
                    try: outputs[random.choices(splits, weights = [80, 20])[0]].write(f"{clean(selftext)}\t{clean(tldr)}\n")
                    except IndexError: continue # skip empty entries

for output in outputs: outputs[output].close()
