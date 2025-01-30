# gen_schematic_v8.py

import datetime
import os.path
import shutil
import uuid
from skidl.scriptinfo import get_script_name

from .kicad_writer import KicadSchematicWriter, SchematicSymbolInstance


from kiutils.schematic import Schematic
from kiutils.items.common import Position, TitleBlock, Property, ColorRGBA, Stroke
from kiutils.items.schitems import HierarchicalSheet


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
    debug_print("COMP", f"Library   : {part.lib.filename}")
    debug_print("COMP", f"Name      : {part.name}")
    debug_print("COMP", f"Value     : {part.value}")
    debug_print("COMP", f"Sheet     : {getattr(part, 'Sheetname', 'default')}")
    debug_print("COMP", f"Pins      : {len(part.pins)}")
    if hasattr(part, 'footprint'):
        debug_print("COMP", f"Footprint : {part.footprint}")
    if hasattr(part, 'position'):
        debug_print("COMP", f"Position  : ({part.position.X}, {part.position.Y})")
    debug_print("COMP", "-" * 40)


def print_placement_info(component, x, y, grid_size):
    """Print placement information for debugging"""
    debug_print("PLACE", "-" * 40)
    debug_print("PLACE", f"Component  : {component.ref}")
    debug_print("PLACE", f"Position   : ({x}, {y})")
    debug_print("PLACE", f"Grid Size  : {grid_size}")
    debug_print("PLACE", "-" * 40)


