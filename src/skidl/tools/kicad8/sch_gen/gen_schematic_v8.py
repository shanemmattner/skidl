# gen_schematic_v9.py

import datetime
import os.path
import shutil
import uuid
from skidl.scriptinfo import get_script_name

from .kicad_writer import KicadSchematicWriter, SchematicSymbolInstance

from kiutils.schematic import Schematic
from kiutils.items.common import Position, TitleBlock, Property, ColorRGBA, Stroke
from kiutils.items.schitems import HierarchicalSheet, HierarchicalSheetInstance


class HierarchyNode:
    """Represents a node in the schematic hierarchy."""
    def __init__(self, name, parent=None):
        self.name = name  # Base name without numeric suffix
        self.full_name = name  # Full path including suffix
        self.parent = parent
        self.children = []
        self.uuid = str(uuid.uuid4())
    
    def get_path(self):
        """Get full hierarchical path from root to this node."""
        if not self.parent or self.parent.name == "top":
            return f"/{self.uuid}"
        return f"{self.parent.get_path()}/{self.uuid}"
    
    def __repr__(self):
        return f"HierarchyNode(name='{self.name}', full_name='{self.full_name}')"

def build_hierarchy_tree(group_name_cntr):
    """
    Build a tree from group_name_cntr dot-separated paths.
    
    Args:
        group_name_cntr: Counter with dot-separated hierarchy paths
        
    Returns:
        HierarchyNode: Root of the hierarchy tree
    """
    root = HierarchyNode("top")
    nodes = {"top": root}
    
    # Sort paths so parents are processed before children
    paths = sorted(group_name_cntr.keys(), key=lambda x: len(x.split('.')))
    
    for path in paths:
        if path == "top":
            continue
            
        # Split path and get node name
        parts = path.split('.')
        node_name = parts[-1].rstrip('0123456789')  # Strip numeric suffix
        parent_path = '.'.join(parts[:-1])
        
        if parent_path in nodes:
            node = HierarchyNode(node_name, nodes[parent_path])
            node.full_name = path  # Store full path including suffix
            nodes[parent_path].children.append(node)
            nodes[path] = node
    
    return root


def setup_debug_printing():
    """Configure debug print statements with environment variable control"""
    import os
    debug_level = os.getenv('SKIDL_DEBUG', 'INFO').upper()
    debug_enabled = debug_level != 'OFF'
    
    def debug_print(section, *args, level='INFO', **kwargs):
        if debug_enabled and (debug_level == 'ALL' or level == debug_level):
            prefix = f"[{section:^10}]"
            print(f"{prefix}", *args, **kwargs)
            
    return debug_print

debug_print = setup_debug_printing()

def print_component_info(part):
    """Print detailed component information for debugging"""
    debug_print("COMP", "-" * 40)
    debug_print("COMP", f"Reference : {part.ref}")
    debug_print("COMP", f"Library   : {part.lib}")
    debug_print("COMP", f"Name      : {part.name}")
    debug_print("COMP", f"Value     : {part.value}")
    debug_print("COMP", f"Sheet     : {getattr(part, 'Sheetname', 'default')}")
    debug_print("COMP", f"Pins      : {len(part.pins)}")
    if hasattr(part, 'footprint'):
        debug_print("COMP", f"Footprint : {part.footprint}")
    debug_print("COMP", "-" * 40)


def collect_subcircuit_parts(circuit, node):
    """
    Collect parts belonging to a specific node in hierarchy.
    
    Args:
        circuit: The SKiDL Circuit object
        node: HierarchyNode representing the sheet
        
    Returns:
        list: Parts that belong to this sheet
    """
    parts = []
    # Need to match parts to the full hierarchical name in group_name_cntr
    node_path = node.full_name  # This includes the numeric suffix
    
    for part in circuit.parts:
        # Get all paths in hierarchical_names that match this node's path
        matching_paths = [p for p in circuit._hierarchical_names if p.startswith(node_path)]
        if matching_paths:
            parts.append(part)
            
    return parts

