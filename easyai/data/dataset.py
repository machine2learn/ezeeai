from tensorflow.python.data.experimental.ops.readers import dataset_ops, dtypes, constant_op, interleave_ops, \
    _get_sorted_col_indices, CsvDataset, _maybe_shuffle_and_repeat
from tensorflow.python.data.experimental.ops.readers import _infer_column_defaults, _infer_column_names, _get_file_names
import tensorflow as tf
import collections
from tensorflow.python.data.experimental.ops import optimization

_ACCEPTABLE_CSV_TYPES = (dtypes.float32, dtypes.float64, dtypes.int32,
                         dtypes.int64, dtypes.string)


def get_dataset_length(dataset):
    if hasattr(dataset, '_tensors'):
        value = dataset._tensors[0][0].shape[0].value if isinstance(dataset._tensors[0], (list, tuple)) else \
            dataset._tensors[0].shape[0].value
        return value
    return get_dataset_length(dataset._input_dataset)


class Dataset:
    def __init__(self, data, size, val_size=None, shuffle=True, batch_size=32, shuffle_buffer_size=10000,
                 test_size=None):
        self.assert_dataset(data)
        self._dataset_size = size  # get_dataset_length(data)

        self.training = data
        self.validation = None
        self.test = None

        self._shuffle = shuffle
        self._batch_size = batch_size
        self._shuffle_buffer_size = shuffle_buffer_size
        self._val_size = val_size or int(round(0.05 * self._dataset_size))
        self._test_size = test_size

        self._split_dataset()

    @staticmethod
    def assert_dataset(data):
        if not isinstance(data, tf.data.Dataset):
            raise TypeError(f'data must be a tf.data.Dataset, not {data.__class__}')

    def _split_dataset(self):
        full_dataset = self.training
        full_dataset.shuffle(self._shuffle_buffer_size, seed=42)

        if self._test_size is not None:
            train_size = self._dataset_size - self._val_size - self._test_size
            self.training = full_dataset.take(train_size)
            remaining = full_dataset.skip(train_size)
            self.validation = remaining.take(self._val_size)
            self.test = remaining.skip(self._val_size)
        else:
            train_size = self._dataset_size - self._val_size
            self.training = full_dataset.take(train_size)
            self.validation = full_dataset.skip(train_size)

    def training_data(self):
        return self.training.shuffle(self._shuffle_buffer_size).batch(self._batch_size).repeat()

    def validation_data(self):
        return self.validation.batch(self._batch_size)

    def test_data(self):
        return self.test


def make_csv_dataset(
        file_pattern,
        batch_size,
        column_names=None,
        column_defaults=None,
        label_names=None,
        select_columns=None,
        field_delim=",",
        use_quote_delim=True,
        na_value="",
        header=True,
        num_epochs=True,
        shuffle=True,
        shuffle_buffer_size=10000,
        shuffle_seed=None,
        prefetch_buffer_size=optimization.AUTOTUNE,
        num_parallel_reads=1,
        sloppy=False,
        num_rows_for_inference=100,
        compression_type=None):
    # Create dataset of all matching filenames
    filenames = _get_file_names(file_pattern, False)
    dataset = dataset_ops.Dataset.from_tensor_slices(filenames)

    # Clean arguments; figure out column names and defaults

    if column_names is None:
        if not header:
            raise ValueError("Cannot infer column names without a header line.")
        # If column names are not provided, infer from the header lines
        column_names = _infer_column_names(filenames, field_delim, use_quote_delim)
    if len(column_names) != len(set(column_names)):
        raise ValueError("Cannot have duplicate column names.")

    if select_columns is not None:
        select_columns = _get_sorted_col_indices(select_columns, column_names)

    if column_defaults is not None:
        column_defaults = [
            constant_op.constant([], dtype=x) if x in _ACCEPTABLE_CSV_TYPES else x
            for x in column_defaults
        ]
    else:
        # If column defaults are not provided, infer from records at graph
        # construction time
        column_defaults = _infer_column_defaults(
            filenames, len(column_names), field_delim, use_quote_delim, na_value,
            header, num_rows_for_inference, select_columns)

    if select_columns is not None and len(column_defaults) != len(select_columns):
        raise ValueError(
            "If specified, column_defaults and select_columns must have same "
            "length."
        )
    if select_columns is not None and len(column_names) > len(select_columns):
        # Pick the relevant subset of column names
        column_names = [column_names[i] for i in select_columns]

    if label_names is None:
        raise ValueError("`label_name` provided must be one of the columns.")
    if isinstance(label_names, (list, tuple)):
        for l in label_names:
            if l not in column_names:
                raise ValueError("`label_name` provided must be one of the columns.")
    else:
        if label_names not in column_names:
            raise ValueError("`label_name` provided must be one of the columns.")

    def filename_to_dataset(filename):
        return CsvDataset(
            filename,
            record_defaults=column_defaults,
            field_delim=field_delim,
            use_quote_delim=use_quote_delim,
            na_value=na_value,
            select_cols=select_columns,
            header=header,
            compression_type=compression_type,
        )

    def map_fn(*columns):
        """Organizes columns into a features dictionary.
        Args:
          *columns: list of `Tensor`s corresponding to one csv record.
        Returns:
          An OrderedDict of feature names to values for that particular record. If
          label_name is provided, extracts the label feature to be returned as the
          second element of the tuple.
        """
        features = collections.OrderedDict(zip(column_names, columns))
        if label_names is not None:
            if isinstance(label_names, (list, tuple)):
                labels = []
                for l in label_names:
                    labels.append(features.pop(l))
                return features, tf.stack(labels, 1)
            else:
                labels = features.pop(label_names)
                return features, labels

        return features

    # Read files sequentially (if num_parallel_reads=1) or in parallel
    dataset = dataset.apply(
        interleave_ops.parallel_interleave(
            filename_to_dataset, cycle_length=num_parallel_reads, sloppy=sloppy))
    dataset = _maybe_shuffle_and_repeat(dataset, num_epochs, shuffle, shuffle_buffer_size, shuffle_seed)
    dataset = dataset.batch(batch_size=batch_size,
                            drop_remainder=num_epochs is None)

    # Apply batch before map for perf, because map has high overhead relative
    # to the size of the computation in each map.
    # NOTE(mrry): We set `drop_remainder=True` when `num_epochs is None` to
    # improve the shape inference, because it makes the batch dimension static.
    # It is safe to do this because in that case we are repeating the input
    # indefinitely, and all batches will be full-sized.

    dataset = dataset_ops.MapDataset(
        dataset, map_fn, use_inter_op_parallelism=False)
    dataset = dataset.prefetch(prefetch_buffer_size)

    return dataset
