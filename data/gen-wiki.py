import sys
import numpy as np
import os
import io
import gdown
import random
import zipfile
from tqdm import tqdm
import multiprocessing
import concurrent.futures
from src.helpers import clean

DATA_URL = "https://drive.google.com/uc?export=download&id=1BnPhEZISDwuWIEzLMQeud-HBA4BSUUor"
IN = "wikiHow/articles"
PROCESSES = multiprocessing.cpu_count()
OUT = "../datasets/wiki"
PREFIX = "wikiHow"
if len(sys.argv) == 1:
    np.random.seed(2022)
else:
    np.random.seed(int(sys.argv[1]))

# download and unzip dataset
if not os.path.exists("wikiHow.zip"):
    gdown.download(DATA_URL, "wikiHow.zip", quiet=False)
if not os.path.exists(IN):
    os.makedirs(IN, exist_ok=True)
    if zipfile.is_zipfile("wikiHow.zip"):
        fz = zipfile.ZipFile("wikiHow.zip", "r")
        for file in fz.namelist():
            fz.extract(file, ".")


# Define processor
def postprocess(text):
    # This is an optional function with addional project-specific postprocessing
    text = text.replace("@summary", " ")
    return text.lstrip(("-!.,^# ")).strip()


def worker(split, title):
    filename = title + ".txt"
    try:
        file = io.open(os.path.join(IN, filename), mode="r", encoding="utf-8")
        data = [postprocess(clean(part)) for part in file.read().split("@article")]  # apply cleaning to each part
    except:  # in case the title cannot be recognized by system
        data = [False, False]
    if data[0] and data[1]:
        return split, data[1], data[0] if not data[0].startswith("/n") else data[0][2:]


# Run concurrent processing
if __name__ == '__main__':
    title_file = open('wikiHow/titles.txt', mode="r", encoding="utf-8").read().split("\n")
    splits = ["train", "validation"]
    split_distrib = random.choices(splits, weights=[80, 20], k=len(title_file))
    os.makedirs(OUT, exist_ok=True)
    outputs = {split: io.open(os.path.join(OUT, f"{PREFIX}.{split}"), mode="w", encoding="utf-8") for split in splits}

    with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        results = list(tqdm(executor.map(worker, split_distrib, title_file), total=len(title_file),
                            desc=f"Using {PROCESSES} Processes"))
        for result in results:
            if result is not None:
                split, article, summary = result
                if len(article) > len(summary):
                    outputs[split].write(f"{article}\t{summary}\n")

    # Close and cleanup
    for output in outputs: outputs[output].close()
