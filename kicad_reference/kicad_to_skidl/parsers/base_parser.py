from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import re

@dataclass
class Component:
    library: str
    symbol: str
    reference: str
    footprint: str
    value: Optional[str] = None

@dataclass
class Label:
    name: str
    x: float
    y: float

@dataclass
class Sheet:
    name: str
    file_path: str
    components: List[Component]
    labels: List[Label]

class SchematicParser(ABC):
    """Abstract base class for schematic file parsers."""
    
    @abstractmethod
    def parse_sheet(self, content: str) -> Optional[Sheet]:
        """Parse sheet content and return a Sheet object."""
        pass

    @abstractmethod
    def parse_components(self, content: str) -> List[Component]:
        """Parse and return components from content."""
        pass

    @abstractmethod
    def parse_labels(self, content: str) -> List[Label]:
        """Parse and return hierarchical labels with positions from content."""
        pass

class KiCadSchematicParser(SchematicParser):
    """KiCad specific schematic parser implementation."""

    def parse_sheet(self, content: str) -> Optional[Sheet]:
        """Parse KiCad sheet content."""
        if not content:
            return None
            
        sheet_name = self._extract_sheet_name(content)
        sheet_file = self._extract_sheet_file(content)
        
        if not sheet_name or not sheet_file:
            return None
            
        components = self.parse_components(content)
        labels = self.parse_labels(content)
        
        return Sheet(
            name=sheet_name,
            file_path=sheet_file,
            components=components,
            labels=labels
        )

    def parse_components(self, content: str) -> List[Component]:
        """Parse KiCad components."""
        components = []
        
        symbol_pattern = r'\(symbol.*?\(lib_id\s+"([^"]+)".*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Footprint"\s+"([^"]*)".*?\)'
        symbol_blocks = re.finditer(symbol_pattern, content, re.DOTALL)
        
        for match in symbol_blocks:
            lib_id = match.group(1)
            reference = match.group(2)
            footprint = match.group(3)
            
            # Skip power symbols and empty footprints
            if lib_id.startswith("power:") or not footprint:
                continue
                
            lib_parts = lib_id.split(":")
            components.append(Component(
                library=lib_parts[0],
                symbol=lib_parts[1],
                reference=reference,
                footprint=footprint
            ))
        
        return components

    def parse_labels(self, content: str) -> List[Label]:
        """Parse KiCad hierarchical labels with positions."""
        labels = []
        label_pattern = r'\(hierarchical_label\s+"([^"]+)".*?\(at\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+[^)]*\)'
        label_matches = re.finditer(label_pattern, content, re.DOTALL)
        
        for match in label_matches:
            name = match.group(1)
            x = float(match.group(2))
            y = float(match.group(3))
            labels.append(Label(name=name, x=x, y=y))
        
        return labels

    def _extract_sheet_name(self, content: str) -> Optional[str]:
        """Extract sheet name from content."""
        pattern = r'\(property\s+"Sheetname"\s+"([^"]+)"'
        match = re.search(pattern, content)
        return match.group(1) if match else None

    def _extract_sheet_file(self, content: str) -> Optional[str]:
        """Extract sheet file path from content."""
        pattern = r'\(property\s+"Sheetfile"\s+"([^"]+)"'
        match = re.search(pattern, content)
        return match.group(1) if match else None
