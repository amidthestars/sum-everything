import os
import t5
import seqio
import functools
from termcolor import cprint
from google.cloud import storage
import tensorflow.compat.v1 as tf
import tensorflow_datasets as tfds

DEFAULT_OUTPUT_FEATURES = {
    "inputs":
        seqio.Feature(
            vocabulary=t5.data.get_default_vocabulary(), add_eos=True),
    "targets":
        seqio.Feature(
            vocabulary=t5.data.get_default_vocabulary(), add_eos=True)
}

global splits, bucket, taskname, compressiontype, storemode
splits, bucket, taskname, compressiontype, storemode = {"train": None, "validation": None}, None, None, None, "local"

def init(bucket_path, train_path, validation_path, task_name, compression_type=None, store_mode="local"):
    global splits, bucket, taskname, compressiontype, storemode
    splits, bucket, taskname, compressiontype, storemode = {"train": train_path, "validation": validation_path}, bucket_path, task_name, compression_type, store_mode
    cprint(f"Registering {'gs' if bucket.startswith('gs://') else 'local'} task \"{taskname}\": {taskname}", 'cyan', attrs=['bold'])
    seqio.TaskRegistry.add(
        taskname,
        # Specify the task source.
        source=seqio.FunctionDataSource(
            # Supply a function which returns a tf.data.Dataset.
            dataset_fn=dataset_fn if bucket.startswith("gs://") else dataset_fn_local,
            splits=["train", "validation"]),
        # Supply a list of functions that preprocess the input tf.data.Dataset.
        preprocessors=[
            preprocess,
            seqio.preprocessors.tokenize_and_append_eos,
        ],
        # Lowercase targets before computing metrics.
        postprocess_fn=t5.data.postprocessors.lower_text,
        # We'll use accuracy as our evaluation metric.
        metric_fns=[t5.evaluation.metrics.accuracy],
        output_features=DEFAULT_OUTPUT_FEATURES,
    )

def sample(num_samples, split, max_in=256, max_out=64):
    global taskname
    ds = seqio.TaskRegistry.get(taskname).get_dataset(split=split, sequence_length={"inputs": max_in, "targets": max_out})
    return list(tfds.as_numpy(ds.take(num_samples)))

def dataset_fn(split, shuffle_files=False):
    del shuffle_files
    client = storage.Client()
    global splits, bucket, compressiontype
    # Load lines from the text file as examples.
    files_to_read=[os.path.join(bucket,str(filename.name)) for filename in client.list_blobs(bucket[5:], prefix=splits[split]) if filename.name.endswith(split)]
    cprint(f"Split {split} contains {len(files_to_read)} shards:\nFirst 10: {files_to_read[0:10]}", 'cyan', attrs=['bold'])
    ds = tf.data.TextLineDataset(files_to_read, compression_type=compressiontype).filter(lambda line:tf.not_equal(tf.strings.length(line),0))
    # Split each "<question>\t<answer>" example into (question, answer) tuple.
    ds = ds.shuffle(buffer_size=100000)
    ds = ds.map(functools.partial(tf.io.decode_csv, record_defaults=["",""], field_delim="\t", use_quote_delim=False),
                num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds = ds.map(lambda *ex: dict(zip(["question", "answer"], ex)))
    return ds

def dataset_fn_local(split, shuffle_files=False):
    del shuffle_files
    global splits, bucket, compressiontype
    # Load lines from the text file as examples.
    files_to_read=[os.path.join(bucket, splits[split],filename) for filename in os.listdir(os.path.join(bucket, splits[split])) if filename.endswith(split)]
    cprint(f"Split {split} contains {len(files_to_read)} shards.\nFirst 10: {files_to_read[0:10]}", 'cyan', attrs=['bold'])
    ds = tf.data.TextLineDataset(files_to_read, compression_type=compressiontype).filter(lambda line:tf.not_equal(tf.strings.length(line),0))
    # Split each "<question>\t<answer>" example into (question, answer) tuple.
    ds = ds.shuffle(buffer_size=100000)
    ds = ds.map(functools.partial(tf.io.decode_csv, record_defaults=["",""], field_delim="\t", use_quote_delim=False),
                num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds = ds.map(lambda *ex: dict(zip(["question", "answer"], ex)))
    return ds

def preprocess(ds):
    def to_inputs_and_targets(ex):
        """Map {"question": ..., "answer": ...}->{"inputs": ..., "targets": ...}."""
        return {
            "inputs": ex["question"],
            "targets": ex["answer"]
        }
    return ds.map(to_inputs_and_targets, num_parallel_calls=tf.data.experimental.AUTOTUNE)

if __name__ == "__main__":
    init("../../datasets/", "scisummnet", "scisummnet", task_name="scisummnet_task")