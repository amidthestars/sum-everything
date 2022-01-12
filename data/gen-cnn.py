import os
import io
import re
import gdown
import random
import subprocess
from tqdm import tqdm
import concurrent.futures
from helpers import clean

# Variables - maybe we should argparse these instead
DATA_URL = "https://docs.google.com/uc?export=download&id=0BwmD_VLjROrfTHk4NFg2SndKcjQ"
IN = "cnn/stories"
OUT = "cnn-stories"
PROCESSES = 12

# Download and unzip the dataset
if not os.path.exists("cnn_stories.tgz"):
    gdown.download(DATA_URL, "cnn_stories.tgz", quiet=False)
if not os.path.exists(IN):
    subprocess.call(["tar", "-xf", "cnn_stories.tgz"])

# Define processor
def postpocess(text):
    # This is an optional function with addional project-specific postprocessing
    r1 = re.compile(r'\s*\(CNN\)\s*', re.IGNORECASE)
    text = re.sub(r1, "", text.strip())
    return text.lstrip(("-!.,^# ")).strip()

def worker(split, filename):
    file = io.open(os.path.join(IN, filename), mode="r", encoding="utf-8")
    data = [postpocess(clean(part)) for part in file.read().split("@highlight\n\n")] #apply cleaning to each part
    return split, data[0], "/n".join([f"- {summary}" for summary in data[1:]])

# Run concurrent processing
tasks = os.listdir(IN)
splits = ["train", "test", "validation"]
split_distrib = random.choices(splits, weights = [80, 10, 10], k=len(tasks))
outputs={split:io.open(f"{OUT}.{split}", mode="w", encoding="utf-8") for split in splits}

with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSES) as executor:
    results = list(tqdm(executor.map(worker, split_distrib, tasks), total = len(tasks)))
    for result in results:
        split, article, summary = result
        outputs[split].write(f"{article}\t{summary}\n")

# Close and cleanup
for output in outputs: outputs[output].close()