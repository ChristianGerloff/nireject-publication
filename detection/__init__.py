"""
The :mod:`detector` module to
access the detectors
"""

from .detection import data_loader, subsampling
from .detection import process_hybrid
from .detection import performance_evaluation
from .detection import nireject, nireject_sv
from .detection import xgbod_sv, feawad_sv
from .nireject import Nireject

__all__ = [
    'data_loader',
    'subsampling',
    'process_hybrid',
    'nireject',
    'nireject_sv',
    'Nireject',
    'xgbod_sv',
    'feawad_sv',
    'performance_evaluation'
]
