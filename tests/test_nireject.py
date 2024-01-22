"""
Tests of nireject class.
"""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: see repository LICENSE file


from pathlib import Path

import re
import pytest
import numpy as np
import math

from detection.detection import data_loader
from detection.nireject import Nireject

TASK_ERROR_MSG = ' is not a supported task.'
PREDICT_TASK_ERROR_MSG = ('The function=predict is not supported '
                          'for the current task=')
PREDICT_PROBA_TASK_ERROR_MSG = ('The function=predict_proba is not supported '
                                'for the current task=')


@pytest.fixture
def features():
    """Fixture to return a list of features."""
    return ['diff_cov',
            'hr_freq_od_wave1',
            'hr_power_od_wave1',
            'flatline',
            'sci']


@pytest.fixture
def tail_priors():
    """Fixture to return an array of tail priors."""
    return np.array([1, 0, -1, 99, -1])


@pytest.fixture
def converted_tail_priors():
    """Fixture to return an array of converted tail priors."""
    return np.array([1, 0, -1, 1, -1])


@pytest.fixture
def auto_tail_priors():
    """Fixture to return an array of auto-generated tail priors."""
    return np.zeros(5)


@pytest.fixture
def fail_tail_priors():
    """Fixture to return an array of failing tail priors."""
    return np.array([1, 0, -1, 99, -1, 0])


@pytest.fixture
def inputdata(features):
    """Fixture to load input data using the given features."""
    filename = Path(__file__).resolve().parent / 'data' / 'feature.parquet'
    return data_loader(filename, features)


@pytest.mark.parametrize(
    'task',
    [pytest.param('unsupervised', marks=pytest.mark.xfail),
     pytest.param('semi-supervised', marks=pytest.mark.xfail),
     pytest.param('supervised', marks=pytest.mark.xfail),
     'RL',
     'test']
    )
def test_task_validation(task):
    """Smoke test of task input validation."""
    with pytest.raises(ValueError, match=f"'{task}'"+TASK_ERROR_MSG):
        Nireject(task=task)


@pytest.mark.parametrize(
    'task, seed',
    [('unsupervised', 21),
     ('supervised', 55)]
    )
def test_repr(task, seed):
    """Test the string representation of the Nireject class."""
    retval = repr(Nireject(task=task, seed=seed))
    assert f"Nireject({{'seed': {seed}, 'task': '{task}'}}" in retval


def test_unsupervised(inputdata, features):
    """Test unsupervised learning in Nireject."""
    train = inputdata.loc[inputdata.augmentation == 'None', features]
    augmented_data = inputdata.loc[inputdata.augmentation == 'AAFT', features]
    n = train.shape[0] - math.ceil(train.shape[0] / 8.) * 2

    detector_1 = Nireject(task='unsupervised', seed=20211001)
    yhat_1 = detector_1.fit_predict(train,
                                    augmented=augmented_data,
                                    dev=True)
    y_score_1 = detector_1.fit_predict_proba(train, dev=True)

    detector_2 = Nireject(task='unsupervised', seed=20211001)
    yhat_2 = detector_2.fit_predict(train,
                                    augmented=augmented_data,
                                    dev=True)
    y_score_2 = detector_2.fit_predict_proba(train, dev=True)

    detector_3 = Nireject(task='unsupervised', seed=20211001)
    detector_3.fit(train.loc[:n-1, :])
    y_score_3 = detector_3.decision_function(
        train.loc[n:, :], augmented=augmented_data)

    assert np.array_equal(yhat_1, yhat_2)
    assert np.array_equal(y_score_1, y_score_2)
    assert min(y_score_1) >= 0
    assert max(y_score_1) <= 1
    assert y_score_3.shape[0] == train.shape[0] - n


