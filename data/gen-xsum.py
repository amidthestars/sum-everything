import concurrent.futures
import io
import multiprocessing
import os
import random
import re
import shutil
import subprocess

import requests
from tqdm import tqdm

from src.helpers import clean

DATA_URL = "http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-Summary-Data-Original.tar.gz"
IN = "bbc-summary-data"
OUT = "../datasets/xsum"
PREFIX = "xsum"
PROCESSES = multiprocessing.cpu_count()
DATASET_FILE = DATA_URL.split("/")[-1]

# Download and unzip the dataset
if not os.path.exists(DATASET_FILE):
    with requests.get(DATA_URL, stream=True) as r, open(DATASET_FILE, "wb") as f:
        shutil.copyfileobj(r.raw, f)
if not os.path.exists(IN):
    subprocess.call(["tar", "-xf", DATASET_FILE])

# Define processor
def postprocess(text):
    # This is an optional function with addional project-specific postprocessing
    text = re.sub(r"^\[SN\].*?\[SN\]/n", "", text)
    return text.strip()

def worker(split, filename):
    file = io.open(os.path.join(IN, filename), mode="r", encoding="utf-8")
    data = []
    for part in file.read().split("\n\n"):
        if part.startswith(("[SN]FIRST-SENTENCE[SN]", "[SN]RESTBODY[SN]")):
            data.append(postprocess(clean(part)))
    if data[0] and data[1]:
        return split, data[1], data[0]

# Run concurrent processing
tasks = os.listdir(IN)
splits = ["train", "validation"]
split_distrib = random.choices(splits, weights = [80, 20], k=len(tasks))
os.makedirs(OUT, exist_ok=True)
outputs={split:io.open(os.path.join(OUT,f"{PREFIX}.{split}"), mode="w", encoding="utf-8") for split in splits}

with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSES) as executor:
    results = list(tqdm(executor.map(worker, split_distrib, tasks), total = len(tasks), desc=f"Using {PROCESSES} Processes"))
    for result in results:
        if result != None:
            split, article, summary = result
            outputs[split].write(f"{article}\t{summary}\n")

# Close and cleanup
for output in outputs: outputs[output].close()
