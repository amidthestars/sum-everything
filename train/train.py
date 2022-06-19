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
py_logging.getLogger("tensorflow").setLevel(py_logging.INFO)
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
parser.add_argument('-gpus', nargs='+', type=str, default=None,
                    help='Available GPUs. Input format: "-gpus gpu:0 gpu:1 "...')
parser.add_argument('-tpu', type=str, default=None,
                    help='TPU ip address. None if using GPU. \
                            local if TPU is attached to the local instance.')
parser.add_argument('-tpu_topology', type=str, default=None, choices=["v2-8", "v3-8", None],
                    help='TPU type. None if using GPU')
parser.add_argument('-in_len', type=int, default=2048,
                    help='Maximum length of input. Inputs will be padded to this length.')
parser.add_argument('-out_len', type=int, default=512,
                    help='Maximum length of output. Outputs will be padded to this length.')
parser.add_argument('-steps', type=int, default=50000,
                    help='Number of steps to train for')
parser.add_argument('-model_size', type=str, default="small",
                    choices=["small", "t5.1.1.small", "base", "large", "3B", "11B"],
                    help='Model size. Small is generally reccomended.')
parser.add_argument('-evaluate_after', type=int, default=500,
                    help='Calcuates the loss after this value')
parser.add_argument('-save_after', type=int, default=2500,
                    help='How many steps before saving a checkpoint')
parser.add_argument('-models_dir', type=str, default="models",
                    help='Where model checkpoints are stored. \
                            Start with gs:// to upload to google cloud platform')
parser.add_argument('-pretrained_dir', type=str, default="gs://t5-data/pretrained_models",
                    help='Where pretrained models are stored')

# There are already defaults for these values per model size. These are simply overrides.
parser.add_argument('-batch_size', type=int, default=None,
                    help='Batches per step')
parser.add_argument('-max_checkpoints', type=int, default=None,
                    help='The maximum number of checkpoints to save at once')
parser.add_argument('-model_paralellism', type=int, default=None,
                    help='Contrary to data paralellism, model paralellism splits a model up into each accelerator, \
                            helping memory usage but reducing overall model efficiency.')
FLAGS = tf.app.flags.FLAGS
try:
  argv = FLAGS(sys.argv, known_only=True)  # parse flags
except tf.app.flags.Error as e:
  print("hello")
  sys.exit(1)

args = parser.parse_args()

if args.gpus:
    assert not args.tpu and not args.tpu_topology, "Cannot set TPU variables if using GPU"
if args.tpu and args.tpu_topology:
    assert not args.gpus, "Cannot set GPU variables if using TPU"

# Register dataset as a mixture
ds_registrar_spec = importlib.util.find_spec('src.createtask')
datasets = json.load(open("datasets.json", "r"))
for dataset in args.datasets:
    if dataset in datasets:
        info = datasets[dataset]
        new_ds = importlib.util.module_from_spec(ds_registrar_spec)
        ds_registrar_spec.loader.exec_module(new_ds)
        sys.modules['new_ds'] = new_ds
        new_ds.init(info["bucket_path"], info["train_path"], info["validation_path"],
                    dataset, info["compression_type"], info["store_mode"])
    else:
        warnings.warn(f"Dataset {dataset} was not in datasets.json, and will not be included.")
        args.datasets.remove(dataset)

seqio.MixtureRegistry.add(
    "all_mix",
    args.datasets,
    default_rate=1.0
)

if args.tpu is not None:
    if args.tpu != 'local':
        args.tpu = f"grpc://{args.tpu}:8470"
    tpu = tf.distribute.cluster_resolver.TPUClusterResolver(tpu=args.tpu)
    tf.enable_eager_execution()
    tf.config.experimental_connect_to_cluster(tpu)
    tf.tpu.experimental.initialize_tpu_system(tpu)
    print("All devices: ", tf.config.list_logical_devices('TPU'))
    tf.disable_v2_behavior()
else:
    print("All devices: ", tf.config.list_logical_devices('GPU'))

MODEL_SIZE = args.model_size
PRETRAINED_DIR = os.path.join(args.pretrained_dir, MODEL_SIZE)
MODEL_DIR = os.path.join(args.models_dir, MODEL_SIZE)

# Set parallelism and batch size to fit on v2-8 TPU (if possible).
# Limit number of checkpoints to fit within 5GB (if possible).
if args.tpu and args.tpu_topology:
    model_parallelism, train_batch_size, keep_checkpoint_max = {
        "small": (1, 512, 2),
        "t5.1.1.small": (1, 512, 2),
        "base": (2, 256, 2),
        "large": (4, 128, 2),
        "3B": (8, 16, 1),
        "11B": (8, 4, 1)}[MODEL_SIZE]
else:
    model_parallelism, train_batch_size, keep_checkpoint_max = {
        "small": (1, 64, 2),
        "t5.1.1.small": (1, 64, 2),
        "base": (2, 16, 2)}[MODEL_SIZE]

if args.model_paralellism:
    model_paralellism = args.model_paralellism
if args.batch_size:
    train_batch_size = args.batch_size
if args.max_checkpoints:
    keep_checkpoint_max = args.max_checkpoints

tf.io.gfile.makedirs(MODEL_DIR)

if args.tpu:
    model = t5.models.MtfModel(
        model_dir=MODEL_DIR,
        tpu=args.tpu,
        tpu_topology=args.tpu_topology,
        model_parallelism=model_parallelism,
        batch_size=train_batch_size,
        sequence_length={"inputs": args.in_len, "targets": args.out_len},
        learning_rate_schedule=0.001,
        save_checkpoints_steps=args.save_after,
        keep_checkpoint_max=keep_checkpoint_max,
        iterations_per_loop=args.evaluate_after,
    )
elif args.gpus:
    model = t5.models.MtfModel(
        model_dir=MODEL_DIR,
        tpu=None,
        mesh_devices=args.gpus,
        mesh_shape=f'model:1,batch:{len(args.gpus)}',
        model_parallelism=model_parallelism,
        batch_size=train_batch_size,
        sequence_length={"inputs": args.in_len, "targets": args.out_len},
        learning_rate_schedule=0.001,
        save_checkpoints_steps=args.save_after,
        keep_checkpoint_max=keep_checkpoint_max,
        iterations_per_loop=args.evaluate_after,
    )
else:
    raise NotImplementedError("Running with no accelerators is not a supported case.")

model.finetune(
    mixture_or_task_name="all_mix",
    pretrained_model_dir=PRETRAINED_DIR,
    finetune_steps=args.steps
)
