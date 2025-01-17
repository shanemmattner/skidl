"""KiCad schematic file reader module.

This module provides functionality to parse and read KiCad schematic (.kicad_sch) files.
It extracts information about components, nets, and other schematic elements.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import re

@dataclass
class Pin:
    """Represents a pin in a KiCad schematic symbol."""
    number: str
    name: str
    type: str  # e.g., 'power_in', 'bidirectional', 'passive'
    position: tuple[float, float]
    length: float
    uuid: str
    alternates: List[str] = None

@dataclass
class Property:
    """Represents a property of a KiCad schematic symbol."""
    name: str
    value: str
    position: tuple[float, float]
    effects: Dict
    hide: bool = False

@dataclass
class Symbol:
    """Represents a symbol in a KiCad schematic."""
    lib_id: str
    at: tuple[float, float, float]  # x, y, rotation
    unit: int
    in_bom: bool
    on_board: bool
    uuid: str
    properties: List[Property]
    pins: List[Pin]

class KicadSchematicReader:
    """Parser for KiCad schematic files."""
    
    def __init__(self, filepath: str):
        """Initialize the KiCad schematic reader.
        
        Args:
            filepath: Path to the .kicad_sch file
        """
        self.filepath = filepath
        self.version = None
        self.generator = None
        self.uuid = None
        self.paper_size = None
        self.lib_symbols = {}
        self.symbols = []
        
    def parse(self) -> bool:
        """Parse the KiCad schematic file.
        
        Returns:
            bool: True if parsing was successful, False otherwise
        """
        try:
            with open(self.filepath, 'r') as f:
                content = f.read()
                
            # Extract basic schematic info
            self.version = self._extract_version(content)
            self.generator = self._extract_generator(content)
            self.uuid = self._extract_uuid(content)
            self.paper_size = self._extract_paper_size(content)
            
            # Parse library symbols
            self._parse_lib_symbols(content)
            
            # Parse placed symbols
            self._parse_symbols(content)
            
            return True
            
        except Exception as e:
            print(f"Error parsing schematic file: {e}")
            return False
    
    def _extract_version(self, content: str) -> str:
        """Extract schematic version."""
        match = re.search(r'\(version\s+"?([^"\s]+)"?\)', content)
        return match.group(1) if match else None
    
    def _extract_generator(self, content: str) -> str:
        """Extract generator information."""
        match = re.search(r'\(generator\s+"([^"]+)"\)', content)
        return match.group(1) if match else None
    
    def _extract_uuid(self, content: str) -> str:
        """Extract schematic UUID."""
        match = re.search(r'\(uuid\s+"([^"]+)"\)', content)
        return match.group(1) if match else None
    
    def _extract_paper_size(self, content: str) -> str:
        """Extract paper size."""
        match = re.search(r'\(paper\s+"([^"]+)"\)', content)
        return match.group(1) if match else None
    
    def _parse_lib_symbols(self, content: str) -> None:
        """Parse library symbols section."""
        # Find lib_symbols section
        lib_symbols_match = re.search(r'\(lib_symbols(.*?)\)\s*\(symbol', content, re.DOTALL)
        if not lib_symbols_match:
            return
        
        lib_symbols_content = lib_symbols_match.group(1)
        
        # Extract individual symbols
        symbol_matches = re.finditer(r'\(symbol\s+"([^"]+)"(.*?)\)\s*\)', lib_symbols_content, re.DOTALL)
        
        for match in symbol_matches:
            symbol_name = match.group(1)
            symbol_content = match.group(2)
            
            # Parse symbol properties
            properties = self._parse_properties(symbol_content)
            
            # Parse pins
            pins = self._parse_pins(symbol_content)
            
            self.lib_symbols[symbol_name] = {
                'properties': properties,
                'pins': pins
            }
    
    def _parse_symbols(self, content: str) -> None:
        """Parse placed symbols in the schematic."""
        # Find symbol instances
        symbol_matches = re.finditer(r'\(symbol\s*\(lib_id\s+"([^"]+)"\)(.*?)\)\s*\)', content, re.DOTALL)
        
        for match in symbol_matches:
            lib_id = match.group(1)
            symbol_content = match.group(2)
            
            # Extract position and rotation
            pos_match = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\)', symbol_content)
            position = (
                float(pos_match.group(1)),
                float(pos_match.group(2)),
                float(pos_match.group(3))
            ) if pos_match else (0, 0, 0)
            
            # Extract unit number
            unit_match = re.search(r'\(unit\s+(\d+)\)', symbol_content)
            unit = int(unit_match.group(1)) if unit_match else 1
            
            # Extract UUID
            uuid_match = re.search(r'\(uuid\s+"([^"]+)"\)', symbol_content)
            uuid = uuid_match.group(1) if uuid_match else None
            
            # Extract properties
            properties = self._parse_properties(symbol_content)
            
            symbol = Symbol(
                lib_id=lib_id,
                at=position,
                unit=unit,
                in_bom=True,  # Default values, could be parsed from content
                on_board=True,
                uuid=uuid,
                properties=properties,
                pins=[]  # Pins come from lib_symbols
            )
            
            self.symbols.append(symbol)
    
    def _parse_properties(self, content: str) -> List[Property]:
        """Parse properties from symbol content."""
        properties = []
        prop_matches = re.finditer(r'\(property\s+"([^"]+)"\s+"([^"]+)"(.*?)\)', content, re.DOTALL)
        
        for match in prop_matches:
            name = match.group(1)
            value = match.group(2)
            prop_content = match.group(3)
            
            # Extract position
            pos_match = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\)', prop_content)
            position = (
                float(pos_match.group(1)),
                float(pos_match.group(2)),
                float(pos_match.group(3))
            ) if pos_match else (0, 0, 0)
            
            # Extract effects
            effects = {}
            effects_match = re.search(r'\(effects(.*?)\)', prop_content, re.DOTALL)
            if effects_match:
                effects_content = effects_match.group(1)
                # Parse font size
                font_match = re.search(r'\(size\s+([\d.-]+)\s+([\d.-]+)\)', effects_content)
                if font_match:
                    effects['font_size'] = (float(font_match.group(1)), float(font_match.group(2)))
                
                # Check if hidden
                hide = 'hide' in effects_content
                
                properties.append(Property(
                    name=name,
                    value=value,
                    position=position,
                    effects=effects,
                    hide=hide
                ))
        
        return properties
    
    def _parse_pins(self, content: str) -> List[Pin]:
        """Parse pins from symbol content."""
        pins = []
        pin_matches = re.finditer(r'\(pin\s+([^\s]+)\s+[^\n]+(.*?)\)\s*\)', content, re.DOTALL)
        
        for match in pin_matches:
            pin_type = match.group(1)
            pin_content = match.group(2)
            
            # Extract pin number
            num_match = re.search(r'\(number\s+"([^"]+)"', pin_content)
            number = num_match.group(1) if num_match else ""
            
            # Extract pin name
            name_match = re.search(r'\(name\s+"([^"]+)"', pin_content)
            name = name_match.group(1) if name_match else ""
            
            # Extract position and length
            pos_match = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\)', pin_content)
            position = (
                float(pos_match.group(1)),
                float(pos_match.group(2)),
                float(pos_match.group(3))
            ) if pos_match else (0, 0, 0)
            
            length_match = re.search(r'\(length\s+([\d.-]+)\)', pin_content)
            length = float(length_match.group(1)) if length_match else 0
            
            # Extract UUID
            uuid_match = re.search(r'\(uuid\s+"([^"]+)"\)', pin_content)
            uuid = uuid_match.group(1) if uuid_match else None
            
            # Extract alternate functions
            alternates = []
            alt_matches = re.finditer(r'\(alternate\s+"([^"]+)"\s+([^\s]+)', pin_content)
            for alt_match in alt_matches:
                alternates.append(f"{alt_match.group(1)} ({alt_match.group(2)})")
            
            pins.append(Pin(
                number=number,
                name=name,
                type=pin_type,
                position=position,
                length=length,
                uuid=uuid,
                alternates=alternates
            ))
        
        return pins
