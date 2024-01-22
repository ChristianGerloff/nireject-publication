"""ETL."""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: see repository LICENSE file


import logging
import argparse
import mlflow
import numpy as np
import pandas as pd

from pathlib import Path
from dataclasses import asdict
from typing import List
from joblib import dump

from config import ETLProfile, DataLoaderProfile
from config import SamplingProfile, AnnotationProfile
from config import load_profile
from detection import data_loader, subsampling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _annotate_samples(data: pd.DataFrame,
                      samples: pd.DataFrame,
                      seed: int,
                      annotation_names: list):
    """Annotate samples.

    Args:
        data (pd.DataFrame): data to annotate.
        samples (pd.DataFrame): samples to annotate.
        seed (int): seed used for sampling.
        profile (dataclass): profile specifying annotation.

    Returns:
        annotated samples.
    """

    idx_train = samples[4]
    idx_test = samples[5]
    idx_aug_train = samples[10]
    idx_aug_test = samples[11]

    train = data.loc[idx_train, annotation_names]
    test = data.loc[idx_test, annotation_names]
    aug_train = (
        data.loc[idx_aug_train, annotation_names]
        if idx_aug_train is not None else None
    )
    aug_test = (
        data.loc[idx_aug_test, annotation_names]
        if idx_aug_test is not None else None
    )

    # sanity check does augmentation correcpond to annotation if not None
    if (aug_train is not None and
       aug_train.shape[0] == train.shape[0]):
        if not np.array_equal(aug_train, train):
            logger.warning('Augmented training data does not match training data')

    return seed, (train, test, aug_train, aug_test)


def _ingest(profile: DataLoaderProfile) -> pd.DataFrame:
    """Ingest data.

    Args:
        profile (DataLoaderProfile): profile specifying dataloader.

    Returns:
        pd.DataFrame: ingested data.
    """

    # read files
    try:
        params = asdict(profile)
        mlflow.log_params(params)
        data = data_loader(**params)
    except Exception as e:
        logger.error(f'Unable to read artifacts: {e}')
        data = None
    return data


def _sampling(data: pd.DataFrame,
              profile: SamplingProfile) -> pd.DataFrame:
    """Sample data.

    Args:
        data (pd.DataFrame): data to sampling base.
        profile (SamplingProfile): profile spefcifing sampling.

    Returns:
        pd.DataFrame: sampled data.
    """

    # create seeds
    try:
        repeats = profile.repeats
        seeds = profile.seeds

        params = asdict(profile)
        mlflow.log_params(params)

        params.pop('seeds')
        params.pop('repeats')

        if (params['mode'] != 0 and
           len(seeds) < repeats):
            r_state = np.random.RandomState(seeds[0])
            seeds = r_state.randint(1, 10e8, size=repeats)
            mlflow.log_param('sampled_seeds', seeds)

    except Exception as e:
        logger.error(f'Unable to set seeds: {e}')
        return None

    # sample data
    try:
        if (params.get('augmentation') is None or
           len(params.get('augmentation')) == 0):
            data = data[data.augmentation == 'None']

        sampled_data = [(s, subsampling(data, **params, seed=s)) for s in seeds]
    except Exception as e:
        logger.error(f'Unable to sample data: {e}')
        return None

    return sampled_data


def _annotate(data: pd.DataFrame,
              datasets: list,
              profile: AnnotationProfile) -> pd.DataFrame:
    """Annotate data.

    Args:
        data (pd.DataFrame): data to annotate.
        datasets (list): list of datasets to annotate.
        profile (AnnotationProfile): profile specifing annotation.

    Returns:
        pd.DataFrame: annotated data.
    """

    params = asdict(profile)
    mlflow.log_params(params)

    if len(profile.annotations) == 0:
        logger.info('No annotations provided')
        return None
    try:
        annotations = [_annotate_samples(data, d, s, profile.annotations) for s, d in datasets]

    except Exception as e:
        logger.error(f'Unable to annotate data: {e}')
        return None
    return annotations


def etl(etl_profile: ETLProfile,
        dataload_profile: DataLoaderProfile,
        sampling_profile: SamplingProfile,
        annotation_profile: AnnotationProfile) -> List[pd.DataFrame]:
    """Extract, Transform, Load.

    Args:
        config_name (str): name of config file.
        etl_profile (ETLProfile): ETL profile.
        dataload_profile (DataLoaderProfile): profile to load data.
        sampling_profile (SamplingProfile): profile to sample data.
        annotation_profile (AnnotationProfile): profile to annotate data.
    """

    with mlflow.start_run() as active_run:

        # set tags
        mlflow.set_tags(etl_profile.tags)

        output_path = Path(etl_profile.output_path) / active_run.info.run_id
        output_path.mkdir(parents=True, exist_ok=True)
        mlflow.log_param('output_path', str(output_path))

        # ingest data
        data = _ingest(dataload_profile)
        dump(data, output_path / 'data.joblib', compress=3)

        # store pandas idx per probe if more than one unique probe
        if len(data.probe.unique()) > 1:
            probes_idx_data = data.groupby('probe').apply(lambda x: x.index)
            dump(probes_idx_data, output_path / 'probes_idx_data.joblib', compress=3)

        # sample data
        sampled_data = _sampling(data, sampling_profile)
        dump(sampled_data, output_path / 'sampled_data.joblib', compress=3)

        # annotate data
        annotated_data = _annotate(data, sampled_data, annotation_profile)
        if annotated_data is not None:
            dump(annotated_data, output_path / 'annotated_data.joblib', compress=3)

        mlflow.log_artifacts(output_path)
        logger.info(f'ETL finished - run_id: {active_run.info.run_id} \n'
                    f'data exported to {output_path}')


if __name__ == "__main__":
    """Start ETL."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_name', type=str, default='SHIFTSuni_24_AAFT_100')
    parser.add_argument('--config_file', type=str, default='/nireject/config/config.yaml')
    args = parser.parse_args()
    #mlflow.set_experiment("first-test")

    # load profiles from config file
    try:
        (etl_profile,
         dataloader_profile,
         sampling_profile,
         annotation_profile) = tuple(
            map(
                lambda profile: load_profile(
                    profile,
                    args.config_name,
                    args.config_file
                ),
                [
                    ETLProfile(),
                    DataLoaderProfile(),
                    SamplingProfile(),
                    AnnotationProfile()
                ]
            )
        )
    except Exception as e:
        logger.error(f'ETL: load profiles failed {e}')

    # run ETL
    etl(etl_profile,
        dataloader_profile,
        sampling_profile,
        annotation_profile)
