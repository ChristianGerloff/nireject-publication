"""
Tests of detection module.
"""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: See repository LICENSE file

from pathlib import Path

import pytest
import numpy as np

from detection.detection import data_loader
from detection.detection import subsampling


@pytest.fixture
def features():
    """Fixture to return a list of feature names."""
    return ['mean_wave1', 'mean_wave2']


@pytest.fixture
def inputdata(features):
    """Fixture to load input data using the given features."""
    filename = Path(__file__).resolve().parent / 'data' / 'feature.parquet'
    return data_loader(filename, features)


def test_dataloader(inputdata):
    """Tests the data loading and processing steps."""
    assert not inputdata.isnull().values.any()

    # Ensure a single signal ID per augmentation
    if 'augmentation' in inputdata.columns:
        unique_signal_idx = [
            len(i) for i in
            inputdata.groupby('augmentation')['signal_id'].unique()]
        all_signal_idx = (
            inputdata.groupby('augmentation')['signal_id'].count())
        assert all(unique_signal_idx == all_signal_idx.values)


@pytest.mark.parametrize('test_size, mode, seed',
                         [(0.6, 0, 42),
                          (1.0, 1, 22),
                          (0.6, 1, 22),
                          (0.6, 2, 20211001)])
def test_subsampling(inputdata, features,
                     test_size, mode, seed):
    """Tests the data consistency of the subsampling procedure."""
    (train, test,
     labels_train, labels_test,
     idx_train, idx_test, *_) = subsampling(
        inputdata, features, test_size=test_size,
        seed=seed, mode=mode)

    # Ensure equal size
    assert len(train) == len(labels_train) == len(idx_train)
    assert len(test) == len(labels_test) == len(idx_test)

    # Test split size
    if mode == 0 or test_size >= 1.0:
        assert len(train) == len(test)
    else:
        print(len(test)/len(train))
        assert (
            pytest.approx(len(test)/(len(train)+len(test)), 0.1) ==
            test_size
            )
        # Ensure disjoint sets
        assert not any(idx_train.isin(idx_test))


@pytest.mark.parametrize('test_size, mode, augmentation, seed',
                         [(0.6, 0, ['AAFT'], 42),
                          (1.0, 1, ['AAFT'], 22),
                          (0.6, 1, ['None'], 22),
                          (0.6, 1, ['AAFT'], 42),
                          (0.6, 2, ['None'], 20211001)])
def test_augmentation_subsampling(inputdata, features,
                                  test_size, mode,
                                  augmentation, seed):
    """Tests data consistency of augmented data in subsampling."""
    sampling = subsampling(
        inputdata, features, test_size=test_size,
        mode=mode, augmentation=augmentation, seed=seed
        )

    (train, test,
     _, _,
     idx_train, idx_test,
     aug_train, aug_test,
     _, _,
     idx_aug_train, idx_aug_test) = sampling

    # Ensure equal size
    assert len(train) == len(aug_train)
    assert len(test) == len(aug_test)

    # Ensure that each signal_id is in both sets
    full_train = inputdata.iloc[idx_train]['signal_id']
    full_aug_train = inputdata.iloc[idx_aug_train]['signal_id']
    full_test = inputdata.iloc[idx_test]['signal_id']
    full_aug_test = inputdata.iloc[idx_aug_test]['signal_id']

    joint_train = np.concatenate((
        np.setdiff1d(full_train.unique(),
                     full_aug_train.unique()),
        np.setdiff1d(full_aug_train.unique(),
                     full_train.unique())))

    joint_test = np.concatenate((
        np.setdiff1d(full_test.unique(),
                     full_aug_test.unique()),
        np.setdiff1d(full_aug_test.unique(),
                     full_test.unique())))

    disjoint = np.concatenate((
        np.setdiff1d(full_test.unique(),
                     full_aug_train.unique()),
        np.setdiff1d(full_aug_train.unique(),
                     full_test.unique())))

    assert joint_train.size == 0
    assert joint_test.size == 0

    if mode == 0 or test_size >= 1.0:
        # Both sets should be joined
        assert disjoint.size == 0
    else:
        # Both sets should be fully disjoint
        assert disjoint.size == full_test.size + full_aug_train.size