def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    project_name="kicad_blank_project",
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """
    Create schematic files from a Circuit object with proper sheet hierarchy.
    """
    from skidl.logger import active_logger
    
    # 1. Setup project directory
    template_dir = os.path.join(
        os.path.dirname(__file__), 
        "kicad_blank_project",
        "kicad_blank_project"
    )
    project_dir = os.path.join(filepath, project_name)
    
    try:
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        os.makedirs(project_dir)
        
        for item in os.listdir(template_dir):
            source = os.path.join(template_dir, item)
            dest = os.path.join(project_dir, item)
            if os.path.isdir(source):
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
                
        active_logger.info(f"Using KiCad blank project directory: {project_dir}")
    except Exception as e:
        active_logger.error(f"Failed to setup project folder: {str(e)}")
        raise
    
    # 2. Build hierarchy tree
    hierarchy = build_hierarchy_tree(circuit.group_name_cntr)
    
    # 3. Create and process sheets recursively
    def process_hierarchy_node(node, parent_path=""):
        debug_print("SHEET", f"Processing sheet: {node.name}")
        
        # Create schematic for this sheet
        sheet_sch_path = os.path.join(project_dir, f"{node.name}.kicad_sch")
        writer = KicadSchematicWriter(sheet_sch_path)
        
        # Add components for this sheet
        sheet_parts = collect_subcircuit_parts(circuit, node)
        for part in sheet_parts:
            print_component_info(part)
            symbol = SchematicSymbolInstance(
                lib_id=f"{part.lib}:{part.name}",
                reference=part.ref,
                value=part.value,
                position=(0, 0),
                rotation=0,
                footprint=getattr(part, 'footprint', None)
            )
            writer.add_symbol_instance(symbol)
        
        # Add sheet references for children
        for child in node.children:
            writer.add_sheet_reference(child)
        
        # Generate the schematic
        try:
            writer.generate()
            active_logger.info(f"Generated schematic for {node.name}")
        except Exception as e:
            active_logger.error(f"Error generating {node.name}: {str(e)}")
            raise
            
        # Process children recursively
        for child in node.children:
            process_hierarchy_node(child, node.get_path())
            
    # 4. Create main schematic
    main_sch = Schematic.create_new()
    main_sch.version = "20231120"
    main_sch.generator = "eeschema"
    main_sch.uuid = str(uuid.uuid4())
    
    # Add only the top-level sheet
    if hierarchy.children:
        top_sheet = hierarchy.children[0]  # single_resistor
        sheet = HierarchicalSheet()
        sheet.position = Position("125.73", "66.04", "0")
        sheet.width = 13.97
        sheet.height = 15.24
        sheet.stroke = Stroke()
        sheet.fill = ColorRGBA()
        sheet.uuid = top_sheet.uuid
        
        sheet.sheetName = Property(
            key="Sheetname",
            value=top_sheet.name
        )
        sheet.fileName = Property(
            key="Sheetfile",
            value=f"{top_sheet.name}.kicad_sch"
        )
        
        main_sch.sheets = [sheet]
    
    # Save main schematic
    main_sch_path = os.path.join(project_dir, f"{project_name}.kicad_sch")
    try:
        main_sch.to_file(main_sch_path)
        active_logger.info(f"Created main schematic at {main_sch_path}")
    except Exception as e:
        active_logger.error(f"Error saving main schematic: {str(e)}")
        raise
    
    # Process hierarchy starting from top sheet
    if hierarchy.children:
        process_hierarchy_node(hierarchy.children[0])
    
    # 5. Update project configuration
    update_project_config(project_dir, project_name, hierarchy)
    
    return True

def update_project_config(project_dir, project_name, hierarchy):
    """Update project configuration with sheet hierarchy."""
    project_path = os.path.join(project_dir, f"{project_name}.kicad_pro")
    if os.path.exists(project_path):
        import json
        with open(project_path, 'r') as f:
            project_config = json.load(f)
        
        # Update sheets configuration
        project_config['sheets'] = [
            {
                "path": f"{project_name}.kicad_sch",
                "sheet_name": "",
                "id": str(uuid.uuid4())
            }
        ]
        
        def add_sheet_to_config(node):
            project_config['sheets'].append({
                "path": f"{node.name}.kicad_sch",
                "sheet_name": node.name,
                "id": node.uuid
            })
            for child in node.children:
                add_sheet_to_config(child)
        
        # Add all sheets from hierarchy
        if hierarchy.children:
            add_sheet_to_config(hierarchy.children[0])
        
        # Write updated configuration
        with open(project_path, 'w') as f:
            json.dump(project_config, f, indent=2)
