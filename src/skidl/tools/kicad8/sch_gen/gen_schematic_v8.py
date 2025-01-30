#!/usr/bin/env python3
# gen_schematic_v8.py

import datetime
import os
import os.path
import shutil
import uuid
import re
from skidl.scriptinfo import get_script_name
from skidl.logger import active_logger

from kiutils.schematic import Schematic
from kiutils.items.common import Position, TitleBlock, Property, ColorRGBA, Stroke
from kiutils.items.schitems import HierarchicalSheet

from .kicad_writer import KicadSchematicWriter, SchematicSymbolInstance


###############################################################################
# Debug Printing Setup
###############################################################################

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


###############################################################################
# Hierarchy-Building Utilities
###############################################################################

def build_subcircuit_hierarchy(paths):
    """
    Convert a list of dotted subcircuit paths (e.g. 'top.my_subckt0.child_subckt')
    into a tree structure:
       { full_path: { 'name': <leaf>, 'parent': <path or None>, 'children': [child_paths] }, ... }

    If a node’s parent is not itself in `paths`, we treat that node as a root by forcing parent=None.
    """
    import sys

    print("[HIERARCHY ] build_subcircuit_hierarchy() given paths:", paths, file=sys.stderr)
    
    # 1) Create an entry for each path
    tree = {}
    for full_path in paths:
        parts = full_path.split('.')
        if len(parts) == 1:
            # Single token => no parent
            parent = None
            name = parts[0]
        else:
            parent = '.'.join(parts[:-1])
            name = parts[-1]
        tree[full_path] = {
            'name': name,
            'parent': parent,
            'children': []
        }

    # 2) If a node’s parent is NOT in tree, treat it as a root
    for full_path, data in tree.items():
        p = data['parent']
        if p not in tree:
            print(f"[HIERARCHY ]   '{full_path}' has parent '{p}' not in tree; making it a root.", file=sys.stderr)
            data['parent'] = None

    # 3) Link up children for those who have a parent in the tree
    for full_path, data in tree.items():
        p = data['parent']
        if p is not None:
            tree[p]['children'].append(full_path)

    # 4) Print out the final structure for debugging
    print("[HIERARCHY ] Final subcircuit tree structure:", file=sys.stderr)
    for fp, info in tree.items():
        print(f"   PATH='{fp}', parent='{info['parent']}', children={info['children']}", file=sys.stderr)

    return tree


def get_part_hierarchy_raw(part):
    """
    Return the raw path assigned by SKiDL, if any.
    For many SKiDL versions, this is `part.hierarchy`.
    Otherwise, fallback to something like `Sheetname` or 'top'.
    """
    h = getattr(part, 'hierarchy', None)
    if h:
        return h
    # If there's no hierarchy attribute, fallback:
    return getattr(part, 'Sheetname', "top")


def remove_trailing_digits(token):
    """
    If token ends in purely numeric digits, strip them off. E.g. 'my_subckt123' -> 'my_subckt'.
    If 'my_subckt123a' or 'regulator_3v3' => no match because the trailing part isn't purely digits.
    """
    m = re.match(r'^(.*?)(\d+)$', token)
    if m:
        return m.group(1)  # everything before the digits
    return token


def normalize_path(part_path, valid_paths):
    """
    If `part_path` is in valid_paths, return it directly.

    Otherwise, we attempt repeatedly to remove purely numeric suffixes from
    *each token (from last to first)* in the dotted path, forming new candidates,
    and checking if that candidate is in valid_paths.

    E.g.:
      - 'top.single_resistor0' => if not in valid_paths, remove trailing digits from
        'single_resistor0' => 'single_resistor', => new path: 'top.single_resistor'.
        If that's in valid_paths, great -> return it.
      - If not found, move to the next token up the chain, etc.

    This lets us unify e.g. 'top.single_resistor0.two_resistors_circuit0'
    to 'top.single_resistor0.two_resistors_circuit', if that’s in valid_paths.
    Or further to 'top.single_resistor.two_resistors_circuit' if needed.
    """
    if part_path in valid_paths:
        return part_path

    original_tokens = part_path.split('.')

    # We'll attempt removing trailing digits from tokens[i], one token at a time,
    # checking if that yields a recognized path in valid_paths. If found, return it.
    tokens = original_tokens[:]

    # We'll do a nested loop so we handle multiple subcircuit suffixes, e.g. "child0.grandchild0"
    # We'll do up to len(tokens) * attempts. On each pass, we remove digits from the last token that still has them, then check.
    # If no match, revert that token, move to the next. This might be overkill, but robust.

    # We'll keep track of which tokens we've tried to strip. 
    n = len(tokens)
    for i in range(n):  # We won't do more than n attempts in practice
        # Start from the last token that hasn't been permanently stripped yet
        # We'll go in descending order
        for idx in reversed(range(n)):
            old_token = tokens[idx]
            new_token = remove_trailing_digits(old_token)
            if new_token == old_token:
                # nothing changed, skip
                continue
            # we changed something
            tokens[idx] = new_token
            candidate = '.'.join(tokens)
            if candidate in valid_paths:
                return candidate
            # revert and keep going
            tokens[idx] = old_token

    # If we never found a match, return original
    return part_path


