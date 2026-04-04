"""
MIDI Captain MAX - Utility Modules

Shared utilities for firmware development.

This package contains pure utility functions with no hardware dependencies,
making them safe to import from any module without creating circular imports.

Import Hierarchy:
    utils ← core ← handlers ← main

Author: Max Cascone
Date: 2026-04-04
"""

from .timing import (
    measure_time,
    PerformanceMonitor,
    AverageTimer,
    format_duration
)

__all__ = [
    'measure_time',
    'PerformanceMonitor',
    'AverageTimer',
    'format_duration',
]
