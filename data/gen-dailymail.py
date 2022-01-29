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
DATA_URL = "https://docs.google.com/uc?export=download&id=0BwmD_VLjROrfM1BxdkxVaTY2bWs"
IN = "dailymail/stories"
OUT = "../datasets/dailymail"
PREFIX = "dailymail"
PROCESSES = multiprocessing.cpu_count()

# Download and unzip the dataset
if not os.path.exists("dailymail_stories.tgz"):
    gdown.download(DATA_URL, "dailymail_stories.tgz", quiet=False)
if not os.path.exists(IN):
    subprocess.call(["tar", "-xf", "dailymail_stories.tgz"])

# Define processor
def preprocess(text):
    # This is an optional function with addional project-specific postprocessing
    r0 = re.compile(r'\n+', re.IGNORECASE | re.DOTALL)
    r1 = re.compile(r'^.*?UPDATED:?\n|^.*?PUBLISHED:?\n|^.*?CREATED:?\n|^.*?BY\n.*?\n|^.*?Follow.*?\n|\d{2}:\d{2} [a-z]{3}, \d{1,2} [a-z]+ \d{4}', re.IGNORECASE | re.DOTALL)
    text = re.sub(r0, "\n", text.strip())
    text = re.sub(r1, "", text.strip())
    return text.lstrip(("-!.,^# ")).strip()

def worker(split, filename):
    file = io.open(os.path.join(IN, filename), mode="r", encoding="utf-8")
    data = [clean(preprocess(part)) if i == 0 else clean(part) for i, part in enumerate(file.read().split("@highlight\n\n"))] #apply cleaning to each part
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
                if len(article) > len(summary):
                    outputs[split].write(f"{article}\t{summary}\n")

    # Close and cleanup
    for output in outputs: outputs[output].close()