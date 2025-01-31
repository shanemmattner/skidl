# hierarchy_manager.py
# Add to src/skidl/tools/kicad8/sch_gen/

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path
import re
import uuid
from kiutils.schematic import Schematic
from kiutils.items.common import Position, Property
from kiutils.items.schitems import HierarchicalSheet
from .kicad_writer import SchematicSymbolInstance

@dataclass
class CircuitNode:
    """Represents a node in the circuit hierarchy"""
    full_path: str              # Full dotted path e.g. 'top.subckt0.child'
    normalized_name: str        # Name without numbers e.g. 'child'
    parent_path: Optional[str]  # Parent's full path or None for root
    children: List[str] = field(default_factory=list)  # Child paths
    parts: List['Part'] = field(default_factory=list)  # Parts in this circuit

class HierarchyManager:
    """Manages schematic hierarchy generation"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.nodes: Dict[str, CircuitNode] = {}
        self.generated_files: Set[str] = set()
        
    def normalize_circuit_name(self, path: str) -> str:
        """Get normalized name from path (last segment, no numbers unless 'top')"""
        segments = path.split('.')
        last_segment = segments[-1]
        if last_segment == 'top':
            return last_segment
        return re.sub(r'\d+$', '', last_segment)


    def build_hierarchy(self, subcircuit_paths: List[str]) -> None:
        """Build hierarchy from subcircuit paths"""
        # First pass: Create nodes
        for path in subcircuit_paths:
            parts = path.split('.')
            if len(parts) == 1:
                parent = None
            else:
                parent = '.'.join(parts[:-1])
                
            node = CircuitNode(
                full_path=path,
                normalized_name=self.normalize_circuit_name(path),
                parent_path=parent
            )
            self.nodes[path] = node
            
        # Second pass: Link children
        for node in self.nodes.values():
            if node.parent_path:
                if node.parent_path in self.nodes:
                    parent = self.nodes[node.parent_path]
                    parent.children.append(node.full_path)

    def assign_parts_to_circuits(self, circuit) -> None:
        """Assign parts to their circuits based on hierarchy"""
        for part in circuit.parts:
            hierarchy = getattr(part, 'hierarchy', None)
            if hierarchy:
                # Need to find the matching node
                for node in self.nodes.values():
                    # Compare the full path but with normalized last segments
                    if self.normalize_path_for_matching(hierarchy) == self.normalize_path_for_matching(node.full_path):
                        node.parts.append(part)
                        # Set Sheetname to normalized name 
                        setattr(part, 'Sheetname', node.normalized_name)
                        break

    def normalize_path_for_matching(self, path: str) -> str:
        """Normalize a path for matching by stripping digits only from last segment"""
        segments = path.split('.')
        if len(segments) == 0:
            return path
        # Keep all segments except last as-is
        result = segments[:-1]
        # Normalize last segment
        last = segments[-1]
        if last != 'top':
            last = re.sub(r'\d+$', '', last)
        result.append(last)
        return '.'.join(result)

    def _generate_circuit_schematic(self, node: CircuitNode, writer_class) -> None:
        """Generate schematic for a circuit node"""
        out_path = self.project_dir / f"{node.normalized_name}.kicad_sch"
        if out_path.name in self.generated_files:
            return  # Already generated this file
                
        # Create a new writer instance for this specific schematic file
        writer = writer_class(str(out_path))  # Pass the full file path
        
        # Create schematic with parts
        grid_size = 20.0
        for idx, part in enumerate(node.parts):
            row = idx // 5
            col = idx % 5
            x = float(col * grid_size)
            y = float(-row * grid_size)
            
            writer.add_symbol_instance(self._create_symbol_instance(
                part, 
                position=(x, y)
            ))
                
        writer.generate()
        self.generated_files.add(out_path.name)

    def generate_schematics(self, writer_class, project_name: str) -> None:
        """Generate all schematic files"""
        # Always create top schematic first
        self._generate_top_schematic(writer_class, project_name)
        
        # Generate child schematics (only once per normalized name)
        generated = set()
        for node in self.nodes.values():
            if node.normalized_name != 'top' and node.normalized_name not in generated:
                self._generate_circuit_schematic(node, writer_class)  # Pass writer class instead of instance
                generated.add(node.normalized_name)

    def _generate_top_schematic(self, writer, project_name: str) -> None:
        """Generate top-level schematic with sheet symbols"""
        out_path = self.project_dir / f"{project_name}.kicad_sch"
        
        # Create basic schematic
        sch = Schematic.create_new()
        
        # Add sheet symbols for immediate children of top
        sheet_x = 100
        for node in self.nodes.values():
            if node.parent_path == 'top':
                sheet = HierarchicalSheet()
                
                # Position and size
                sheet.position = Position(f"{sheet_x}", "50", "0")
                sheet.width = 30
                sheet.height = 20
                
                # Sheet properties
                sheet.sheetName = Property("Sheetname", node.normalized_name)
                sheet.sheetName.position = Position(
                    f"{sheet_x + sheet.width/2}", "45", "0"
                )
                
                sheet.fileName = Property(
                    "Sheetfile", 
                    f"{node.normalized_name}.kicad_sch"
                )
                sheet.fileName.position = Position(
                    f"{sheet_x + sheet.width/2}", "48", "0"
                )
                
                sch.sheets.append(sheet)
                sheet_x += 50  # Space between sheets
                
        sch.to_file(str(out_path))

    def _create_symbol_instance(self, part, position: tuple = (0, 0)) -> 'SchematicSymbolInstance':
        """Create symbol instance from part 
        
        Args:
            part: The SKiDL Part object
            position: Tuple of (x,y) coordinates for placement
        """
        lib_name = getattr(part.lib, 'filename', "Device")
        lib_id = f"{lib_name}:{part.name}"
        
        return SchematicSymbolInstance(
            lib_id=lib_id,
            reference=part.ref,
            value=part.value,
            position=position,  # Use passed position
            footprint=getattr(part, 'footprint', None)
        )