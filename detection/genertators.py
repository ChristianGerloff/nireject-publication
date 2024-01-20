"""
Generates different data conditions
"""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: see repository LICENSE file


import numpy as np
import pandas as pd


def _check_labels(labels: np.ndarray):
    """Check if labels are binary and ensure type is np.ndarray

    Args:
        labels (np.ndarray): array of labels

    Raises:
        ValueError: if labels are not binary
    """
    labels = np.asarray(labels)
    if not np.array_equal(np.unique(labels), [0, 1]):
        raise ValueError('Labels are not binary')
    return labels


def _np_pandas_consitency_check(labels, shuffled_labels, shuffled_idx):
    """Check if numpy and pandas series are consistent

    Args:
        labels (): original labels
        shuffled_labels (np.ndarray): shuffled labels
        shuffled_idx (np.ndarray): indices of shuffled labels

    Raises:
        AssertionError: if numpy and pandas array are not consistent
    """

    # check if labels is a dataframe
    if isinstance(labels, pd.Series):
        # assign values of shuffled_labels
        labels.iloc[shuffled_idx] = shuffled_labels[shuffled_idx]
    else:
        labels = shuffled_labels

    return labels


def binary_label_shuffling(labels: np.ndarray,
                           shuffled_idx: np.ndarray = None,
                           noise_ratio: float = 0.1,
                           seed: int = None):
    """Shuffle labels across both classes

    Args:
        labels (np.ndarray): array of labels
        shuffled_idx (np.ndarray): indices of shuffled labels. If None, it will be generated.
        noise_ratio (float): percentage of labels to be
            shuffled

    Returns:
        np.ndarray: shuffled labels
        np.ndarray: indices of shuffled labels
    """
    if noise_ratio <= 0.0 and shuffled_idx is None:
        return labels, shuffled_idx

    shuffled_labels = _check_labels(labels)

    if seed is not None:
        np.random.seed(seed)
    # labels are shuffled across the binary classes with p (i.e., noise ratio)
    if shuffled_idx is None:
        shuffled_idx = np.random.choice(
            np.arange(len(shuffled_labels)),
            int(len(shuffled_labels) * noise_ratio),
            replace=False)

    # shuffle labels in numpy array
    shuffled_labels[shuffled_idx] = 1 - shuffled_labels[shuffled_idx]

    # check if labels is a dataframe
    labels = _np_pandas_consitency_check(labels, shuffled_labels, shuffled_idx)

    return labels, shuffled_idx


def preserving_badchannel_label_shuffling(labels: np.ndarray,
                                          shuffled_idx: np.ndarray = None,
                                          noise_ratio: float = 0.1,
                                          seed: int = None):
    """Shuffle labels across both classes while preserving label distribution of badchannels.

    Args:
        labels (np.ndarray): array of labels
        shuffled_idx (np.ndarray): indices of shuffled labels. If None, it will be generated.
            Defaults to 0.1.
        noise_ratio (float, optional): percentage of labels to be
            shuffled. Defaults to 0.1.
        seed (int, optional): seed for random number generator. Defaults to None.

    Returns:
        np.ndarray: shuffled labels
        dict: dictionary that maps the index of original
            labels to the index of shuffled labels. Defaults to None
    """

    if noise_ratio <= 0.0 and shuffled_idx is None:
        return labels, shuffled_idx

    if seed is not None:
        np.random.seed(seed)

    shuffled_labels = _check_labels(labels)

    # create lookup dictionary
    if shuffled_idx is None:

        # get indices of labels
        normal_idx = np.where(shuffled_labels == 0)[0]
        bad_idx = np.where(shuffled_labels == 1)[0]

        # number of shuffle badchannels
        n_shuffled = int(noise_ratio * len(bad_idx))

        # random sample of indices to be shuffled for badchannels
        bad_shuffled_idx = np.random.choice(
            bad_idx,
            n_shuffled,
            replace=False
        )

        # random sample of indices to not to be shuffled of normal data
        normal_shuffled_idx = np.random.choice(
            normal_idx,
            n_shuffled,
            replace=False,
        )

        # concernate indices of shuffled data
        shuffled_idx = np.concatenate((bad_shuffled_idx, normal_shuffled_idx))

    # shuffle labels in numpy array
    shuffled_labels[shuffled_idx] = 1 - shuffled_labels[shuffled_idx]

    # check if labels is a dataframe
    labels = _np_pandas_consitency_check(labels, shuffled_labels, shuffled_idx)

    # ToDO export to Unit tests
    if isinstance(labels, pd.Series) and 'bad_shuffled_idx' in locals():
        # assert that every label with index in bad_shuffled_idx is 0
        assert all(labels.iloc[bad_shuffled_idx] == 0)
        assert all(labels.iloc[normal_shuffled_idx] == 1)

    return labels, shuffled_idx


