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
parser.add_argument('-gpus', nargs='+', type=str, default=None,
                    help='Available GPUs. Input format: "-gpus gpu:0 gpu:1 "...')
parser.add_argument('-tpu', type=str, default=None,
                    help='TPU ip address. None if using GPU. local if TPU is attached to the local instance.')
parser.add_argument('-tpu_topology', type=str, default=None, choices=["v2-8","v3-8", None],
                    help='TPU type. None if using GPU')
parser.add_argument('-models_dir', type=str, default="models",
                    help='Where model checkpoints are stored. Start with gs:// to upload to google cloud platform')
parser.add_argument('-in_len', type=int, default=2048,
                    help='Maximum length of input. Inputs will be padded to this length.')
parser.add_argument('-out_len', type=int, default=512,
                    help='Maximum length of output. Outputs will be padded to this length.')
parser.add_argument('-evaluate_after', type=int, default=100,
                    help='Calcuates the loss after this value')

# There are already defaults for these values per model size. These are simply overrides.
parser.add_argument('-batch_size', type=int, default=None,
                    help='Batches per step')
parser.add_argument('-model_paralellism', type=int, default=None,
                    help='Contrary to data paralellism, model paralellism splits a model up into each accelerator, helping memory usage but reducing overall model efficiency.')
args = parser.parse_args()

if args.tpu != None:
    if args.tpu != 'local':
        args.tpu = f"grpc://{args.tpu}:8470"
    tpu = tf.distribute.cluster_resolver.TPUClusterResolver(tpu=args.tpu)
    tf.enable_eager_execution()
    tf.config.experimental_connect_to_cluster(tpu)
    tf.tpu.experimental.initialize_tpu_system(tpu)
    tf.disable_v2_behavior()

print("All CPU: ", tf.config.list_logical_devices('CPU'))
print("All GPU: ", tf.config.list_logical_devices('GPU'))
print("All TPU: ", tf.config.list_logical_devices('TPU'))

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

model_parallelism, eval_batch_size = 1, 256
if args.model_paralellism: model_paralellism=args.model_paralellism
if args.batch_size: eval_batch_size=args.batch_size

tf.io.gfile.makedirs(MODEL_DIR)
tf.io.gfile.makedirs(os.path.join(MODEL_DIR, "validation_eval"))
# The models from our paper are based on the Mesh Tensorflow Transformer.

if args.tpu:
    model = t5.models.MtfModel(
        model_dir=MODEL_DIR,
        tpu=args.tpu,
        tpu_topology=args.tpu_topology,
        model_parallelism=model_parallelism,
        batch_size=eval_batch_size,
        sequence_length={"inputs": args.in_len, "targets": args.out_len},
        iterations_per_loop=args.evaluate_after,
    )
elif args.gpus:
    model = t5.models.MtfModel(
        model_dir=MODEL_DIR,
        tpu=None,
        mesh_devices=args.gpus,
        mesh_shape=f'model:1,batch:{len(args.gpus)}',
        model_parallelism=model_parallelism,
        batch_size=eval_batch_size,
        sequence_length={"inputs": args.in_len, "targets": args.out_len},
        iterations_per_loop=args.evaluate_after,
    )
else:
    print("WARNING: Running with no accelerators is not a supported case, and may be very slow")
    model = t5.models.MtfModel(
        model_dir=MODEL_DIR,
        tpu=None,
        model_parallelism=model_parallelism,
        batch_size=eval_batch_size,
        sequence_length={"inputs": args.in_len, "targets": args.out_len},
        iterations_per_loop=args.evaluate_after,
    )

model.eval(
    mixture_or_task_name="all_mix",
    checkpoint_steps="all",
    compute_sequence_length=False
)