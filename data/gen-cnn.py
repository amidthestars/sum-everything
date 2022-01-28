import os
import io
import re
import gdown
import random
import subprocess
from tqdm import tqdm
import multiprocessing
import concurrent.futures
from src.helpers import clean

# Variables - maybe we should argparse these instead
DATA_URL = "https://docs.google.com/uc?export=download&id=0BwmD_VLjROrfTHk4NFg2SndKcjQ"
IN = "cnn/stories"
OUT = "../datasets/cnn"
PREFIX = "cnn"
PROCESSES = multiprocessing.cpu_count()

# Download and unzip the dataset
if not os.path.exists("cnn_stories.tgz"):
    gdown.download(DATA_URL, "cnn_stories.tgz", quiet=False)
if not os.path.exists(IN):
    subprocess.call(["tar", "-xf", "cnn_stories.tgz"])

# Define processor
def postprocess(text):
    # This is an optional function with addional project-specific postprocessing
    r1 = re.compile(r'\s*\(CNN\)\s*', re.IGNORECASE)
    text = re.sub(r1, "", text.strip())
    return text.lstrip(("-!.,^# ")).strip()

def worker(split, filename):
    file = io.open(os.path.join(IN, filename), mode="r", encoding="utf-8")
    data = [postprocess(clean(part)) for part in file.read().split("@highlight\n\n")] #apply cleaning to each part
    if data[0] and data[1]:
        return split, data[0], "/n".join([f"- {summary}" for summary in data[1:]])

# Run concurrent processing
if __name__ == '__main__':
    tasks = os.listdir(IN)
    splits = ["train", "validation"]
    split_distrib = random.choices(splits, weights = [80, 20], k=len(tasks))
    try: os.makedirs(OUT)
    except FileExistsError: pass
    outputs={split:io.open(os.path.join(OUT,f"{PREFIX}.{split}"), mode="w", encoding="utf-8") for split in splits}

    with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        results = list(tqdm(executor.map(worker, split_distrib, tasks), total = len(tasks), desc=f"Using {PROCESSES} Processes"))
        for result in results:
            if result != None:
                split, article, summary = result
                outputs[split].write(f"{article}\t{summary}\n")

    # Close and cleanup
    for output in outputs: outputs[output].close()