def preserving_binary_label_shuffling(labels: np.ndarray,
                                      shuffling_lookup: dict = None,
                                      noise_ratio: float = 0.1,
                                      seed: int = None):
    """Shuffle labels across both classes while preserving label distribution.

    Args:
        labels (np.ndarray): array of labels
        shuffling_lookup (dict, optional): dictionary that maps the index of original
            labels to the index of shuffled labels. Defaults to None.
        noise_ratio (float, optional): percentage of labels to be
            shuffled. Defaults to 0.1.
        seed (int, optional): seed for random number generator. Defaults to None.

    Returns:
        np.ndarray: shuffled labels
        dict: dictionary that maps the index of original
            labels to the index of shuffled labels. Defaults to None
    """

    if noise_ratio <= 0.0:
        return labels, shuffling_lookup

    if seed is not None:
        np.random.seed(seed)

    labels = _check_labels(labels)

    # create lookup dictionary
    if shuffling_lookup is None:
        # get indices of labels
        idx_0 = np.where(labels == 0)[0]
        idx_1 = np.where(labels == 1)[0]

        # random sample of indices to be shuffled per class
        shuffled_idx_0 = np.random.choice(
            idx_0,
            int(noise_ratio * len(idx_0)),
            replace=False
        )
        shuffled_idx_1 = np.random.choice(
            idx_1,
            int(noise_ratio * len(idx_1)),
            replace=False
        )

        # random sample of indices to not to be shuffled per class
        not_shuffled_idx_0 = np.setdiff1d(idx_0, shuffled_idx_0)
        not_shuffled_idx_1 = np.setdiff1d(idx_1, shuffled_idx_1)
        pair_0 = np.random.choice(
            not_shuffled_idx_1,  # important from 1!
            int(noise_ratio * len(idx_0)),
            replace=True  # required as not_shuffled_idx_1 might be smaller
        )
        pair_1 = np.random.choice(
            not_shuffled_idx_0,  # important from 0!
            int(noise_ratio * len(idx_1)),
            replace=False
        )

        shuffling_lookup = {}
        for idx, i in enumerate(shuffled_idx_0):
            shuffling_lookup[i] = pair_0[idx]
        for idx, i in enumerate(shuffled_idx_1):
            shuffling_lookup[i] = pair_1[idx]

    # shuffling based on keys of lookup dictionary
    shuffled_labels = np.copy(labels)
    for key, value in shuffling_lookup.items():
        shuffled_labels[key] = labels[value]
        shuffled_labels[value] = labels[key]
    return shuffled_labels, shuffling_lookup


def _unlabel(data, unlabel_idx: np.ndarray):
    """Unlabel data.

    Args:
        data: data to unlabel.
        unlabel_idx (np.ndarray): indices of data to unlabel.

    Returns:
        np.ndarray: unlabeld data.
    """

    # check if data depends on pandas
    if (isinstance(data, pd.Series) or
       isinstance(data, pd.DataFrame)):

        # get pandas index of unlabelled data
        unlabel_idx = data.index[unlabel_idx]

        # frop unlabelled data by index
        data = data.drop(unlabel_idx)

    else:
        data = np.delete(data, unlabel_idx, axis=0)

    return data


def _add_label(data, idx: np.ndarray):
    """add data.

    Args:
        data: data to unlabel.
        idx (np.ndarray): indices of data to add.

    Returns:
        np.ndarray: extened data.
    """

    # check if data depends on pandas
    if (isinstance(data, pd.Series) or
       isinstance(data, pd.DataFrame)):

        # get pandas index of unlabelled data
        idx = data.index[idx]

        # concat data by rows from idx
        data = pd.concat([data, data[idx]])
    elif isinstance(data, pd.Index):
        # append index
        data = data.append(data[idx])
    else:
        data = np.concatenate((data, data[idx]), axis=0)

    return data


