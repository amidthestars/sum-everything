import os
import io
import re
import html
import random
import subprocess
from tqdm import tqdm
import concurrent.futures
from src.helpers import clean

# Variables - maybe we should argparse these instead
DATA_URL = "https://cs.stanford.edu/~myasu/projects/scisumm_net/scisummnet_release1.1__20190413.zip"
IN = "scisummnet/top1000_complete"
OUT = "scisummnet"
PROCESSES = 12

# Download and unzip the dataset
if not os.path.exists("scisummnet.zip"):
    subprocess.call(["wget", "-O", "scisummnet.zip", DATA_URL])
if not os.path.exists(IN):
    subprocess.call(["unzip", "scisummnet.zip"])
    subprocess.call(["rm", "-rf", "__MACOSX"])
    subprocess.call(["mv", "scisummnet_release1.1__20190413", "scisummnet"])

# Define processor
def preprocess(text):
    # This is an optional function with addional project-specific postprocessing
    r1 = re.compile(r'\s*<.*?>\s*', re.IGNORECASE)
    text = re.sub(r1, "", text.strip())
    text = html.unescape(text.strip())
    return text.lstrip(("-!.,^# ")).strip()

def worker(split, foldername):
    path=os.path.join(IN, foldername, "Documents_xml")
    article = io.open(os.path.join(path, os.listdir(path)[0]), mode="r", encoding="utf-8").read()
    article = clean(preprocess(article))
    path=os.path.join(IN, foldername, "summary")
    summary = io.open(os.path.join(path, os.listdir(path)[0]), mode="r", encoding="utf-8").read()
    summary = clean(preprocess(summary))
    return split, article, summary

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