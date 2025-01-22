"""
SKiDL Generator package for converting KiCad hierarchy text files to SKiDL Python code.
"""

from .component_parser.component_parser import (
    parse_component_name,
    parse_component_properties,
    Component,
    ParseResult,
    ParseError
)

__all__ = [
    'parse_component_name',
    'parse_component_properties',
    'Component',
    'ParseResult',
    'ParseError'
]
