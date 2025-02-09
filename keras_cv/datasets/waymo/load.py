# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Data loader for the Waymo Open Dataset."""
import os

import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow_datasets.proto.waymo_dataset_generated_pb2 import Frame


def _generate_frames(segments, transformer):
    def _generator():
        for record in tfds.as_numpy(segments):
            frame = Frame()
            frame.ParseFromString(record)
            yield transformer(frame)

    return _generator


def load(tfrecord_path, transformer, output_signature):
    """
    Loads the Waymo Open Dataset and transforms frames into features as
    tensors.

    Args:
        tfrecord_path: a string pointing to the directory containing the raw
            tfrecords in the Waymo Open Dataset, or a list of strings pointing
            to the tfrecords themselves
        transformer: a Python function which transforms a Waymo Open Dataset
           Frame object into tensors.
        output_signature: the type specification of the tensors created by the
            transformer. This is often a dictionary from feature column names
            to tf.TypeSpecs.

    Returns:
        tf.data.Dataset containing the features extracted from Frames using the
        provided transformer.

    Example:

    ```python
    from keras_cv.datasets.waymo import load

    def simple_transformer(frame):
        return {"timestamp_micros": frame.timestamp_micros}

    output_signature = {"timestamp_micros": tf.TensorSpec((), tf.int64)}
    load("/path/to/tfrecords", simple_transformer, output_signature)
    ```
    """
    if type(tfrecord_path) == list:
        filenames = tfrecord_path
    else:
        filenames = tf.data.TFRecordDataset.list_files(
            os.path.join(tfrecord_path, "*.tfrecord")
        )
    segments = tf.data.TFRecordDataset(filenames)
    return tf.data.Dataset.from_generator(
        _generate_frames(segments, transformer), output_signature=output_signature
    )
