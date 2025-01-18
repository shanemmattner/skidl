"""Default configuration for circuit generation."""

from typing import Dict, List
from dataclasses import dataclass

DEFAULT_CONFIG = {
    'power_nets': ['GND', '+5V', '+3V3'],
    'default_values': {
        'C': {
            'value': '10uF'
        },
        'R': {
            'value': '1K'
        }
    }
}