def gen_schematic(
    circuit,
    filepath=".",
    top_name=get_script_name(),
    project_name="kicad_blank_project",  # <-- NEW ARG: user can override
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """
    Create schematic files from a Circuit object.

    Args:
        circuit: The SKiDL Circuit object
        filepath: Output directory path
        top_name: A default name for the script or top-level
        project_name: The user-provided project folder (and top schematic) name
        title: Title block text
        ...
    """
    from skidl.logger import active_logger
    
    # 1) Setup project directory name using 'project_name'.
    #    So "kicad_blank_project" is replaced by user input.
    template_dir = os.path.join(
        os.path.dirname(__file__), 
        "kicad_blank_project",      # This is your *template* folder name on disk
        "kicad_blank_project"       # containing the blank project files to copy
    )
    # We'll create the new project folder as user has requested:
    project_dir = os.path.join(filepath, project_name)
    
    # 2) Copy the blank project template into project_dir
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
    
    # 3) Gather subcircuits from the SKiDL circuit
    subcircuits = circuit.group_name_cntr.keys()

    # For each subcircuit, build a separate schematic
    for subcircuit_path in subcircuits:
        subcircuit_name = subcircuit_path.split('.')[-1]
        debug_print("SHEET", f"Looking for components in sheet: {subcircuit_name}")

        # Build the path: e.g. /my/path/<project_name>/<sheet>.kicad_sch
        subcircuit_sch_path = os.path.join(project_dir, f"{subcircuit_name}.kicad_sch")
        
        # Instead of "test.kicad_sch", pass this path to the writer:
        writer = KicadSchematicWriter(subcircuit_sch_path)
        
        components_found = 0
        grid_size = 20.0
        symbol_count = 0

        for part in circuit.parts:
            # Use subcircuit name as default sheet name if Sheetname not provided
            part_sheet = getattr(part, 'Sheetname', subcircuit_name)
            if part_sheet == subcircuit_name:
                components_found += 1
                debug_print("MATCH", f"Found component {part.ref} in {subcircuit_name}")
                print_component_info(part)
                
                # Calculate position
                row = symbol_count // 5  # 5 symbols per row
                col = symbol_count % 5
                x = float(col * grid_size)
                y = float(row * -grid_size)
                
                # Build the lib_id from part.lib.filename:name
                symbol = SchematicSymbolInstance(
                    lib_id=f"{part.lib.filename}:{part.name}",
                    reference=part.ref,
                    value=part.value,
                    position=(x, y),
                    rotation=0,
                    footprint=getattr(part, 'footprint', None)
                )
                
                print_placement_info(part, x, y, grid_size)
                debug_print("SYMBOL", f"Adding symbol {part.ref} to schematic")
                writer.add_symbol_instance(symbol)
                
                symbol_count += 1
            else:
                # Not in this sheet => skip
                debug_print("SKIP", f"{part.ref} (in {part.Sheetname})")

        debug_print("SHEET", f"Found {components_found} components in {subcircuit_name}")

        # 4) Actually generate the subcircuit schematic into <subcircuit_name>.kicad_sch
        try:
            writer.generate()  # This writes to subcircuit_sch_path now!
            active_logger.info(f"Generated schematic for {subcircuit_name} at {subcircuit_sch_path}")
            print(f"Generated schematic for {subcircuit_name} at {subcircuit_sch_path}")
        except Exception as e:
            active_logger.error(f"Error saving schematic {subcircuit_name}: {str(e)}")
            raise

    # 5) Now add the hierarchical sheets to the *top-level* schematic file.
    #    We'll rename that top-level file to <project_name>.kicad_sch
    main_sch_name = f"{project_name}.kicad_sch"
    main_sch_path = os.path.join(project_dir, main_sch_name)

    # In your template, the default blank schematic might be named "kicad_blank_project.kicad_sch".
    # So we rename it or re-load it below:
    old_main_sch = os.path.join(project_dir, "kicad_blank_project.kicad_sch")
    
    try:
        if os.path.exists(old_main_sch):
            # rename the file to <project_name>.kicad_sch
            os.rename(old_main_sch, main_sch_path)
        else:
            # fallback if the template doesn't have "kicad_blank_project.kicad_sch"
            # create a brand-new minimal top schematic
            main_sch = Schematic.create_new()
            main_sch.to_file(main_sch_path)

        # Load with KiCad Python tools (kiutils, or your own method)
        main_sch = Schematic.from_file(main_sch_path)
    except Exception as e:
        active_logger.error(f"Error creating/loading main schematic: {e}")
        # Fallback to creating a completely new schematic
        main_sch = Schematic.create_new()
        main_sch.to_file(main_sch_path)
    
    # Build hierarchical sheet symbols in a simple grid
    sheet_width = 30  # mm
    sheet_height = 30
    spacing = 40
    sheets_per_row = 2
    
    num_sheets = len(subcircuits)
    num_rows = (num_sheets + sheets_per_row - 1) // sheets_per_row
    num_cols = min(sheets_per_row, num_sheets)
    
    total_width = num_cols * sheet_width + (num_cols - 1) * spacing
    total_height = num_rows * sheet_height + (num_rows - 1) * spacing
    
    # A4 is 297mm x 210mm
    start_x = (297 - total_width) / 2
    start_y = (210 - total_height) / 2
    
    if not hasattr(main_sch, 'sheets'):
        main_sch.sheets = []
        
    i = 0
    for subcircuit_path in subcircuits:
        subcircuit_name = subcircuit_path.split('.')[-1]
        
        row = i // sheets_per_row
        col = i % sheets_per_row
        x = start_x + col * (sheet_width + spacing)
        y = start_y + row * (sheet_height + spacing)
        i += 1
        
        # Create hierarchical sheet
        sheet = HierarchicalSheet()
        sheet.position = Position(str(x), str(y), "0")
        sheet.width = sheet_width
        sheet.height = sheet_height
        sheet.stroke = Stroke()
        sheet.fill = ColorRGBA()

        # Sheet name & file
        sheet.sheetName = Property(key="Sheetname", value=subcircuit_name)
        sheet.sheetName.position = Position(
            str(x + sheet_width/2), str(y - 5), "0"
        )
        sheet.fileName = Property(key="Sheetfile", value=f"{subcircuit_name}.kicad_sch")
        sheet.fileName.position = Position(
            str(x + sheet_width/2), str(y - 2), "0"
        )
        
        main_sch.sheets.append(sheet)
    
    # Save updated top-level schematic
    try:
        main_sch.to_file(main_sch_path)
        active_logger.info(f"Added sheet symbols to main schematic at {main_sch_path}")
    except Exception as e:
        active_logger.error(f"Error saving main schematic: {str(e)}")
        raise

    # 6) Update project files
    try:
        # Rename project files
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
        
        # Update project configuration
        project_path = os.path.join(project_dir, f"{project_name}.kicad_pro")
        if os.path.exists(project_path):
            import json
            with open(project_path, 'r') as f:
                project_config = json.load(f)
            
            # Update meta filename
            project_config['meta']['filename'] = f"{project_name}.kicad_pro"
            
            # Update sheets configuration
            project_config['sheets'] = [
                {
                    "path": f"{project_name}.kicad_sch",
                    "sheet_name": "",  # Root sheet has no name
                    "id": str(uuid.uuid4())
                }
            ]
            
            # Add hierarchical sheets
            for subcircuit_path in subcircuits:
                subcircuit_name = subcircuit_path.split('.')[-1]
                project_config['sheets'].append({
                    "path": f"{subcircuit_name}.kicad_sch",
                    "sheet_name": subcircuit_name,
                    "id": str(uuid.uuid4())
                })
            
            # Write updated configuration
            with open(project_path, 'w') as f:
                json.dump(project_config, f, indent=2)
            active_logger.info(f"Updated project configuration in {project_path}")
    except Exception as e:
        active_logger.error(f"Error updating project files: {str(e)}")
        raise
