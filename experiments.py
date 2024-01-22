"""Run all experiments for paper."""

# Author: Christian Gerloff <christian.gerloff@rwth-aachen.de>
# License: see repository LICENSE file


import itertools
import mlflow

ETL_Q1 = ['N21_UNGROUPED_AAFT', 'R22_UNGROUPED_AAFT']

ETL_Q2 = [
    'UNCOUPLED_HRF_AAFT_100',
    'SIGNALLOSS_10_AAFT_100',
    'SIGNALLOSS_50_AAFT_100',
    'SIGNALLOSS_100_AAFT_100',
    'SHIFTSuni_12_AAFT_100',
    'SHIFTSuni_24_AAFT_100',
    'SHIFTSuni_36_AAFT_100',
    'SHIFTS_12_AAFT_100',
    'SHIFTS_24_AAFT_100',
    'SHIFTS_36_AAFT_100',
    'PEAKS_6_AAFT_100',
    'PEAKS_36_AAFT_100',
    'PEAKS_60_AAFT_100'
]


ETL_Q3 = [
    'ANNOTATION_ERROR_1',
    'ANNOTATION_ERROR_5',
    'ANNOTATION_ERROR_10',
    'ANNOTATION_ERROR_25',
    'ANNOTATION_ERROR_50',
    'ANNOTATION_ERROR_75',
    'ANNOTATION_ERROR_100',
    'LABELLED_1',
    'LABELLED_5',
    'LABELLED_10',
    'LABELLED_25',
    'LABELLED_50',
    'LABELLED_75',
    'LABELLED_100',
    'CONTAMINATION_1',
    'CONTAMINATION_2',
    'CONTAMINATION_3',
    'CONTAMINATION_4',
    'CONTAMINATION_5',
    'CONTAMINATION_7.5',
    'CONTAMINATION_10',
    'CONTAMINATION_15',
    'CONTAMINATION_20',
    'CONTAMINATION_25',
    'CONTAMINATION_30',
    'CONTAMINATION_40',
    'CONTAMINATION_50',
]

ETL_Q4 = ['HYBRID_CHANNEL_MIXED_V3_AAFT_VR', 'HYBRID_CHANNEL_MIXED_V3_AAFT_LM', 'HYBRID_CHANNEL_MIXED_V3_AAFT_MAX']

# same detectors
DETECTION_Q1 = ['Q1']
DETECTION_Q2 = ['Q1']  
DETECTION_Q3 = ['Q1']
DETECTION_Q4 = ['Q1']

# ablation study
config_file = 'config.yaml'

# Q1
for etl_config, detection_config in itertools.product(ETL_Q1, DETECTION_Q1):
    mlflow.projects.run(
        backend='local',
        uri=".",
        synchronous=True,
        entry_point='main',
        env_manager='local',
        experiment_name='Q1_final',
        parameters={
            'etl_config': etl_config,
            'detection_config': detection_config,
            'config_file': config_file
        }
    )

# Q2
for etl_config, detection_config in itertools.product(ETL_Q2, DETECTION_Q2):
    mlflow.projects.run(
        backend='local',
        uri=".",
        synchronous=True,
        entry_point='main',
        env_manager='local',
        experiment_name='Q2_final',
        parameters={
            'etl_config': etl_config,
            'detection_config': detection_config,
            'config_file': config_file
        }
    )

# Q3
for etl_config, detection_config in itertools.product(ETL_Q3, DETECTION_Q3):
    mlflow.projects.run(
        backend='local',
        uri=".",
        synchronous=True,
        entry_point='main',
        env_manager='local',
        experiment_name='Q3_final',
        parameters={
            'etl_config': etl_config,
            'detection_config': detection_config,
            'config_file': config_file
        }
    )

# Q4
for etl_config, detection_config in itertools.product(ETL_Q4, DETECTION_Q4):
    mlflow.projects.run(
        backend='local',
        uri=".",
        synchronous=True,
        entry_point='hybrid_main',
        env_manager='local',
        experiment_name='Q4_final',
        parameters={
            'etl_config': etl_config,
            'detection_config': detection_config,
            'config_file': config_file
        }
    )