###############################################################################
# Recursive Generation of Each Subcircuit
###############################################################################

def generate_subcircuit_schematic(full_path, hierarchy_dict, circuit, project_dir, valid_paths):
    """
    Recursively generate a .kicad_sch for the subcircuit node `full_path`.
    1) Finds all SKiDL Parts whose normalized hierarchy path matches `full_path`.
    2) Creates <subckt_name>.kicad_sch placing those parts.
    3) Recursively adds child subcircuits as HierarchicalSheet references.
    """
    node = hierarchy_dict[full_path]
    subckt_name = node['name']  # e.g. "two_resistors_circuit"
    
    # -------------------------------------------------------------------------
    # 1) Gather parts that belong to this subcircuit path
    # -------------------------------------------------------------------------
    parts_for_this_node = []
    for part in circuit.parts:
        raw_hier = get_part_hierarchy_raw(part)
        # Attempt to unify if not in valid_paths
        normed = normalize_path(raw_hier, valid_paths)
        if normed == full_path:
            parts_for_this_node.append(part)

    debug_print("HIERARCHY", f"Building schematic for {full_path} -> {subckt_name}")
    debug_print("HIERARCHY", f"  Found {len(parts_for_this_node)} parts in {subckt_name}")
    
    # -------------------------------------------------------------------------
    # 2) Create or overwrite <subckt_name>.kicad_sch with these parts
    # -------------------------------------------------------------------------
    out_sch_path = os.path.join(project_dir, f"{subckt_name}.kicad_sch")
    writer = KicadSchematicWriter(out_sch_path)
    
    grid_size = 20.0
    for idx, part in enumerate(parts_for_this_node):
        row = idx // 5
        col = idx % 5
        x = float(col * grid_size)
        y = float(-row * grid_size)
        
        # Build the lib_id from part's library and name
        lib_name = getattr(part.lib, 'filename', "Device")  # fallback if not found
        symbol_name = part.name
        lib_id = f"{lib_name}:{symbol_name}"
        
        debug_print("SYMBOL", f" + Adding symbol {part.ref} at ({x},{y}) in {subckt_name}")
        symbol = SchematicSymbolInstance(
            lib_id=lib_id,
            reference=part.ref,
            value=part.value,
            position=(x, y),
            rotation=0,
            footprint=getattr(part, 'footprint', None)
        )
        writer.add_symbol_instance(symbol)
    
    # Actually write out the schematic for this node
    writer.generate()
    
    # -------------------------------------------------------------------------
    # 3) Add child subcircuits as hierarchical sheets in <subckt_name>.kicad_sch
    # -------------------------------------------------------------------------
    if not node['children']:
        # No children => done
        return
    
    # If there are children, open the just-created .kicad_sch with kiutils:
    sch_obj = Schematic.from_file(out_sch_path)
    debug_print("HIERARCHY", f"Creating {len(node['children'])} child sheet(s) in {subckt_name}")
    
    # Place the child sheets in a small grid
    sheet_width = 30
    sheet_height = 20
    spacing = 40
    
    for i, child_path in enumerate(node['children']):
        child_name = hierarchy_dict[child_path]['name']
        
        # Build a HierarchicalSheet object
        hs = HierarchicalSheet()
        hs.position = Position(str(100 + i*(sheet_width+spacing)), "50", "0")
        hs.width = sheet_width
        hs.height = sheet_height
        hs.stroke = Stroke()
        hs.fill = ColorRGBA()
        
        # sheetName / sheetFile props
        hs.sheetName = Property(key="Sheetname", value=child_name)
        hs.sheetName.position = Position(
            str(100 + i*(sheet_width+spacing) + sheet_width/2), "45", "0"
        )
        
        hs.fileName = Property(key="Sheetfile", value=f"{child_name}.kicad_sch")
        hs.fileName.position = Position(
            str(100 + i*(sheet_width+spacing) + sheet_width/2), "48", "0"
        )
        
        # Append to the parent's schematic
        sch_obj.sheets.append(hs)
        
        # Recursively generate the child's schematic
        generate_subcircuit_schematic(child_path, hierarchy_dict, circuit, project_dir, valid_paths)
    
    # Now save the updated schematic with child references
    sch_obj.to_file(out_sch_path)


