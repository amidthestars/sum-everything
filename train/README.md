# Training
To read the help menu of [/train/train.py](https://github.com/JEF1056/sum-everything/blob/main/train/train.py), run:
```
python3 train.py -h
```
To train a simple small model on the cnn and scisummnet datasets with two GPUs:
```
python3 train.py \
    -datasets cnn scisummnet \
    -gpus gpu:0 gpu:1 \
    -steps 10000 \
    -batch_size 8 \
    -in_len 1028 \
    -out_len 128
```
To train a simple small model on the local cnn and gs scisummnet datasets with a TPU:
```
python3 train.py \
    -datasets cnn scisummnet_gs \
    -tpu 192.168.1.1\
    -tpu_topology v3-8 \
    -steps 10000 \
```

# Exporting the model
To read the help menu of [/train/export.py](https://github.com/JEF1056/sum-everything/blob/main/train/export.py), run:
```
python3 expot.py -h
```
To export a model stored in `models/small`:
```
python3 export.py \
    -dir models/small \
    -out export \
    -name v7500
```
Note that `dir` supports gs:// paths