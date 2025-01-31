#!/usr/bin/env python3
# gen_schematic_v8.py

import datetime
import os
import os.path
import shutil
import uuid
from pathlib import Path
from skidl.scriptinfo import get_script_name
from skidl.logger import active_logger

from .hierarchy_manager import HierarchyManager
from .kicad_writer import KicadSchematicWriter

def setup_debug_printing():
    """Configure debug print statements with environment variable control."""
    debug_level = os.getenv('SKIDL_DEBUG', 'INFO').upper()
    debug_enabled = debug_level != 'OFF'
    
    def debug_print(section, *args, level='INFO', **kwargs):
        if debug_enabled and (debug_level == 'ALL' or level == debug_level):
            prefix = f"[{section:^10}]"
            print(f"{prefix}", *args, **kwargs)
            
    return debug_print

debug_print = setup_debug_printing()

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
    Create hierarchical KiCad schematic files from a SKiDL Circuit object.
    """
    debug_print("GENSCM", f"Generating project '{project_name}' in '{filepath}'")
    
    # -------------------------------------------------------------------------
    # Step 1) Copy blank KiCad project template into project_dir
    # -------------------------------------------------------------------------
    try:
        template_dir = os.path.join(
            os.path.dirname(__file__),
            "kicad_blank_project",
            "kicad_blank_project"
        )
        project_dir = os.path.join(filepath, project_name)

        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        shutil.copytree(template_dir, project_dir)
        
        active_logger.info(f"Using KiCad blank project directory: {project_dir}")
        debug_print("GENSCM", f"Template copied to {project_dir}")
    except Exception as e:
        active_logger.error(f"Failed to setup project folder: {str(e)}")
        raise
    
    # -------------------------------------------------------------------------
    # Step 2) Create and setup the hierarchy manager
    # -------------------------------------------------------------------------
    hierarchy = HierarchyManager(project_dir)
    
    # Get subcircuit paths from circuit's group_name_cntr
    subcircuit_paths = list(circuit.group_name_cntr.keys())
    if not subcircuit_paths:
        # If no subcircuits defined, create top-level only
        subcircuit_paths = ['top']
        
    debug_print("HIERARCHY", "All subcircuit paths:", subcircuit_paths)
    
    # Build the hierarchy tree
    hierarchy.build_hierarchy(subcircuit_paths)
    
    # Assign parts to their circuits and set Sheetname attributes
    hierarchy.assign_parts_to_circuits(circuit)
    
    # -------------------------------------------------------------------------
    # Step 3) Generate all schematics
    # -------------------------------------------------------------------------
    try:
        # Pass the writer class instead of an instance
        hierarchy.generate_schematics(KicadSchematicWriter, project_name)
    except Exception as e:
        active_logger.error(f"Error generating schematics: {str(e)}")
        raise

    # -------------------------------------------------------------------------
    # Step 4) Update project files
    # -------------------------------------------------------------------------
    try:
        # Rename template project files
        old_files = {
            "kicad_blank_project.kicad_pro": f"{project_name}.kicad_pro",
            "kicad_blank_project.kicad_pcb": f"{project_name}.kicad_pcb",
            "kicad_blank_project.kicad_prl": f"{project_name}.kicad_prl"
        }
        for old_name, new_name in old_files.items():
            old_path = os.path.join(project_dir, old_name)
            new_path = os.path.join(project_dir, new_name)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                active_logger.info(f"Renamed {old_name} to {new_name}")

        # Update .kicad_pro file contents
        project_path = os.path.join(project_dir, f"{project_name}.kicad_pro")
        if os.path.exists(project_path):
            import json
            with open(project_path, 'r') as f:
                project_config = json.load(f)

            # Update meta filename
            project_config['meta']['filename'] = f"{project_name}.kicad_pro"

            # Add generated sheets to project
            sheets = [
                {
                    "path": f"{project_name}.kicad_sch",  # Top sheet
                    "sheet_name": "",
                    "id": str(uuid.uuid4())
                }
            ]
            
            # Add subcircuit sheets (if any)
            for node in hierarchy.nodes.values():
                if node.sheet_name != 'top':  # Use sheet_name instead of normalized_name
                    sheets.append({
                        "path": f"{node.sheet_name}.kicad_sch",  # Use sheet_name
                        "sheet_name": node.sheet_name,  # Use sheet_name
                        "id": str(uuid.uuid4())
                    })
            
            project_config['sheets'] = sheets

            with open(project_path, 'w') as f:
                json.dump(project_config, f, indent=2)
            active_logger.info(f"Updated project configuration in {project_path}")
    
    except Exception as e:
        active_logger.error(f"Error updating project files: {str(e)}")
        raise
        
    # All done successfully
    active_logger.info("No errors or warnings found while generating schematic.")