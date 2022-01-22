import os
import sys
import json
import seqio
import warnings
import argparse
import statistics
import importlib.util
import tensorflow_datasets as tfds
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Get dataset statstics')
parser.add_argument('-datasets', nargs='+', type=str, required=True,
                    help='Names of dataset(s) as defined in datasets.json')
parser.add_argument('-samples', type=int, default=1000,
                    help='Number of samples per dataset to calculate from')
parser.add_argument('-in_len', type=int, default=2048,
                    help='Maximum length of input. Inputs will be padded to this length.')
parser.add_argument('-out_len', type=int, default=512,
                    help='Maximum length of output. Outputs will be padded to this length.')
args = parser.parse_args()

# Register dataset as a mixture
ds_registrar_spec = importlib.util.find_spec('src.createtask')
datasets=json.load(open("datasets.json", "r"))
for dataset in args.datasets:
    if dataset in datasets:
        info=datasets[dataset]
        new_ds = importlib.util.module_from_spec(ds_registrar_spec)
        ds_registrar_spec.loader.exec_module(new_ds)
        sys.modules['new_ds'] = new_ds
        new_ds.init(info["bucket_path"],info["train_path"], info["validation_path"], 
                    dataset, info["compression_type"], info["store_mode"])
    else:
        warnings.warn(f"Dataset {dataset} was not in datasets.json, and will not be included.")
        args.datasets.remove(dataset)

seqio.MixtureRegistry.add(
    "all_mix",
    args.datasets,
    default_rate=1.0
)

# Run statistcs
train_ds=seqio.MixtureRegistry.get("all_mix").get_dataset(split="train", sequence_length={"inputs": args.in_len, "targets": args.out_len})
validation_ds=seqio.MixtureRegistry.get("all_mix").get_dataset(split="validation", sequence_length={"inputs": args.in_len, "targets": args.out_len})
train=list(tfds.as_numpy(train_ds.take(args.samples)))
validation=list(tfds.as_numpy(validation_ds.take(args.samples)))

print("Dataset creation complete.")

t_in, t_out=[], []
for sample in train:
    t_in.append(len(sample["inputs"]))
    t_out.append(len(sample["targets"]))

v_in, v_out=[], []
for sample in validation:
    v_in.append(len(sample["inputs"]))
    v_out.append(len(sample["targets"]))

print(f"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{args.samples} samples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Train Input:
Min {min(t_in)}
Max {max(t_in)}
Avg. {sum(t_in)/len(t_in)}
Std. Dev {statistics.pstdev(t_in)}

Train Target:
Min {min(t_out)}
Max {max(t_out)}
Avg. {sum(t_out)/len(t_out)}
Std. Dev {statistics.pstdev(t_out)}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Validation Input:
Min {min(v_in)}
Max {max(v_in)}
Avg. {sum(v_in)/len(v_in)}
Std. Dev {statistics.pstdev(v_in)}

Validation Target:
Min {min(v_out)}
Max {max(v_out)}
Avg. {sum(v_out)/len(v_out)}
Std. Dev {statistics.pstdev(v_out)}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")