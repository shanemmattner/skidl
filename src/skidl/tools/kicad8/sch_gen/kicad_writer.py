"""
kicad_writer.py

A robust generator for .kicad_sch schematics using SKiDL's Part objects.
"""

import datetime
import uuid
import re
from typing import List, Dict, Tuple
import os

from kiutils.items.schitems import HierarchicalSheet
from kiutils.items.common import Position, Property

from skidl import Part
from skidl.tools.kicad8.lib import load_sch_lib, parse_lib_part


def escape_property_value(value: str) -> str:
    """Escape a property value for use in KiCad s-expressions"""
    if not isinstance(value, str):
        value = str(value)
    # Replace newlines with spaces
    value = value.replace('\n', ' ')
    # Escape quotes
    value = value.replace('"', '\\"')
    # Remove any control characters
    value = ''.join(char for char in value if ord(char) >= 32 or char == '\\"')
    return value


def get_pin_type(pin) -> str:
    """Convert SKiDL pin type to KiCad pin type"""
    pin_type_map = {
        'INPUT': 'input',
        'OUTPUT': 'output',
        'BIDIR': 'bidirectional',
        'TRISTATE': 'tri_state',
        'PASSIVE': 'passive',
        'UNSPEC': 'unspecified',
        'PWRIN': 'power_in',
        'PWROUT': 'power_out',
        'OPENCOLL': 'open_collector',
        'OPENEMIT': 'open_emitter',
        'NOCONNECT': 'no_connect'
    }
    return pin_type_map.get(pin.func, 'passive')


class SchematicSymbolInstance:
    """
    Represents a single placed symbol in the schematic. The symbol is identified by:
      - lib_id: e.g. "Device:R"
      - reference: e.g. "R1"
      - value: e.g. "10k"
      - x, y: coordinates in mm in the schematic
    """
    def __init__(self, part: Part, position: Tuple[float, float], rotation: int = 0):
        """Initialize from a SKiDL Part object"""
        self.part = part  # Store reference to original part
        self.lib_id = f"{part.lib.filename}:{part.name}"
        self.reference = part.ref
        self.value = part.value
        self.x = position[0]
        self.y = position[1]
        self.uuid = str(uuid.uuid4())
        self.rotation = rotation
        self.footprint = getattr(part, 'footprint', '')
        self.description = getattr(part, 'description', '')
        self.datasheet = getattr(part, 'datasheet', '~')
        self.hierarchical_path = getattr(part, 'hierarchy', '/')
        
        # Get additional properties
        self.properties = {}
        for key, value in vars(part).items():
            if not key.startswith('_') and isinstance(value, str):
                self.properties[key] = value

    def __repr__(self):
        return (f"<SchematicSymbolInstance lib_id='{self.lib_id}' ref='{self.reference}' "
                f"value='{self.value}' x={self.x} y={self.y} uuid={self.uuid}>")


