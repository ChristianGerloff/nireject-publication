"""Loads configured profiles from a YAML config file."""
import yaml
import logging
from pathlib import Path
from pydantic.dataclasses import dataclass
from .basis_profiles import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _recursive_update(profile, profile_updates: dict):
    """Recursively updates the profile with the profile_updates.

    Args:
        profile (dict): The profile to be updated.
        profile_updates (dict): The updates to be applied to the profile.

    Returns:
        The updated profile.
    """

    # check if any key definitions is in schema (nested profile)
    schema = profile.__pydantic_model__.schema()

    for key, value in profile_updates.items():
        # test if profile_updates contains subclass in definitions
        if key in globals():
            # check if dataclass imported
            dataclass = globals()[key]
            instance = dataclass()
            if value is not None:
                instance = _recursive_update(instance, value)
            profile = instance  # ToDo: beautify
        elif key in schema['properties']:
            # check if items are dataclasses
            if '$ref' in schema['properties'][key].get('items', []):
                for idx, item in enumerate(value):
                    if item is None:
                        continue
                    # why?
                    if idx < len(profile.__getattribute__(key)):
                        profile.__getattribute__(key)[idx] = _recursive_update(profile.__getattribute__(key)[idx], item)
                    else:
                        instance = globals()[
                            schema['properties'][key]['items']['$ref'].split('/')[-1]
                        ]()
                        instance = _recursive_update(instance, item)  # ToDo: beautify
                        profile.__getattribute__(key).append(instance)
            else:
                profile.__dict__.update(profile_updates)
    return profile


def load_profile(profile: dataclass,
                 config_name: str,
                 config_file: str = 'config.yaml') -> dataclass:
    """Loads the configuration from a YAML config file into a dataclass profile.

    Args:
        profile (dataclass): The profile to load.
        config_name (str): The name of the configuration.
        config_file (str, optional): The name of the configuration file.
            Defaults to 'test.yaml'.

    Returns:
        dataclass: The parametrized profile.
    """

    try:
        profile_name = profile.__class__.__name__
        config_file = Path(config_file).read_text(encoding='UTF-8')
        all_configs = yaml.safe_load(config_file)

        if config_name not in all_configs:
            logger.warning(f'Unable to load config {config_name} from {config_file}.\n'
                           'Using default configuration.')
            return profile

        config = all_configs.get(config_name)
        if profile_name not in config:
            return profile

        profile_updates = config.get(profile_name)
        _recursive_update(profile, profile_updates)

    except Exception as e:
        logger.error(f'Unable to load profile {config_name}/{profile} '
                     f'from configuration file {config_file}: {e}')
    return profile
