import t5
import os
import sys
import json
import seqio
import warnings
import argparse
import t5.models
import importlib.util
import logging as py_logging
import tensorflow.compat.v1 as tf
from contextlib import contextmanager
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Disable GPUs
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Set up logging
tf.get_logger().propagate = False
py_logging.root.setLevel('INFO')
@contextmanager
def tf_verbosity_level(level):
    og_level = tf.logging.get_verbosity()
    tf.logging.set_verbosity(level)
    yield
    tf.logging.set_verbosity(og_level)

parser = argparse.ArgumentParser(description='Finetune T5')
parser.add_argument('-datasets', nargs='+', type=str, required=True,
                    help='Names of dataset(s) as defined in datasets.json')
parser.add_argument('-model_size', type=str, default="small", choices=["small", "t5.1.1.small", "base", "large", "3B", "11B"],
                    help='Model size. Match model size used in training')
parser.add_argument('-models_dir', type=str, default="models",
                    help='Where model checkpoints are stored. Start with gs:// to upload to google cloud platform')
parser.add_argument('-in_len', type=int, default=2048,
                    help='Maximum length of input. Inputs will be padded to this length.')
parser.add_argument('-out_len', type=int, default=512,
                    help='Maximum length of output. Outputs will be padded to this length.')

# There are already defaults for these values per model size. These are simply overrides.
parser.add_argument('-batch_size', type=int, default=None,
                    help='Batches per step')
parser.add_argument('-max_checkpoints', type=int, default=None,
                    help='The maximum number of checkpoints to save at once')
parser.add_argument('-storemode', type=str, default="gs", choices=["gs", "local"],
                    help='Whee is the dataset and checkpoint saved? Local or google cloud storage.')
parser.add_argument('-model_paralellism', type=int, default=None,
                    help='Contrary to data paralellism, model paralellism splits a model up into each accelerator, helping memory usage but reducing overall model efficiency.')
args = parser.parse_args()

print("All devices: ", tf.config.list_logical_devices('GPU'))

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

MODEL_SIZE = args.model_size
MODEL_DIR = os.path.join(args.models_dir, MODEL_SIZE)

# Set parallelism and batch size to fit on v2-8 TPU (if possible).
# Limit number of checkpoints to fit within 5GB (if possible).
try:
    model_parallelism, train_batch_size, keep_checkpoint_max = {
        "small": (1, 512, 4),
        "t5.1.1.small": (1, 512, 4),
        "base": (2, 256, 2),
        "large": (4, 128, 2),
        "3B": (8, 16, 1),
        "11B": (8, 4, 1)}[MODEL_SIZE]
except:
    model_parallelism, train_batch_size, keep_checkpoint_max=None,None,None
    assert args.model_paralellism and args.batch_size and args.max_checkpoints, "Model not found in supported list. Cannot determine model paralellism, batch size, and number of checkpoints to keep automatically."
if args.model_paralellism: model_paralellism=args.model_paralellism
if args.batch_size: train_batch_size=args.batch_size
if args.max_checkpoints: keep_checkpoint_max=args.max_checkpoints

tf.io.gfile.makedirs(MODEL_DIR)
tf.io.gfile.makedirs(os.path.join(MODEL_DIR, "validation_eval"))
# The models from our paper are based on the Mesh Tensorflow Transformer.

model = t5.models.MtfModel(
    model_dir=MODEL_DIR,
    tpu=None,
    model_parallelism=model_parallelism,
    batch_size=train_batch_size,
    iterations_per_loop=500,
)

model.eval(
    mixture_or_task_name="all_mix",
    checkpoint_steps="all"
)