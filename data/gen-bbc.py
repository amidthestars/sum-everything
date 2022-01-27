import numpy as np
import os
import re
import gdown
import zipfile
from tqdm import tqdm
from src.helpers import clean

DATA_URL = "https://drive.google.com/uc?export=download&id=1i4cPVFTZjVzfOn5GRCzDEc_OHiJ79Rlt"
IN = "bbc"
OUT = "../datasets/bbc"

folders = {"business": 510, "entertainment": 386, "politics": 417, "sport": 510, "tech": 401}
overall_count = [0, 0]
path = os.getcwd()
np.random.seed(2022)

if not os.path.exists("bbc.zip"):
    gdown.download(DATA_URL, "bbc.zip", quiet=False)
if not os.path.exists(IN):
    os.mkdir(IN)
    if zipfile.is_zipfile("bbc.zip"):
        fz = zipfile.ZipFile("bbc.zip", "r")
        for file in fz.namelist():
            fz.extract(file, ".")

os.makedirs(OUT, exist_ok=True)
train_data = open(os.path.join(OUT, "bbc.train"), "w")
val_data = open(os.path.join(OUT, "bbc.validation"), "w")

# clean and distribute data for different category
for folder in tqdm(folders):

    outputs = [train_data, val_data]
    count = [0, 0]
    for i in range(folders[folder]):
        try:
            doc = str(i + 1).rjust(3, '0')
            doc = "/" + doc + ".txt"
            # if category=0, then is a training data, otherwise validation
            category = np.random.choice(2, 1, p=[0.8, 0.2])[0]

            f_src = open("../data/bbc/News Articles/" + folder + doc, "r")
            cont_src = f_src.read()
            cont_src = cont_src.replace("\n", " ")
            cont_src = cont_src.replace("\t", " ")
            f_tgt = open("../data/bbc/Summaries/" + folder + doc, "r")
            cont_tgt = f_tgt.read()
            cont_tgt = cont_tgt.replace("\n", " ")
            cont_tgt = cont_tgt.replace("\t", " ")
            cont_tgt = re.sub(r"([\.!?,])([a-zA-Z\'\"0-9])", r"\1 \2", cont_tgt.strip())
            outputs[category].write(clean(cont_src) + "\t" + clean(cont_tgt) + "\n")
            count[category] += 1
            overall_count[category] += 1
        except:
            print(folder, doc)
    # print(folder, "merge finish. [train, val]=", count)

print("overall_count: [train, val]=", overall_count)
train_data.close()
val_data.close()
