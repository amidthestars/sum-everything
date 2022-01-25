import numpy as np
import os

folders = {"business" : 510, "entertainment" : 386, "politics" : 417, "sport" : 510, "tech" : 401}
overall_count = [0, 0]
path = os.getcwd()
np.random.seed(2022)

# clean and distribute data for different category
for folder in folders:

    train_data = open(path+"//"+folder+".train", "w")
    val_data = open(path+"//"+folder+".val", "w")
    outputs = [train_data, val_data]
    count = [0, 0]
    for i in range(folders[folder]):
        try:
            doc = str(i+1).rjust(3,'0')
            doc = "\\"+doc+".txt"
            # if category=0, then is a training data, otherwise validation
            category = np.random.choice(2, 1, p=[0.8, 0.2])[0]

            f_src = open(path+"\\News Articles\\"+folder+doc, "r")
            cont_src = f_src.read()
            cont_src = cont_src.replace("\n", " ")
            cont_src = cont_src.replace("\t", " ")
            f_tgt = open(path+"\\Summaries\\"+folder+doc, "r")
            cont_tgt = f_tgt.read()
            cont_tgt = cont_tgt.replace("\n", " ")
            cont_tgt = cont_tgt.replace("\t", " ")
            outputs[category].write(cont_src+"\t"+cont_tgt+"\n")
            count[category] += 1
            overall_count[category] += 1
        except:
            print(folder, doc)
    train_data.close()
    val_data.close()
    print(folder, "merge finish. [train, val]=", count)

# merge all categories together
train_data = open(path+"\\bbc.train", "w")
val_data = open(path+"\\bbc.validation", "w")
for folder in folders:
    f_src = open(path+"//"+folder+".train", "r")
    cont_src = f_src.read()
    train_data.write(cont_src)
    f_tgt = open(path+"//"+folder+".val", "r")
    cont_tgt = f_tgt.read()
    val_data.write(cont_tgt)

print("overall_count: [train, val]=", overall_count)
train_data.close()
val_data.close()