def set_perc_rated(data,
                   labels,
                   idx,
                   gamma: float = 1.0,
                   unlabel_idx: np.ndarray = None,
                   seed: int = None):
    """ Set percentage of labels to be rated.
        Apply only to train data.

    Args:
        data (_type_): rated dataset.
        labels (_type_): labels of rated dataset.
        idx (_type_): indices of rated dataset.
        gamma (float): percentage of rated badchannels of dataset.
            Defaults to 1.0.
        unlabel_idx (np.ndarray): unlabelled indices of dataset.
            Defaults to None.
        seed (int): seed for random number generator. Defaults to None.
    """

    if ((gamma <= 0.0 and unlabel_idx is None) or
       (gamma >= 1.0 and unlabel_idx is None)):
        return data, labels, idx, unlabel_idx

    if seed is not None:
        np.random.seed(seed)

    # get number of observations for sanity check
    data_shape = data.shape[0]
    labels_shape = labels.shape[0]
    idx_shape = idx.shape[0]

    # convert labels to numpy array
    label_array = _check_labels(labels)

    # create lookup dictionary
    if unlabel_idx is None:

        # get indices of labels
        bad_idx = np.where(label_array == 1)[0]

        # number labeled badchannels
        n_labeled = int(gamma * len(bad_idx))
        n_unlabelled = len(bad_idx) - n_labeled

        # random sample of indices to be unlabelled for badchannels
        bad_unlabelled_idx = np.random.choice(
            bad_idx,
            n_unlabelled,
            replace=False
        )
        unlabel_idx = bad_unlabelled_idx

    # unlabel
    data = _unlabel(data, unlabel_idx)
    labels = _unlabel(labels, unlabel_idx)
    idx = _unlabel(idx, unlabel_idx)

    # check if shape has changed as expected
    # ToDO add to unit tests
    assert data_shape - len(unlabel_idx) == data.shape[0]
    assert labels_shape - len(unlabel_idx) == labels.shape[0]
    assert idx_shape - len(unlabel_idx) == idx.shape[0]

    return data, labels, idx, unlabel_idx


def set_contamination_rate(data,
                           labels,
                           idx,
                           contamination: float = 0.1,
                           remove_idx: np.ndarray = None,
                           add_idx: np.ndarray = None,
                           seed: int = None):
    """Set contamination rate of data.
        Apply to both taind and test data.

    Args:
        data (_type_): dataset.
        labels (_type_): labels of dataset.
        idx (_type_): indices of dataset.
        contamination (float): contamination rate of dataset.
            Defaults to 0.1.
        remove_idx (np.ndarray):    indices of data to remove.
            Defaults to None.
        add_idx (np.ndarray): indices of data to add.
            Defaults to None.
        seed (int): seed for random number generator.
            Defaults to None.
    """
    if ((contamination <= 0.0 and remove_idx is None and add_idx is None) or
       (contamination >= 1.0 and remove_idx is None and add_idx is None)):
        return data, labels, idx, remove_idx, add_idx

    if seed is not None:
        np.random.seed(seed)

    # convert labels to numpy array
    label_array = _check_labels(labels)

    # create lookup dictionary
    if remove_idx is None and add_idx is None:

        # get indices of labels
        bad_idx = np.where(label_array == 1)[0]
        current_contamination = len(bad_idx) / len(label_array)

        # number remaining badchannels
        n_labeled = int(contamination * len(label_array))
        if current_contamination > contamination:
            n_remove = len(bad_idx) - n_labeled

            # random sample of indices to be unlabelled for badchannels
            remove_idx = np.random.choice(
                bad_idx,
                n_remove,
                replace=False
            )
            # avoid empty array
            if len(remove_idx) == 0:
                remove_idx = None

        elif current_contamination < contamination:
            n_add = n_labeled - len(bad_idx)

            # random sample of indices to be unlabelled for badchannels
            add_idx = np.random.choice(
                bad_idx,
                n_add,
                replace=True
            )
            # avoid empty array
            if len(add_idx) == 0:
                add_idx = None
    if remove_idx is not None:
        data = _unlabel(data, remove_idx)
        labels = _unlabel(labels, remove_idx)
        idx = _unlabel(idx, remove_idx)

    if add_idx is not None:
        data = _add_label(data, add_idx)
        labels = _add_label(labels, add_idx)
        idx = _add_label(idx, add_idx)

    return data, labels, idx, remove_idx, add_idx
