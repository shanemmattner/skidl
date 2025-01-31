from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path
import re
import uuid
import logging
from kiutils.schematic import Schematic
from kiutils.items.common import Position, Property
from kiutils.items.schitems import HierarchicalSheet
from .kicad_writer import SchematicSymbolInstance

def get_sheet_name(path: str) -> str:
    """Extract sheet name without numeric suffixes for file naming"""
    segments = path.split('.')
    last = segments[-1]
    if last == 'top':
        return last
    return re.sub(r'\d+$', '', last)

def get_instance_path(part) -> str:
    """Get full hierarchical instance path for part matching"""
    h = getattr(part, 'hierarchy', None)
    if h:
        return h
    return getattr(part, 'Sheetname', "top")

@dataclass
class CircuitNode:
    """Represents a node in the circuit hierarchy"""
    instance_path: str          # Full path with numbers e.g. 'top.subckt0.child1'
    sheet_name: str            # Name for sheet file e.g. 'child'
    parent_path: Optional[str]  # Parent's full instance path or None for root
    children: List[str] = field(default_factory=list)  # Child instance paths
    parts: List['Part'] = field(default_factory=list)  # Parts in this circuit instance

class HierarchyManager:
    """Manages schematic hierarchy generation"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.nodes: Dict[str, CircuitNode] = {}
        self.generated_files: Set[str] = set()
        self.valid_paths: Set[str] = set()
        
    def build_hierarchy(self, subcircuit_paths: List[str]) -> None:
        """Build hierarchy from subcircuit paths"""
        logging.debug("Building hierarchy from paths:")
        for path in subcircuit_paths:
            logging.debug(f"  Processing path: {path}")
        
        # Store valid instance paths
        self.valid_paths = set(subcircuit_paths)
        
        # Create nodes
        for path in subcircuit_paths:
            parts = path.split('.')
            parent = '.'.join(parts[:-1]) if len(parts) > 1 else None
            
            logging.debug(f"Creating node:")
            logging.debug(f"  Instance path: {path}")
            logging.debug(f"  Sheet name: {get_sheet_name(path)}")
            logging.debug(f"  Parent path: {parent}")
            
            node = CircuitNode(
                instance_path=path,
                sheet_name=get_sheet_name(path),
                parent_path=parent
            )
            self.nodes[path] = node
        
        # Link children using instance paths
        for node in self.nodes.values():
            if node.parent_path and node.parent_path in self.nodes:
                parent = self.nodes[node.parent_path]
                parent.children.append(node.instance_path)
                logging.debug(f"Linked child {node.instance_path} to parent {parent.instance_path}")

    def assign_parts_to_circuits(self, circuit) -> None:
        """Assign parts to their circuit instances"""
        logging.debug("\nAssigning parts to circuits:")
        for part in circuit.parts:
            # Get instance path with numbers preserved
            instance_path = get_instance_path(part)
            logging.debug(f"\nProcessing part {part.ref}:")
            logging.debug(f"  Instance path: {instance_path}")
            
            # Try exact match first
            if instance_path in self.nodes:
                node = self.nodes[instance_path]
                node.parts.append(part)
                logging.debug(f"  Assigned to node: {node.instance_path}")
                logging.debug(f"  Sheet file will be: {node.sheet_name}.kicad_sch")
                continue
                
            # Try matching without numeric suffixes
            base_path = '.'.join(get_sheet_name(segment) for segment in instance_path.split('.'))
            matching_nodes = [
                node for node in self.nodes.values()
                if '.'.join(get_sheet_name(segment) for segment in node.instance_path.split('.')) == base_path
            ]
            
            if matching_nodes:
                node = matching_nodes[0]  # Use first matching node
                node.parts.append(part)
                logging.debug(f"  Assigned to matching node: {node.instance_path}")
                logging.debug(f"  Sheet file will be: {node.sheet_name}.kicad_sch")
            else:
                logging.warning(f"  No matching node found for path: {instance_path}")
                logging.debug(f"  Valid paths are: {self.valid_paths}")

    def _generate_circuit_schematic(self, node: CircuitNode, writer_class) -> None:
        """Generate schematic for a circuit node"""
        logging.debug(f"\nGenerating schematic for node:")
        logging.debug(f"  Instance path: {node.instance_path}")
        logging.debug(f"  Sheet name: {node.sheet_name}")
        
        # Use sheet name (without numbers) for file
        out_path = self.project_dir / f"{node.sheet_name}.kicad_sch"
        logging.debug(f"  Output file: {out_path}")
        
        if out_path.name in self.generated_files:
            logging.debug("  Sheet already exists, skipping generation")
            return
        
        # Create writer for this sheet
        writer = writer_class(str(out_path))
        
        # Add all parts from this instance
        logging.debug(f"  Adding {len(node.parts)} parts:")
        grid_size = 20.0
        for idx, part in enumerate(node.parts):
            row = idx // 5
            col = idx % 5
            x = float(col * grid_size)
            y = float(-row * grid_size)
            
            logging.debug(f"    Part {part.ref} at position ({x}, {y})")
            writer.add_symbol_instance(self._create_symbol_instance(
                part, 
                position=(x, y)
            ))
        
        # Add sheet symbols for child circuits
        if node.children:
            logging.debug(f"  Adding sheet symbols for {len(node.children)} children:")
            sheet_x = 100
            for child_path in node.children:
                child = self.nodes[child_path]
                logging.debug(f"    Adding sheet symbol for: {child.instance_path}")
                sheet = self._create_sheet_symbol(child, sheet_x, 50)
                writer.add_sheet_symbol(sheet)
                sheet_x += 50  # Space between sheets
                logging.debug(f"    Sheet symbol added at x={sheet_x}")

        writer.generate()
        self.generated_files.add(out_path.name)
        logging.debug("  Sheet generated successfully")

    def _create_sheet_symbol(self, node: CircuitNode, x: float, y: float) -> HierarchicalSheet:
        """Create sheet symbol for circuit instance"""
        sheet = HierarchicalSheet()
        
        # Position and size
        sheet.position = Position(f"{x}", f"{y}", "0")
        sheet.width = 30
        sheet.height = 20
        
        # Use sheet name without path for display name
        sheet.sheetName = Property("Sheetname", node.sheet_name)
        sheet.sheetName.position = Position(f"{x + sheet.width/2}", f"{y - 5}", "0")
        
        # Use sheet name (without numbers) for file reference
        sheet.fileName = Property("Sheetfile", f"{node.sheet_name}.kicad_sch")
        sheet.fileName.position = Position(f"{x + sheet.width/2}", f"{y - 2}", "0")
        
        logging.debug(f"\nCreated sheet symbol:")
        logging.debug(f"  Instance path: {node.instance_path}")
        logging.debug(f"  Sheet file: {node.sheet_name}.kicad_sch")
        
        return sheet

    def generate_schematics(self, writer_class, project_name):
        """Generate all schematics in the hierarchy."""
        logging.debug("\nGenerating all schematics:")
        
        # First generate leaf node schematics (bottom-up)
        for node in self.nodes.values():
            if not node.children:
                logging.debug(f"Generating leaf node: {node.instance_path}")
                self._generate_circuit_schematic(node, writer_class)
                
        # Then generate parent schematics (including sheet symbols)
        for node in self.nodes.values():
            if node.children:
                logging.debug(f"Generating parent node: {node.instance_path}")
                self._generate_circuit_schematic(node, writer_class)
                
        # Finally generate top-level schematic
        self._generate_top_schematic(writer_class, project_name)

    def _generate_top_schematic(self, writer_class, project_name: str) -> None:
        """Generate top-level schematic with sheet symbols"""
        logging.debug("\nGenerating top-level schematic:")
        out_path = self.project_dir / f"{project_name}.kicad_sch"
        
        # Create basic schematic
        sch = Schematic.create_new()
        
        # Add sheet symbols for immediate children of top
        sheet_x = 100
        for node in self.nodes.values():
            if node.parent_path == 'top':
                logging.debug(f"Adding sheet symbol for: {node.instance_path}")
                sheet = self._create_sheet_symbol(node, sheet_x, 50)
                sch.sheets.append(sheet)
                sheet_x += 50  # Space between sheets
                
        sch.to_file(str(out_path))
        logging.debug("Top schematic generated successfully")

    def _create_symbol_instance(self, part, position: tuple = (0, 0)) -> 'SchematicSymbolInstance':
        """Create symbol instance from part"""
        lib_name = getattr(part.lib, 'filename', "Device")
        lib_id = f"{lib_name}:{part.name}"
        
        return SchematicSymbolInstance(
            lib_id=lib_id,
            reference=part.ref,
            value=part.value,
            position=position,
            footprint=getattr(part, 'footprint', None)
        )