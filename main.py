"""
Multistage pipeline.
"""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: see repository LICENSE file


import os
import logging
import argparse
import mlflow

from pathlib import Path
from mlflow.utils import mlflow_tags
from mlflow.entities import RunStatus
from mlflow.utils.logging_utils import eprint
from mlflow.tracking.fluent import _get_experiment_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _already_ran(entry_point_name: str,
                 parameters: dict,
                 git_commit: str,
                 user_name: str = None,
                 experiment_id: str = None) -> str:
    """Detect if a run with the given entrypoint name,
       parameters, experiment id from a specific user already ran.

    Args:
        entry_point_name (str): Name of pipeline stage.
        parameters (dict): Parameters of pipeline stage.
        git_commit (str): Id of corresponding git commit.
        user_name (str, optional): Filter history by this name.
            Defaults to None.
        experiment_id (str, optional): Id of relevant experiment.
            Defaults to None.

    Returns:
        str: id of identical historical run.
    """
    experiment_id = (experiment_id if experiment_id is not None
                     else _get_experiment_id())
    client = mlflow.tracking.MlflowClient()

    all_run_infos = reversed(client.list_run_infos(experiment_id))
    for run_info in all_run_infos:
        full_run = client.get_run(run_info.run_id)
        tags = full_run.data.tags
        hist_entry_point = tags.get(
            mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT, None)
        if hist_entry_point != entry_point_name:
            continue
        match_failed = False
        for param_key, param_value in parameters.items():
            run_value = full_run.data.params.get(param_key)
            if run_value != param_value:
                match_failed = True
                break
        if match_failed:
            continue
        if run_info.to_proto().status != RunStatus.FINISHED:
            eprint(f'Run matched, but is not FINISHED, so skipping'
                   f'run_id={run_info.run_id}, status= {run_info.status}')
            continue
        hist_user_name = tags.get(mlflow_tags.MLFLOW_USER, None)
        if (user_name is not None and hist_user_name != user_name):
            eprint(f'Run matched, but user does not match'
                   f'found={hist_user_name}, '
                   f'current user={user_name}')
            continue
        previous_version = tags.get(mlflow_tags.MLFLOW_GIT_COMMIT, None)
        if git_commit != previous_version:
            eprint(f'Run matched, but has a different source version, '
                   f'so skipping found={previous_version}, '
                   f'expected={git_commit}')
            continue
        return client.get_run(run_info.run_id)
    eprint("No matching run has been found.")
    return None


def _get_or_run(entrypoint: str,
                parameters: dict,
                git_commit: str,
                user_name: str = None,
                use_cache: bool = True,
                env_manager: str = 'local'):
    """Provides information about current run of pipeline stage.

    Args:
        entrypoint (str): Name of pipeline stage.
        parameters (dict): Parameters of pipeline entry point.
        git_commit (str): Corresponding git commit.
        user_name (str, optional): User name. Defaults to None.
        use_cache (bool, optional): Check history to avoid duplicate runs.
            Defaults to True.
        env_manager (str, optional): Environment manager. Defaults to 'local'.

    Returns:
        mlflow.entities.Run: Information about current run.
    """
    if user_name is not None:
        existing_run = _already_ran(entrypoint,
                                    parameters,
                                    git_commit,
                                    user_name)
    else:
        existing_run = _already_ran(entrypoint, parameters, git_commit)
    if use_cache and existing_run:
        print(f'Found existing run for entrypoint={entrypoint} '
              f'and parameters={parameters}')
        return existing_run
    print(f'Launching new run for entrypoint={entrypoint} '
          f'and parameters={parameters}')
    submitted_run = mlflow.run(
        uri=".",
        entry_point=entrypoint,
        env_manager=env_manager,
        parameters=parameters,
    )

    return mlflow.tracking.MlflowClient().get_run(submitted_run.run_id)


def workflow(etl_config: str = 'TRINH',
             detection_config: str = 'Q1',
             config_file: str = 'config.yaml'):
    """Main workflow of pipeline.

    Args:
        etl_config (str, optional): Name of ETL configuration. Defaults to 'TRINH'.
        detection_config (str, optional): Name of detection configuration.
        config_file (str, optional): Path to configuration file.
    """

    user_name = os.getenv('MLFLOW_TRACKING_USERNAME')
    with mlflow.start_run() as parent_run:
        mlflow.set_tag('mlflow.user', user_name)
        git_commit = parent_run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)

        config_file = Path.cwd() / 'config' / config_file

        # get or run etl stage
        etl_run = _get_or_run(
            'etl',
            {
                'config_name': etl_config,
                'config_file': config_file
            },
            git_commit,
            user_name
        )
        etl_artifact_uri = etl_run.info.artifact_uri

        # get or run detection stage
        _get_or_run(
            'detection',
            {
                'config_name': detection_config,
                'config_file': config_file,
                'artifact_path': etl_artifact_uri
            },
            git_commit,
            user_name
        )


if __name__ == "__main__":
    """Start workflow."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--etl_config', type=str, default='TRINH')
    parser.add_argument('--detection_config', type=str, default='Q1')
    parser.add_argument('--config_file', type=str, default='config.yaml')
    args = parser.parse_args()

    if os.getenv('MLFLOW_TRACKING_URI', None):
        logger.info('MLFLOW_TRACKING_URI not set')
    workflow(args.etl_config, args.detection_config, args.config_file)
