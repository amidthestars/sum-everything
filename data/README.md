# Data Processing
## General format:
```
[article]\t[summary]\n
[article]\t[summary]\n
[article]\t[summary]\n
```
Special characters must be handled. See [/data/gen-cnn.py](https://github.com/JEF1056/sum-everything/blob/main/data/gen-cnn.py) for a general template to create clean text.<br>
Newlines are handled by converting them to `/n` instead of the traditional `\n`<br>
T5 is text-to-text, which means any feature of the text that occurs consistently enough will become present in the final model. Please format the output to require minimal post-processing in production.
## Article formats
See the example (gen-cnn.py).
## Summary formats
This will vary depending on input data, but some ideas:<br>
Bullet points:
```
[article]\t- item1/n- item2/n- item3/n
```
Paragraph:
```
This is the abstract of a research paper....
```
## Splits
There should be a train and a val split. This should vaguely be a 80% train, 20% val, shuffled.<br>
Each dataset should be contained into its own folder, with shards in train being named `[dataset_name].train` and validation being named `[dataset_name].validation`. There can be multiple shards; the task manager will automatically stream and combine files from each split as long as they are givven the correct identifier.<br>An example directory structure is below:
```
cnn-1.train
cnn-2.train
cnn.validation
```
# Data Hosting
Data needs to be hosted on GCP, in the bucket [gs://sum-data-us](https://console.cloud.google.com/storage/browser/sum-data-us). If you do not have the `gsutil` command, please follow https://cloud.google.com/storage/docs/gsutil_install<br>
Note that this command is similar to the cp command. The below, run from the root folder, will copy all your compiled datasets. I reccomend being more selective when uploading datasets.<br>
Becasue the datasets are loaded into memory for training, it should be OK to uploadd updates to datasets whil traiing on them, but please do check running tasks.
```
gsutil -m cp -R datasets/* gs://sum-data-us
```
# Datasets.json
Please keep [/train/datasets.json](https://github.com/JEF1056/sum-everything/blob/main/train/datasets.json) up to date.<br>
To add a new entry, follow this format:
```
"DATASET NAME": {
    "bucket_path": "gs://sum-data-us",    # This is a gs:// path or a local path, the root dir
    "train_path": "cnn",                  # This is the parent folder for the training split
    "validation_path": "cnn",             # This is the parent folder for the validation split
    "compression_type": null,             # null (no compression), gzip (gzip compression), zlib (zlib compression). NOTE: not a .zip file, but the text is compressed
    "store_mode": "gs"                    # gs (google cloud), local (local file)
}
```
Example:
```
"cnn": {
    "bucket_path": "../datasets",
    "train_path": "cnn", 
    "validation_path": "cnn",
    "compression_type": null,
    "store_mode": "local"
}
```