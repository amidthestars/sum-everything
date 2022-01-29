import os
import io
import csv
import sys
import tqdm
import gdown
import random
import subprocess
from src.helpers import clean

DATA_URL = "https://drive.google.com/uc?export=download&id=14-yvKIYucN9dEq5S9FcwHnvL0EHGgkFx"
IN = "idt"
OUT = "../datasets/idt"
PREFIX = "idt"
if len(sys.argv) == 1: random.seed(2022)
else: random.seed(int(sys.argv[1]))

if not os.path.exists("hindu_indian_times_guardian_news.zip"):
    gdown.download(DATA_URL, "hindu_indian_times_guardian_news.zip", quiet=False)
if not os.path.exists(IN):
    os.mkdir(IN)
    subprocess.call(['unzip', '-o', "hindu_indian_times_guardian_news.zip", '-d', "../data/idt"])

files = os.listdir(IN)
splits = ["train", "validation"]
try: os.makedirs(OUT)
except FileExistsError: pass
outputs={split:io.open(os.path.join(OUT,f"{PREFIX}.{split}"), mode="w", encoding="utf-8") for split in splits}

for filename in tqdm.tqdm(files):
    with io.open(os.path.join(IN, filename), mode="r", encoding = "ISO-8859-1") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if row[0] == "author": continue
            try: outputs[random.choices(splits, weights = [80, 20])[0]].write(f"{clean(row[4])}\t{clean(row[5])}\n")
            except IndexError: continue # skip empty entries

for output in outputs: outputs[output].close()
