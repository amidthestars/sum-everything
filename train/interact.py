import tensorflow as tf
import tensorflow_text  # Required to run exported model.
import argparse

parser = argparse.ArgumentParser(description='Interact with T5')
parser.add_argument('-dir', type=str, help='Folder containing the serving model', required=True)
parser.add_argument('-inp', type=str, help='File containing some test data', default=None)
args = parser.parse_args()

def load_predict_fn(model_path):
  if tf.executing_eagerly():
    print("Loading SavedModel in eager mode.")
    imported = tf.saved_model.load(model_path, ["serve"])
    return lambda x: imported.signatures['serving_default'](tf.constant(x))['outputs'].numpy()
  else:
    print("Loading SavedModel in tf 1.x graph mode.")
    tf.compat.v1.reset_default_graph()
    sess = tf.compat.v1.Session()
    meta_graph_def = tf.compat.v1.saved_model.load(sess, ["serve"], model_path)
    signature_def = meta_graph_def.signature_def["serving_default"]
    return lambda x: sess.run(
        fetches=signature_def.outputs["outputs"].name, 
        feed_dict={signature_def.inputs["inputs"].name: x}
    )

predict_fn = load_predict_fn(args.dir)


def run_inference(inp):
    ret=predict_fn([inp, inp, inp])
    return [i.decode('utf-8').replace("/n", "\n") for i in ret]
        
if __name__ == "__main__":
    if args.inp:
        print("\n")
        for inference in run_inference(open(args.inp, "r").read()):
            print(f"{inference}\n")
    else:
        while True:
            inp = input("> ")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(run_inference(inp))
            print("\n")
