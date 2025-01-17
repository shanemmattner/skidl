"""KiCad schematic file writer module.

This module provides functionality to generate KiCad schematic (.kicad_sch) files.
It handles the KiCad file format and delegates component placement to specialized modules.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import uuid
import datetime
import os
from .kicad_symbol_lib import KicadSymbolLib
from .component_placement import (
    ComponentPlacer,
    WireRouter,
    WireSegment
)


@dataclass
class SchematicSymbol:
    """Represents a symbol to be placed in the schematic."""
    lib_id: str
    reference: str
    value: str
    position: tuple[float, float] = (63.5, 63.5)
    rotation: float = 0
    unit: int = 1
    in_bom: bool = True
    property_positions: Dict[str, tuple[float, float]] = None
    on_board: bool = True
    uuid: Optional[str] = None
    pin_numbers_visible: bool = True
    pin_names_visible: bool = True
    footprint: Optional[str] = None

    def __post_init__(self):
        if self.property_positions is None:
            self.property_positions = {}


class KicadSchematicWriter:
    """Generator for KiCad schematic files."""
    
    def __init__(self, kicad_lib_path: Optional[str] = None):
        """Initialize the KiCad schematic writer."""
        self.symbols: List[SchematicSymbol] = []
        self.version = "20231120"
        self.generator = "eeschema"
        self.generator_version = "8.0"
        self.paper_size = "A4"
        self.uuid = str(uuid.uuid4())
        
        # Set up KiCad library path
        if kicad_lib_path is None:
            if os.name == 'posix':
                if os.path.exists("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"):
                    self.kicad_lib_path = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
                else:
                    self.kicad_lib_path = "/usr/share/kicad/library"
            elif os.name == 'nt':
                self.kicad_lib_path = r"C:\Program Files\KiCad\share\kicad\library"
        else:
            self.kicad_lib_path = kicad_lib_path
            
        self.required_symbols: Set[str] = set()
        self.symbol_defs: Dict[str, str] = {}

    def _find_library_file(self, library_name: str) -> Optional[str]:
        """Find the .kicad_sym file for a given library."""
        lib_file = os.path.join(self.kicad_lib_path, f"{library_name}.kicad_sym")
        if os.path.exists(lib_file):
            return lib_file
            
        # Try case-insensitive search as fallback
        for filename in os.listdir(self.kicad_lib_path):
            if filename.lower() == f"{library_name.lower()}.kicad_sym":
                return os.path.join(self.kicad_lib_path, filename)
                
        return None

    def _extract_symbol_def(self, lib_file: str, lib_id: str) -> Optional[str]:
        """Extract a symbol definition from a library file."""
        try:
            library_name, symbol_name = lib_id.split(':')
            
            with open(lib_file, 'r') as f:
                content = f.read()

            lines = content.split('\n')
            symbol_lines = []
            in_symbol = False
            bracket_count = 0
            
            for line in lines:
                line = line.rstrip()
                
                # Check for symbol start - look for the bare symbol name
                if f'(symbol "{symbol_name}"' in line:
                    # Replace only the main symbol name, not unit references
                    line = line.replace(f'"{symbol_name}"', f'"{lib_id}"', 1)
                    in_symbol = True
                    bracket_count = line.count('(') - line.count(')')
                    symbol_lines = [line]
                    continue
                
                if in_symbol:
                    # DO NOT modify internal unit references
                    symbol_lines.append(line)
                    bracket_count += line.count('(') - line.count(')')
                    
                    if bracket_count == 0:
                        return '\n'.join(symbol_lines)
        
            return None
            
        except Exception as e:
            print(f"Error extracting symbol {lib_id}: {e}")
            return None

    def _load_symbol_definition(self, lib_id: str) -> Optional[str]:
        """Load a symbol definition from library, with caching."""
        if lib_id in self.symbol_defs:
            return self.symbol_defs[lib_id]
            
        try:
            library_name, symbol_name = lib_id.split(':')
            lib_file = self._find_library_file(library_name)
            
            if not lib_file:
                print(f"Could not find library file for {library_name}")
                return None
                
            symbol_def = self._extract_symbol_def(lib_file, lib_id)
            if symbol_def:
                self.symbol_defs[lib_id] = symbol_def
                return symbol_def
                
        except Exception as e:
            print(f"Error loading symbol {lib_id}: {e}")
            return None

    def _generate_lib_symbols(self) -> str:
        """Generate library symbols section."""
        content = "\t(lib_symbols\n"
        
        for lib_id in sorted(self.required_symbols):
            symbol_def = self._load_symbol_definition(lib_id)
            if symbol_def:
                # Indent the definition with tabs
                indented_def = '\n'.join(f"\t\t{line}" for line in symbol_def.split('\n'))
                content += indented_def + '\n'
                
        content += "\t)\n"
        return content
    
    def _generate_symbol_instance(self, symbol: SchematicSymbol) -> str:
        """Generate a symbol instance."""
        # Determine whether the reference should be hidden
        hide_reference = "yes" if symbol.reference.startswith("#PWR") else "no"
        return f'''    (symbol
            (lib_id "{symbol.lib_id}")
            (at {symbol.position[0]} {symbol.position[1]} {symbol.rotation})
            (unit {symbol.unit})
            (exclude_from_sim no)
            (in_bom yes)
            (on_board yes)
            (dnp no)
            (fields_autoplaced yes)
            (uuid "{str(uuid.uuid4())}")
            (property "Reference" "{symbol.reference}"
                (at {symbol.position[0] + 2.54} {symbol.position[1] - 1.27} 0)
                (effects
                    (font 
                        (size 1.27 1.27)
                    )
                    (justify left)
                    (hide {hide_reference})
                )
            )
            (property "Value" "{symbol.value}"
                (at {symbol.position[0] + 2.54} {symbol.position[1] + 1.27} 0)
                (effects
                    (font
                        (size 1.27 1.27)
                    )
                    (justify left)
                )
            )
            (property "Footprint" "{symbol.footprint or ''}"
                (at {symbol.position[0]} {symbol.position[1]} 0)
                (effects
                    (font
                        (size 1.27 1.27)
                    )
                    (hide yes)
                )
            )
            (property "Datasheet" "~"
                (at {symbol.position[0]} {symbol.position[1]} 0)
                (effects
                    (font
                        (size 1.27 1.27)
                    )
                    (hide yes)
                )
            )
        )'''

    def add_symbol(self, symbol: SchematicSymbol) -> None:
        """Add a symbol to the schematic."""
        if symbol.uuid is None:
            symbol.uuid = str(uuid.uuid4())
        self.symbols.append(symbol)
        self.required_symbols.add(symbol.lib_id)

    def _generate_wire(self, segment: WireSegment) -> str:
        """Generate a wire element for the schematic."""
        return f'''    (wire
            (pts
                (xy {segment.start[0]} {segment.start[1]}) (xy {segment.end[0]} {segment.end[1]})
            )
            (stroke
                (width 0)
                (type default)
            )
            (uuid "{str(uuid.uuid4())}")
        )'''

    def generate(self, filepath: str) -> bool:
        """Generate the KiCad schematic file."""
        try:
            content = f'''(kicad_sch
            (version {self.version})
            (generator "eeschema")
            (generator_version "8.0")
            (uuid "{str(uuid.uuid4())}")
            (paper "A4")
            (title_block
                (date "{datetime.datetime.now().strftime('%Y-%m-%d')}")
            )'''
            
            # Add library symbols
            content += self._generate_lib_symbols()
            
            # Add placed symbols
            for symbol in self.symbols:
                content += self._generate_symbol_instance(symbol)

            # Add wires for nets
            for segment in getattr(self, 'wire_segments', []):
                content += self._generate_wire(segment)
            
            # Add sheet instances
            content += '''    (sheet_instances
                (path "/"
                    (page "1")
                )
            )
        )'''

            with open(filepath, 'w') as f:
                f.write(content)
            return True

        except Exception as e:
            print(f"Error generating schematic file: {e}")
            return False


def generate_kicad_schematic(circuit, output_file="output.kicad_sch") -> bool:
    """
    Generate a KiCad schematic from a Circuit object.
    
    Args:
        circuit: Circuit object containing components and nets
        output_file: Path to output .kicad_sch file
        
    Returns:
        bool: True if schematic generation was successful
    """
    writer = KicadSchematicWriter()
    
    # Create component placer and get optimal positions
    placer = ComponentPlacer()
    component_positions = placer.place_components(circuit)
    
    # Add symbols to schematic at calculated positions
    for comp in circuit.components:
        x, y, rotation = component_positions[comp.ref]
        
        # Create SchematicSymbol with calculated position
        symbol = SchematicSymbol(
            lib_id=f"{comp.library}:{comp.name}",
            reference=comp.ref,
            value=comp.parameters.get("Value", comp.name),
            position=(x, y),
            rotation=rotation,
            footprint=comp.metadata.footprint if comp.metadata.footprint else ""
        )
        
        # Add symbol to writer
        writer.add_symbol(symbol)

    # Create wire router and route all nets
    router = WireRouter()
    wire_segments = []
    for net in circuit.get_nets():
        segments = router.route_net(net, placer.placement_nodes)
        wire_segments.extend(segments)
    
    # Add wire segments to writer
    writer.wire_segments = wire_segments
    
    # Generate the schematic file
    return writer.generate(output_file)
