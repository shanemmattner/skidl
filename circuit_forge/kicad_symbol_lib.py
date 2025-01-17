# kicad_symbol_lib.py
"""
kicad_symbol_lib.py - KiCad Symbol Library Parser and Manager

This module provides functionality for parsing and extracting information from KiCad
symbol libraries (.kicad_sym files). It handles the S-Expression format used by KiCad
and provides structured access to symbol information including pins, properties, and
footprints.
"""

import os
from typing import Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass
from enum import Enum


class PinElectricalType(str, Enum):
    """Pin electrical types as defined in KiCad documentation"""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRISTATE = "tri_state"
    PASSIVE = "passive"
    FREE = "free"
    UNSPECIFIED = "unspecified"
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    OPEN_COLLECTOR = "open_collector"
    OPEN_EMITTER = "open_emitter"
    NO_CONNECT = "no_connect"


class PinGraphicalStyle(str, Enum):
    """Pin graphical styles as defined in KiCad documentation"""
    LINE = "line"
    INVERTED = "inverted"
    CLOCK = "clock"
    INVERTED_CLOCK = "inverted_clock"
    INPUT_LOW = "input_low"
    CLOCK_LOW = "clock_low"
    OUTPUT_LOW = "output_low"
    EDGE_CLOCK_HIGH = "edge_clock_high"
    NON_LOGIC = "non_logic"


class PinInfo(TypedDict):
    """Pin information dictionary"""
    type: str
    graphic_style: str
    name: Optional[str]
    number: Optional[str]


class SymbolProperties(TypedDict):
    """
    Symbol properties as per KiCad documentation
    """
    Reference: Optional[str]
    Value: Optional[str]
    Footprint: Optional[str]
    Description: Optional[str]
    Keywords: Optional[str]
    Datasheet: Optional[str]


class SymbolInfo(TypedDict):
    """
    Complete symbol information structure
    """
    name: str
    properties: SymbolProperties
    pins: List[PinInfo]
    extends: Optional[str]
    footprint: Optional[str]
    in_bom: bool
    on_board: bool


@dataclass
class LibraryPath:
    """
    Represents a KiCad library search path with priority
    """
    path: str
    priority: int = 0