def test_semi_supervised(inputdata, features):
    """Test semi-supervised learning in Nireject."""
    data = inputdata[inputdata.augmentation == 'None']
    n = math.ceil(data.shape[0] / 8.) * 2
    features_train = data.loc[n:, features]
    labels_train = data.loc[n:, 'labels']
    features_test = data.loc[:n, features]

    detector_1 = Nireject(task='semi-supervised', seed=20211001)
    detector_1.fit(features_train, labels_train, dev=True)
    yhat_1

 = detector_1.predict(features_train)
    y_score_1 = detector_1.predict_proba(features_train)
    test_yhat_1 = detector_1.predict(features_test)

    detector_2 = Nireject(task='semi-supervised', seed=20211001)
    yhat_2 = detector_2.fit_predict(
        features_train, labels_train, dev=True)
    y_score_2 = detector_2.fit_predict_proba(
        features_train, labels_train, dev=True)

    # Ensure reproducibility and fit_predict behavior
    assert np.array_equal(yhat_1, yhat_2)
    assert np.array_equal(y_score_1, y_score_2)

    # Ensure the correct shape of prediction and probability
    assert yhat_1.shape == y_score_1.shape
    assert yhat_1.shape == y_score_2.shape

    # Ensure correct test size
    assert test_yhat_1.shape[0] == features_test.shape[0] 


@pytest.mark.parametrize(
    'task, tail_fixture',
    [('unsupervised', 'fail_tail_priors'),
     ('semi-supervised', 'fail_tail_priors'),
     ('supervised', 'fail_tail_priors'),
     pytest.param('semi-supervised', 'tail_priors', marks=pytest.mark.xfail)]
    )
def test_tail_priors_check(inputdata, features, task, tail_fixture, request):
    """Smoke test for tail prior check."""
    train = inputdata[inputdata.augmentation == 'None']
    features_train = train[features]
    labels_train = train['labels']

    detector = Nireject(task=task)
    tail_prior = request.getfixturevalue(tail_fixture)

    error_msg = (
        f'Shape of X({len(features)}) and '
        f'tail_priors({tail_prior.shape[0]}) does not align.'
    )

    with pytest.raises(ValueError, match=re.escape(error_msg)):
        detector.fit(features_train,
                     labels_train,
                     tail_priors=tail_prior,
                     dev=True)


@pytest.mark.parametrize(
    'task, tail_fixture',
    [('unsupervised', 'tail_priors'),
     ('semi-supervised', 'tail_priors'),
     ('supervised', 'tail_priors'),
     pytest.param('semi-supervised',
                  'auto_tail_priors',
                  marks=pytest.mark.xfail)])
def test_tail_priors(inputdata,
                     features,
                     task,
                     tail_fixture,
                     converted_tail_priors,
                     request):
    """Test whether priors are considered in Nireject."""
    train = inputdata[inputdata.augmentation == 'None']
    features_train = train[features]
    labels_train = train['labels']

    detector_1 = Nireject(task=task)
    tail_prior = request.getfixturevalue(tail_fixture)
    detector_1.fit(features_train,
                   labels_train,
                   tail_priors=tail_prior,
                   dev=True)

    detector_2 = Nireject(task=task)
    detector_2.fit(features_train,
                   labels_train,
                   dev=True)

    # Ensure that tail priors are set
    assert np.array_equal(detector_1.tail_priors,
                          converted_tail_priors)

    # Ensure that tails are considered
    assert not np.array_equal(detector_1.decision_scores_,
                              detector_2.decision_scores_)


@pytest.mark.parametrize(
    'task',
    ['unsupervised',
     pytest.param('semi-supervised', marks=pytest.mark.xfail),
     pytest.param('supervised', marks=pytest.mark.xfail)]
    )
def test_prohibit_functions(inputdata, features, task):
    """Smoke test to avoid predict function in unsupported tasks."""
    train = inputdata.loc[inputdata.augmentation == 'None', features]
    detector_1 = Nireject(task=task, seed=20211001)
    detector_1.fit(train, dev=True)

    pred_msg = f'{PREDICT_TASK_ERROR_MSG}{task}'
    with pytest.raises(ValueError, match=pred_msg):
        detector_1.predict(train)

    prob_msg = f'{PREDICT_PROBA_TASK_ERROR_MSG}{task}'
    with pytest.raises(ValueError, match=prob_msg):
        detector_1.predict_proba(train)