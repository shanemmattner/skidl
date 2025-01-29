# -*- coding: utf-8 -*-

import datetime
import os.path
import shutil
from skidl.scriptinfo import get_script_name

#
# IMPORTANT: The lines below now reference the updated kicad_writer.py,
# which includes a robust s-expression parser & symbol inheritance flattening.
#
# >>> KEY CHANGE: Make sure kicad_writer.py implements parse + flatten logic <<<
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
    debug_print("COMP", f"Sheet     : {part.Sheetname}")
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
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """Create schematic files from a Circuit object."""
    from skidl.logger import active_logger
    
    # Setup project directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template_dir = os.path.join(os.path.dirname(__file__), "kicad_blank_project", "kicad_blank_project")
    blank_project_dir = os.path.join(filepath, "kicad_blank_project")
    
    try:
        if os.path.exists(blank_project_dir):
            shutil.rmtree(blank_project_dir)
        os.makedirs(blank_project_dir)
        
        for item in os.listdir(template_dir):
            source = os.path.join(template_dir, item)
            dest = os.path.join(blank_project_dir, item)
            if os.path.isdir(source):
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
                
        active_logger.info(f"Using KiCad blank project directory: {blank_project_dir}")
    except Exception as e:
        active_logger.error(f"Failed to setup blank project: {str(e)}")
        raise
    
    # Get all subcircuits
    subcircuits = circuit.group_name_cntr.keys()

    for subcircuit_path in subcircuits:
        subcircuit_name = subcircuit_path.split('.')[-1]
        debug_print("SHEET", f"Looking for components in sheet: {subcircuit_name}")
        
        #
        # 1) Create the new KicadSchematicWriter with a library path.
        #    THIS version references the robust parser & flatten approach inside kicad_writer.py
        #
        # >>> KEY CHANGE: We pass in kicad_lib_folder to the new logic that does parse+flatten <<<
        #
        kicad_lib_folder = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"  # <-- Customize as needed!
        writer = KicadSchematicWriter('test.kicad_sch')
        
        components_found = 0
        grid_size = 20.0
        symbol_count = 0

        for part in circuit.parts:
            if part.Sheetname in subcircuit_name:
                components_found += 1
                debug_print("MATCH", f"Found component {part.ref} in {subcircuit_name}")
                print_component_info(part)
                
                # Calculate position
                row = symbol_count // 5  # 5 symbols per row
                col = symbol_count % 5
                x = float(col * grid_size)
                y = float(row * -grid_size)  # Negative for KiCad coordinate system
                
                # Build the lib_id from part.lib.filename and part.name
                # e.g. "Regulator_Linear:NCP1117-3.3_SOT223"
                # >>> KEY CHANGE: We are using 'SchematicSymbol' consistent with kicad_writer's robust approach <<<
                symbol = SchematicSymbolInstance(
                    lib_id=f"{part.lib.filename}:{part.name}",
                    reference=part.ref,
                    value=part.value,
                    position=(x, y),
                    rotation=0,
                    footprint=part.footprint if hasattr(part, 'footprint') else None
                )
                
                print_placement_info(part, x, y, grid_size)
                debug_print("SYMBOL", f"Adding symbol {part.ref} to schematic")
                
                writer.add_symbol_instance(symbol)
                symbol_count += 1
            else:
                debug_print("SKIP", f"{part.ref} (in {part.Sheetname})")
        
        debug_print("SHEET", f"Found {components_found} components in {subcircuit_name}")
        
        # Generate the schematic file
        sch_path = os.path.join(blank_project_dir, f"{subcircuit_name}.kicad_sch")
        try:
            # >>> KEY CHANGE: Instead of writer.generate(...), we might call writer.generate_schematic(...) 
            # if that's how your new logic is named. Adjust as needed.
            writer.generate()
            active_logger.info(f"Generated schematic for {subcircuit_name} at {sch_path}")
            print(f"Generated schematic for {subcircuit_name} at {sch_path}")
        except Exception as e:
            active_logger.error(f"Error saving schematic {subcircuit_name}: {str(e)}")
            raise

    # Now add sheet symbols to main schematic
    main_sch_path = os.path.join(blank_project_dir, "kicad_blank_project.kicad_sch")
    main_sch = Schematic.from_file(main_sch_path)
    
    # Grid layout settings for sheet symbols
    sheet_width = 30  # mm
    sheet_height = 30  # mm
    spacing = 40  # mm between sheets
    sheets_per_row = 2
    
    # Calculate layout dimensions
    num_sheets = len(subcircuits)
    num_rows = (num_sheets + sheets_per_row - 1) // sheets_per_row
    num_cols = min(sheets_per_row, num_sheets)
    
    total_width = num_cols * sheet_width + (num_cols - 1) * spacing
    total_height = num_rows * sheet_height + (num_rows - 1) * spacing
    
    # Calculate starting position to center sheets (A4 dimensions = 297mm x 210mm)
    start_x = (297 - total_width) / 2
    start_y = (210 - total_height) / 2
    
    # Create sheets for each subcircuit
    if not hasattr(main_sch, 'sheets'):
        main_sch.sheets = []
        
    for i, subcircuit_path in enumerate(subcircuits):
        subcircuit_name = subcircuit_path.split('.')[-1]
        
        # Calculate grid position
        row = i // sheets_per_row
        col = i % sheets_per_row
        x = start_x + col * (sheet_width + spacing)
        y = start_y + row * (sheet_height + spacing)
        
        # Create hierarchical sheet
        sheet = HierarchicalSheet()
        sheet.position = Position()
        sheet.position.X = str(x)
        sheet.position.Y = str(y)
        sheet.position.angle = "0"
        
        sheet.width = sheet_width
        sheet.height = sheet_height
        
        sheet.stroke = Stroke()
        sheet.fill = ColorRGBA()
        
        # Set sheet properties
        sheet.sheetName = Property(key="Sheet name")
        sheet.sheetName.value = subcircuit_name
        sheet.sheetName.position = Position()
        sheet.sheetName.position.X = str(x + sheet_width / 2)
        sheet.sheetName.position.Y = str(y - 5)
        sheet.sheetName.position.angle = "0"
        
        sheet.fileName = Property(key="Sheet file")
        sheet.fileName.value = f"{subcircuit_name}.kicad_sch"
        sheet.fileName.position = Position()
        sheet.fileName.position.X = str(x + sheet_width / 2)
        sheet.fileName.position.Y = str(y - 2)
        sheet.fileName.position.angle = "0"
        
        main_sch.sheets.append(sheet)
    
    # Save main schematic with added sheets
    try:
        main_sch.to_file(main_sch_path)
        active_logger.info(f"Added sheet symbols to main schematic at {main_sch_path}")
    except Exception as e:
        active_logger.error(f"Error saving main schematic: {str(e)}")
        raise