class KicadSchematicWriter:
    """
    Writes a .kicad_sch file with:
      1) Symbol definitions in lib_symbols section
      2) Symbol instance placements
      3) Hierarchical sheets
      4) Sheet instances block
    """
    def __init__(self, out_file: str):
        """
        out_file: path to the .kicad_sch that we want to create.
        """
        self.out_file = out_file
        self.symbol_instances: List[SchematicSymbolInstance] = []
        self.sheet_symbols: List[HierarchicalSheet] = []

        # Schematic metadata
        self.version = 20231120  # Version must be an integer for KiCad
        self.generator = "eeschema"
        self.generator_version = "8.0"
        self.paper_size = "A4"
        self.uuid = str(uuid.uuid4())

    def add_symbol_instance(self, instance: SchematicSymbolInstance):
        """Add a symbol instance to be placed in the final .kicad_sch."""
        self.symbol_instances.append(instance)

    def add_sheet_symbol(self, sheet: HierarchicalSheet):
        """Add a hierarchical sheet symbol to be placed in the final .kicad_sch."""
        self.sheet_symbols.append(sheet)

    def _collect_symbols(self) -> Dict[str, Part]:
        """Collect all unique symbols used in instances"""
        symbols = {}
        for inst in self.symbol_instances:
            if inst.lib_id not in symbols:
                # Ensure part is parsed
                if inst.part.part_defn:
                    parse_lib_part(inst.part, False)
                symbols[inst.lib_id] = inst.part
        return symbols

    def _write_symbol_definition(self, lines: List[str], lib_id: str, part: Part):
        """Write complete symbol definition from part"""
        lines.append(f'    (symbol "{lib_id}"')
        
        # Write standard attributes
        lines.append('      (pin_numbers hide)')
        lines.append('      (pin_names')
        lines.append('        (offset 0)')
        lines.append('      )')
        lines.append('      (exclude_from_sim no)')
        lines.append('      (in_bom yes)')
        lines.append('      (on_board yes)')

        # Write standard properties
        self._write_property(lines, "Reference", part.ref_prefix, at=(2.032, 0, 90))
        self._write_property(lines, "Value", part.name, at=(0, 0, 90))
        self._write_property(lines, "Footprint", part.footprint or "", at=(-1.778, 0, 90), hide=True)
        self._write_property(lines, "Datasheet", part.datasheet or "~", hide=True)
        self._write_property(lines, "Description", part.description or "", hide=True)

        # Write additional properties from part
        for key, value in vars(part).items():
            if not key.startswith('_') and isinstance(value, str) and key not in ['ref', 'value', 'footprint', 'datasheet', 'description']:
                self._write_property(lines, key, value, hide=True)

        # Write shapes from part's draw_cmds
        for unit, cmds in part.draw_cmds.items():
            lines.append(f'      (symbol "{part.name}_{unit}_1"')
            for cmd in cmds:
                if isinstance(cmd, list):
                    lines.append('        ' + self._format_draw_cmd(cmd))
            lines.append('      )')

        # Write pins
        for pin in part.pins:
            pin_type = get_pin_type(pin)
            lines.append(f'      (pin {pin_type} line')
            lines.append(f'        (at {pin.x} {pin.y} {pin.orientation})')
            lines.append(f'        (length {pin.length})')
            lines.append(f'        (name "{escape_property_value(pin.name)}"')
            lines.append('          (effects')
            lines.append('            (font')
            lines.append('              (size 1.27 1.27)')
            lines.append('            )')
            lines.append('          )')
            lines.append('        )')
            lines.append(f'        (number "{escape_property_value(pin.num)}"')
            lines.append('          (effects')
            lines.append('            (font')
            lines.append('              (size 1.27 1.27)')
            lines.append('            )')
            lines.append('          )')
            lines.append('        )')
            lines.append('      )')

        lines.append('    )')

    def _write_property(self, lines: List[str], key: str, value: str, at: Tuple[float, float, float] = (0, 0, 0), hide: bool = False):
        """Write a property with proper formatting"""
        escaped_value = escape_property_value(value)
        lines.append(f'      (property "{key}" "{escaped_value}"')
        lines.append(f'        (at {at[0]} {at[1]} {at[2]})')
        lines.append('        (effects')
        lines.append('          (font')
        lines.append('            (size 1.27 1.27)')
        lines.append('          )')
        if hide:
            lines.append('          (hide yes)')
        lines.append('        )')
        lines.append('      )')

    def _format_draw_cmd(self, cmd) -> str:
        """Format a drawing command as s-expression"""
        if not cmd:
            return ""
        cmd_type = cmd[0].value().lower()
        if cmd_type == "rectangle":
            return self._format_rectangle(cmd)
        elif cmd_type == "polyline":
            return self._format_polyline(cmd)
        elif cmd_type == "circle":
            return self._format_circle(cmd)
        elif cmd_type == "arc":
            return self._format_arc(cmd)
        return ""

    def _format_rectangle(self, cmd) -> str:
        """Format rectangle command"""
        # Default resistor dimensions
        start_x, start_y = -1.016, -2.54
        end_x, end_y = 1.016, 2.54

        # Try to extract coordinates from command
        try:
            if len(cmd) >= 3:
                if isinstance(cmd[1], list) and len(cmd[1]) >= 2:
                    # Handle both string/Symbol and numeric values
                    start_x = float(cmd[1][0].value() if hasattr(cmd[1][0], 'value') else cmd[1][0])
                    start_y = float(cmd[1][1].value() if hasattr(cmd[1][1], 'value') else cmd[1][1])
                if isinstance(cmd[2], list) and len(cmd[2]) >= 2:
                    end_x = float(cmd[2][0].value() if hasattr(cmd[2][0], 'value') else cmd[2][0])
                    end_y = float(cmd[2][1].value() if hasattr(cmd[2][1], 'value') else cmd[2][1])
        except (ValueError, AttributeError, IndexError):
            # If any conversion fails, use default dimensions
            pass

        return (f'(rectangle (start {start_x} {start_y}) '
                f'(end {end_x} {end_y}) '
                '(stroke (width 0.254) (type default)) '
                '(fill (type none)))')

    def _format_polyline(self, cmd) -> str:
        """Format polyline command"""
        points = []
        for point in cmd[1:]:
            if isinstance(point, list) and len(point) >= 2:
                points.append(f'(xy {point[0]} {point[1]})')
        return f'(polyline (pts {" ".join(points)}) (stroke (width 0.254) (type default)))'

    def _format_circle(self, cmd) -> str:
        """Format circle command"""
        center = cmd[1] if len(cmd) > 1 else [0, 0]
        radius = cmd[2] if len(cmd) > 2 else 1
        return (f'(circle (center {center[0]} {center[1]}) '
                f'(radius {radius}) '
                '(stroke (width 0.254) (type default)) '
                '(fill (type none)))')

    def _format_arc(self, cmd) -> str:
        """Format arc command"""
        start = cmd[1] if len(cmd) > 1 else [0, 0]
        mid = cmd[2] if len(cmd) > 2 else [1, 1]
        end = cmd[3] if len(cmd) > 3 else [2, 0]
        return (f'(arc (start {start[0]} {start[1]}) '
                f'(mid {mid[0]} {mid[1]}) '
                f'(end {end[0]} {end[1]}) '
                '(stroke (width 0.254) (type default)))')

    def _sheet_to_s_expression(self, sheet: HierarchicalSheet) -> str:
        """Convert a hierarchical sheet to KiCad s-expression format."""
        s = []
        s.append("(sheet")
        s.append(f"  (at {sheet.position.X} {sheet.position.Y})")
        s.append(f"  (size {sheet.width} {sheet.height})")
        s.append("  (fields_autoplaced yes)")
        s.append("  (stroke")
        s.append("    (width 0.1524)")
        s.append("    (type solid)")
        s.append("  )")
        s.append("  (fill")
        s.append("    (color 0 0 0 0.0000)")
        s.append("  )")
        s.append(f"  (uuid \"{str(uuid.uuid4())}\")")
        
        # Add sheet properties with proper positioning and effects
        s.append(f"  (property \"Sheetname\" \"{escape_property_value(sheet.sheetName.value)}\"")
        s.append(f"    (at {sheet.position.X} {float(sheet.position.Y) - 0.7116} 0)")
        s.append("    (effects")
        s.append("      (font")
        s.append("        (size 1.27 1.27)")
        s.append("      )")
        s.append("      (justify left bottom)")
        s.append("    )")
        s.append("  )")
        
        s.append(f"  (property \"Sheetfile\" \"{escape_property_value(sheet.fileName.value)}\"")
        s.append(f"    (at {sheet.position.X} {float(sheet.position.Y) + float(sheet.height) + 0.5846} 0)")
        s.append("    (effects")
        s.append("      (font")
        s.append("        (size 1.27 1.27)")
        s.append("      )")
        s.append("      (justify left top)")
        s.append("    )")
        s.append("  )")
        
        # Add instances block with proper project path
        s.append("  (instances")
        s.append("    (project \"testing_hierarchy\"")
        s.append(f"      (path \"{escape_property_value(sheet.hierarchical_path)}\"")
        s.append("        (page \"3\")")
        s.append("      )")
        s.append("    )")
        s.append("  )")
        
        s.append(")")
        return "\n".join(s)

    def generate(self) -> None:
        """
        Generate the .kicad_sch file:
          1) Write schematic header
          2) Write lib_symbols section with all used symbols
          3) Write symbol instances
          4) Write sheet instances
        """
        lines = []
        lines.append("(kicad_sch")
        lines.append(f"  (version {self.version})")
        lines.append(f"  (generator \"{self.generator}\")")
        lines.append(f"  (generator_version \"{self.generator_version}\")")
        lines.append(f"  (uuid \"{self.uuid}\")")
        lines.append(f"  (paper \"{self.paper_size}\")")

        # Title block with date
        lines.append("  (title_block")
        dt_str = datetime.datetime.now().strftime('%Y-%m-%d')
        lines.append(f"    (date \"{dt_str}\")")
        lines.append("  )")

        # Write lib_symbols section
        lines.append("  (lib_symbols")
        symbols = self._collect_symbols()
        for lib_id, part in symbols.items():
            self._write_symbol_definition(lines, lib_id, part)
        lines.append("  )")

        # Write symbol instances
        for inst in self.symbol_instances:
            inst_block = self._instance_to_s_expression(inst)
            for l in inst_block.splitlines():
                lines.append("  " + l)

        # Write hierarchical sheets
        for sheet in self.sheet_symbols:
            sheet_block = self._sheet_to_s_expression(sheet)
            for l in sheet_block.splitlines():
                lines.append("  " + l)

        # Write sheet instances block
        lines.append("  (sheet_instances")
        lines.append("    (path \"/\" (page \"1\"))")
        for sheet in self.sheet_symbols:
            sheet_id = str(uuid.uuid4())
            sheet_path = getattr(sheet, 'hierarchical_path', f"/{sheet.sheetName.value}")
            lines.append(f"    (path \"{escape_property_value(sheet_path)}\" (page \"{sheet_id}\"))")
        lines.append("  )")

        lines.append(")")

        # Write to file
        with open(self.out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _instance_to_s_expression(self, inst: SchematicSymbolInstance) -> str:
        """
        Create the schematic's (symbol) instance referencing the lib_id.
        For example:
            (symbol
              (lib_id "Device:R")
              (at 50.8 63.5 0)
              ...
            )
        """
        s = []
        s.append("(symbol")
        s.append(f"  (lib_id \"{inst.lib_id}\")")
        s.append(f"  (at {inst.x:.2f} {inst.y:.2f} {inst.rotation})")
        s.append("  (unit 1)")
        s.append("  (exclude_from_sim no)")
        s.append("  (in_bom yes)")
        s.append("  (on_board yes)")
        s.append("  (dnp no)")
        s.append("  (fields_autoplaced yes)")
        s.append(f"  (uuid \"{inst.uuid}\")")

        # Write all properties
        self._write_property(s, "Reference", inst.reference, at=(inst.x+2.54, inst.y-1.2701, 0))
        self._write_property(s, "Value", inst.value, at=(inst.x+2.54, inst.y+1.2699, 0))
        
        if inst.footprint:
            self._write_property(s, "Footprint", inst.footprint, at=(inst.x-1.778, inst.y, 90), hide=True)
        
        self._write_property(s, "Datasheet", inst.datasheet, hide=True)
        self._write_property(s, "Description", inst.description, hide=True)

        # Write additional properties
        for key, value in inst.properties.items():
            if key not in ['ref', 'value', 'footprint', 'datasheet', 'description']:
                self._write_property(s, key, value, hide=True)

        # Add instances block
        s.append("  (instances")
        s.append("    (project \"testing_hierarchy\"")
        s.append(f"      (path \"{escape_property_value(inst.hierarchical_path)}\"")
        s.append(f"        (reference \"{inst.reference}\")")
        s.append("        (unit 1)")
        s.append("      )")
        s.append("    )")
        s.append("  )")

        s.append(")")
        return "\n".join(s)