###############################################################################
# Main Entry: gen_schematic
###############################################################################

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

    Steps:
      1) Copies a blank KiCad project template into <filepath>/<project_name>.
      2) Reads circuit.group_name_cntr => subcircuit paths => build hierarchy.
      3) Recursively generates .kicad_sch for each subcircuit (parent->children).
      4) Renames the first root subcircuit's .kicad_sch => <project_name>.kicad_sch.
      5) Updates .kicad_pro, .kicad_pcb, etc. with that name.

    :param circuit:        The SKiDL Circuit object with parts & subcircuits
    :param filepath:       Output directory for the project folder
    :param top_name:       A default name for the script or top-level (unused here)
    :param project_name:   The user-provided project folder (and top schematic) name
    :param title:          Title block text (not heavily used here)
    :param flatness:       Not used in hierarchical approach
    :param retries:        Not used in this example
    :param options:        Catch-all for additional arguments
    """
    debug_print("GENSCM", f"Generating project '{project_name}' in '{filepath}'")
    
    # -------------------------------------------------------------------------
    # Step 1) Copy a blank KiCad project template into project_dir
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
    # Step 2) Build the subcircuit hierarchy from circuit.group_name_cntr
    # -------------------------------------------------------------------------
    subcircuit_paths = list(circuit.group_name_cntr.keys())
    debug_print("HIERARCHY", "All subcircuit paths:", subcircuit_paths)
    hierarchy_dict = build_subcircuit_hierarchy(subcircuit_paths)
    
    # Find the root subcircuit(s): any node with parent == None
    root_nodes = [p for p, data in hierarchy_dict.items() if data['parent'] is None]
    debug_print("HIERARCHY", f"Root subcircuits: {root_nodes}")
    
    if not root_nodes:
        raise RuntimeError("No top-level subcircuit found. (No root in hierarchy.)")
    
    # -------------------------------------------------------------------------
    # Step 3) Recursively generate each root subcircuit and its children
    # -------------------------------------------------------------------------
    for i, root_path in enumerate(root_nodes):
        generate_subcircuit_schematic(
            full_path=root_path,
            hierarchy_dict=hierarchy_dict,
            circuit=circuit,
            project_dir=project_dir,
            valid_paths=subcircuit_paths
        )

    # -------------------------------------------------------------------------
    # Step 4) Optionally rename the *first* root subcircuit to <project_name>.kicad_sch
    # -------------------------------------------------------------------------
    main_sch_path = os.path.join(project_dir, f"{project_name}.kicad_sch")
    renamed = False
    
    for i, root_path in enumerate(root_nodes):
        root_name = hierarchy_dict[root_path]['name']
        old_path = os.path.join(project_dir, f"{root_name}.kicad_sch")
        
        if i == 0:  # Rename only the first root
            if os.path.exists(old_path):
                os.rename(old_path, main_sch_path)
                debug_print("GENSCM", f"Renamed root subckt {root_name} -> {project_name}.kicad_sch")
                renamed = True
        else:
            # Optionally embed references from the newly renamed main to each additional root
            pass
    
    # If we never renamed anything, create a blank main if desired:
    if not renamed:
        main_sch = Schematic.create_new()
        main_sch.to_file(main_sch_path)

    # -------------------------------------------------------------------------
    # Step 5) Update the .kicad_pro, .kicad_pcb, etc. to use <project_name> naming
    # -------------------------------------------------------------------------
    try:
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

        # If .kicad_pro is JSON-based (KiCad 6/7), update meta + sheets
        project_path = os.path.join(project_dir, f"{project_name}.kicad_pro")
        if os.path.exists(project_path):
            import json
            with open(project_path, 'r') as f:
                project_config = json.load(f)

            # Update meta filename
            project_config['meta']['filename'] = f"{project_name}.kicad_pro"
            
            # Minimal approach: set root sheet to <project_name>.kicad_sch
            project_config['sheets'] = [
                {
                    "path": f"{project_name}.kicad_sch",
                    "sheet_name": "",
                    "id": str(uuid.uuid4())
                }
            ]
            # If multiple roots or nested subcircuits, KiCad auto-discovers them 
            # from hierarchical sheets. No need to list them all.

            with open(project_path, 'w') as f:
                json.dump(project_config, f, indent=2)
            active_logger.info(f"Updated project configuration in {project_path}")
    
    except Exception as e:
        active_logger.error(f"Error updating project files: {str(e)}")
        raise
