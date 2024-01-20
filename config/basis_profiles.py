"""General profiles"""
from typing import List, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class ETLProfile:
    output_path: str = '/tmp/artifact_download'
    tags: dict = Field(
        default_factory=lambda: {
            'stage': 'etl',
            'question': 'Q1',
            'dataset': 'R22',
        }
    )
@dataclass
class ETLProfileHybrid:
    output_path: str = '/tmp/artifact_download'
    ratings_filename: str = 'ratings.csv'
    tags: dict = Field(
        default_factory=lambda: {
            'stage': 'etl',
            'question': 'hybrid real',
            'dataset': 'hybrid_mixed',
        }
    )

@dataclass
class DataLoaderProfile:
    filename: str = ''
    features: List[str] = Field(
        default_factory=lambda: [
            'snr_wave1',
            'sinad_wave1',
            'spike_rate_hbo',
            'cov_wave_1',
            'diff_cov',
            'hr_freq_od_wave1',
            'hr_power_od_wave1',
            'flatline',
            'sci'
        ]
    )
    probe: Optional[str] = None
    prefix_features: Optional[str] = None


@dataclass
class SamplingProfile:
    mode: int = Field(1, ge=0, le=2)
    features: List[str] = Field(
        default_factory=lambda: [
            'snr_wave1',
            'sinad_wave1',
            'spike_rate_hbo',
            'cov_wave_1',
            'diff_cov',
            'hr_freq_od_wave1',
            'hr_power_od_wave1',
            'flatline',
            'sci'
        ]
    )
    test_size: float = Field(0.4, ge=0, le=1)
    standardize: bool = True
    seeds: List[int] = Field(default_factory=lambda: [42])
    repeats: int = Field(10, ge=1)
    augmentation: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    label_noise_ratio: float = 0.0
    gamma: float = 1.0
    c_rate: float = 0.0


@dataclass
class ProcessingHybridProfile:
    features: List[str] = Field(
        default_factory=lambda: [
            'snr_wave1',
            'sinad_wave1',
            'spike_rate_hbo',
            'cov_wave_1',
            'diff_cov',
            'hr_freq_od_wave1',
            'hr_power_od_wave1',
            'flatline',
            'sci'
        ]
    )
    standardize: bool = True
    mode: str = Field('suggestion', regex='^(suggestion|hybrid|max)$')
    augmentation: Optional[List[str]] = Field(
        default_factory=lambda: [
            'AAFT'
        ]
    )


@dataclass
class AnnotationProfile:
    annotations: List[str] = Field(default_factory=lambda: ['channel'])


@dataclass
class DetectionProfile:
    output_path: str = '/tmp/artifact_download'
    main_metrics: List[str] = Field(
        default_factory=lambda: [
            'precision',
            'recall',
            'roc_auc',
            'roc_auc_scores',
            'auc_pr',
            'precision_rank_scores'
        ]
    )
    tags: dict = Field(default_factory=lambda: {'stage': 'detection'})


@dataclass
class BaselineNamesProfile:
    detector_data: List[tuple] = Field(
        default_factory=lambda: [
            ('sci', 'sci_decision', 'sci'),
            ('ppower', 'ppower_decision', 'ppower'),
            ('snr_default', 'snr_default_decision', 'snr_default'),
            ('signal_level', 'signal_level_decision', 'signal_level'),
            ('sqs', 'sqs_decision', 'sqs'),
            ('phoebe', 'phoebe', None),
            ('cov', 'cov', None)
        ]
    )


@dataclass
class DetectorNamesProfile:
    detector_names: List[str] = Field(
        default_factory=lambda: [
            'ABOD',
            'CBLOF',
            'HBOS',
            'IForest',
            'KNN',
            'LOF',
            'MCD',
            'OCSVM',
            'PCA',
        ]
    )


@dataclass
class DetectorProfile:
    name: Optional[str] = None


@dataclass
class NirejectProfile:
    task: Optional[str] = 'unsupervised-t'
    tail_priors: List[int] = Field(
        default_factory=lambda: [
            -1,
            -1,
            1,
            0,
            0,
            0,
            -1,
            1,
            -1
        ]
    )
    opt: Optional[bool] = False
    append: Optional[bool] = False
    annotate: Optional[bool] = False
    augmented_training: Optional[bool] = False
    hbos: Optional[bool] = False
    tabpfn: Optional[bool] = False
    name: Optional[str] = None


@dataclass
class NirejectNamesProfile:
    detectors: List[NirejectProfile] = Field(
        default_factory=lambda: [
            NirejectProfile()
        ]
    )
    semi_supervised_detectors: List[NirejectProfile] = Field(
        default_factory=lambda: [
            NirejectProfile(task='supervised-i', name='semi-supervised'),
        ]
    )
