# nireject-publication

This repository contains the codebase for the nireject publication.

## Structure

- `Dockerfile`: Container. Ensures that the project can run in a consistent environment, with all dependencies pre-installed.

- `pyproject.toml`: This file is used to manage project dependencies and settings specific to Python.

- `utils/`: This directory contains utility scripts and modules that are used across the project. These might include helper functions any other generic utilities.

- `assets/`: This folder is intended to store third party code from other libraries or projects.

- `config/`: Contains configuration environment that enable an efficient and traceable experiment configuration.
  
- `detection/`: This module includes scripts and code related to detection algorithms or processes.
  
- `features/`: Focuses on feature extraction process using Matlab.

- `simulation/`: Contains code and resources related to simulation using Matlab.