class KicadSymbolLib:
    """
    Class for parsing and extracting information from KiCad symbol libraries
    Following KiCad S-Expression format specification
    """

    def __init__(self, lib_paths: Optional[List[Union[str, LibraryPath]]] = None):
        """
        Initialize KicadSymbolLib with library paths
        """
        self.lib_paths: List[LibraryPath] = []

        # Default KiCad library path based on operating system
        if os.name == 'posix':
            # Unix/Linux/MacOS default path
            default_path = "/usr/share/kicad/library"
            # Check for MacOS default path
            if os.path.exists("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"):
                default_path = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
        elif os.name == 'nt':
            # Windows default path
            default_path = r"C:\Program Files\KiCad\share\kicad\library"
        else:
            default_path = "./"

        if lib_paths is None:
            self.lib_paths.append(LibraryPath(default_path, 0))
        else:
            for path in lib_paths:
                if isinstance(path, str):
                    self.lib_paths.append(LibraryPath(path, 0))
                else:
                    self.lib_paths.append(path)

        # Sort paths by priority (highest first)
        self.lib_paths.sort(key=lambda x: x.priority, reverse=True)

    def find_library_file(self, library_name: str) -> Optional[str]:
        """
        Find the KiCad symbol library file in the configured paths
        """
        # List of possible file extensions in order of preference
        extensions = ['.kicad_sym', '.lib']

        for lib_path in self.lib_paths:
            for ext in extensions:
                # Try exact name match first
                file_path = os.path.join(lib_path.path, f"{library_name}{ext}")
                if os.path.isfile(file_path):
                    return file_path

                # Try case-insensitive match
                try:
                    for filename in os.listdir(lib_path.path):
                        if filename.lower() == f"{library_name.lower()}{ext}":
                            return os.path.join(lib_path.path, filename)
                except OSError:
                    # Handle case where directory doesn't exist or isn't readable
                    continue

                # Try matching library name as part of filename
                try:
                    for filename in os.listdir(lib_path.path):
                        if (filename.lower().startswith(library_name.lower()) and
                            filename.endswith(ext)):
                            return os.path.join(lib_path.path, filename)
                except OSError:
                    continue

        return None

    def _extract_footprint(self, symbol_data: list) -> Optional[str]:
        """
        Extract default footprint from symbol data
        """
        # First check explicit footprint property
        footprint = self._find_property_value(symbol_data, 'Footprint')
        if footprint:
            return footprint.strip('"')

        # Check for footprint in properties section
        for item in symbol_data:
            if isinstance(item, list) and len(item) > 2:
                if item[0] == 'footprint':
                    return item[1].strip('"')
        return None

    def get_symbol_info(self, component_path: str) -> Optional[SymbolInfo]:
        """
        Get information about a KiCad symbol including footprint
        """
        library_name, component_name = self._parse_component_path(component_path)
        library_path = self.find_library_file(library_name)

        if not library_path:
            raise FileNotFoundError(
                f"Library '{library_name}' not found in configured paths: "
                f"{[p.path for p in self.lib_paths]}"
            )

        symbol_info = self._parse_kicad_symbol(library_path, component_name)

        # Add footprint information if available
        if symbol_info:
            footprint = self._extract_footprint(symbol_info)
            if footprint:
                symbol_info['footprint'] = footprint

        return symbol_info

    @staticmethod
    def _parse_component_path(component_path: str) -> tuple[str, str]:
        """
        Parse a KiCad component path in the format "Library:Component"
        """
        try:
            library_name, component_name = component_path.split(':')
            return library_name, component_name
        except ValueError:
            raise ValueError(
                "Component path must be in format 'Library:Component' (e.g., 'Device:R_Small')"
            )

    @staticmethod
    def _parse_parens(s: str) -> list:
        """
        Parse parenthesized s-expressions into nested lists
        """
        result = []
        current = result
        stack = []

        i = 0
        token = ''
        in_string = False
        while i < len(s):
            char = s[i]

            if char == '(' and not in_string:
                if token:
                    current.append(token)
                    token = ''
                stack.append(current)
                new_list = []
                current.append(new_list)
                current = new_list
            elif char == ')' and not in_string:
                if token:
                    current.append(token)
                    token = ''
                if stack:
                    current = stack.pop()
            elif char.isspace() and not in_string:
                if token:
                    current.append(token)
                    token = ''
            elif char == '"':
                token += char
                if not in_string:
                    in_string = True
                else:
                    in_string = False
            else:
                token += char

            i += 1

        if token:
            current.append(token)

        return result

    @staticmethod
    def _find_property_value(symbol_data: list, property_name: str) -> Optional[str]:
        """
        Extract value of a specific property from symbol data
        """
        for item in symbol_data:
            if isinstance(item, list) and len(item) > 2:
                if item[0] == 'property' and item[1].strip('"') == property_name:
                    return item[2]
        return None

    @staticmethod
    def _find_extends_value(symbol_data: list) -> Optional[str]:
        """
        Find the extended symbol name if it exists
        """
        for item in symbol_data:
            if isinstance(item, list) and item and item[0] == 'extends':
                return item[1].strip('"')
        return None

    @staticmethod
    def _find_extended_symbol(parsed_data: list, symbol_name: str) -> Optional[list]:
        """
        Find the extended symbol definition in the parsed data
        """
        if parsed_data and parsed_data[0] and parsed_data[0][0] == 'kicad_symbol_lib':
            for section in parsed_data[0][1:]:
                if isinstance(section, list) and section and section[0] == 'symbol':
                    name = section[1]
                    if isinstance(name, str) and name.strip('"') == symbol_name:
                        return section
        return None

    def _extract_pins(self, symbol_data: list) -> List[PinInfo]:
        """
        Extract pin information from symbol data
        """
        pins = []
        for item in symbol_data:
            if isinstance(item, list):
                if item and item[0] == 'pin':
                    try:
                        # Extract electrical type and graphic style
                        pin_info: PinInfo = {
                            'type': item[1],  # Electrical type
                            'graphic_style': item[2],  # Visual style
                            'name': None,
                            'number': None
                        }

                        # Parse pin details
                        for attr in item[3:]:
                            if isinstance(attr, list):
                                if attr[0] == 'name':
                                    pin_info['name'] = attr[1]
                                elif attr[0] == 'number':
                                    pin_info['number'] = attr[1]

                        if pin_info['number']:  # Only add if we found a pin number
                            pins.append(pin_info)
                    except Exception as e:
                        print(f"Error parsing pin: {e}")
                        continue
                else:
                    pins.extend(self._extract_pins(item))
        return pins

    def _parse_kicad_symbol(self, file_path: str, symbol_name: str) -> Optional[SymbolInfo]:
        """
        Parse KiCad symbol file and extract information for a specific symbol
        """
        with open(file_path, 'r') as f:
            content = f.read()

        # Split content into lines and join with single spaces
        content = ' '.join(line.strip() for line in content.split('\n') if line.strip())
        parsed = self._parse_parens(content)

        if parsed and parsed[0] and parsed[0][0] == 'kicad_symbol_lib':
            for section in parsed[0][1:]:
                if isinstance(section, list) and section and section[0] == 'symbol':
                    name = section[1]
                    if isinstance(name, str) and name.strip('"') == symbol_name:
                        # Found the symbol we're looking for
                        extends_name = self._find_extends_value(section)

                        # Initialize symbol info with proper typing
                        symbol_info: SymbolInfo = {
                            'name': symbol_name,
                            'properties': {
                                'Reference': self._find_property_value(section, 'Reference'),
                                'Value': self._find_property_value(section, 'Value'),
                                'Footprint': self._find_property_value(section, 'Footprint'),
                                'Description': self._find_property_value(section, 'Description'),
                                'Keywords': self._find_property_value(section, 'Keywords'),
                                'Datasheet': self._find_property_value(section, 'Datasheet'),
                            },
                            'pins': self._extract_pins(section),
                            'extends': None,
                            'in_bom': True,  # Default values per KiCad docs
                            'on_board': True
                        }

                        # Handle extends relationship
                        if extends_name:
                            extended_symbol = self._find_extended_symbol(parsed, extends_name)
                            if extended_symbol:
                                symbol_info['extends'] = extends_name
                                # Inherit pins from parent if child has none
                                if not symbol_info['pins']:
                                    symbol_info['pins'] = self._extract_pins(extended_symbol)

                        return symbol_info

        return None

