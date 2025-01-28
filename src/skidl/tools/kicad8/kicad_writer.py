"""KiCad schematic writer module.

This module provides functionality to write KiCad schematic files by generating
the appropriate S-expressions. It handles library symbol loading and component placement.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import uuid
import datetime
import os

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
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

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
        """Extract a complete symbol definition from a library file.
        
        Args:
            lib_file: Path to the .kicad_sym library file
            lib_id: Library identifier in format "library:symbol"
            
        Returns:
            Complete symbol definition as a string, or None if not found
        """
        try:
            library_name, symbol_name = lib_id.split(':')
            
            with open(lib_file, 'r') as f:
                content = f.read()

            lines = content.split('\n')
            symbol_lines = []
            in_symbol = False
            bracket_count = 0
            
            # Find main symbol definition start
            for i, line in enumerate(lines):
                line = line.rstrip()
                
                # Look for main symbol definition
                if f'(symbol "{symbol_name}"' in line or f'(symbol "{lib_id}"' in line:
                    in_symbol = True
                    bracket_count = line.count('(') - line.count(')')
                    # Replace only the main symbol name, not unit references
                    if f'(symbol "{symbol_name}"' in line:
                        line = line.replace(f'"{symbol_name}"', f'"{lib_id}"', 1)
                    symbol_lines = [line]
                    continue
                    
                if in_symbol:
                    # Handle nested symbol definitions (_0_1, _1_1 etc)
                    if f'(symbol "{symbol_name}_' in line:
                        # Don't replace the unit number parts of the symbol name
                        symbol_lines.append(line)
                    else:
                        symbol_lines.append(line)
                        
                    bracket_count += line.count('(') - line.count(')')
                    
                    if bracket_count == 0:
                        # Found complete symbol definition including all units
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
            (uuid "{symbol.uuid}")
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

    def generate(self, filepath: str) -> bool:
        """Generate the KiCad schematic file."""
        try:
            content = f'''(kicad_sch
            (version {self.version})
            (generator "{self.generator}")
            (generator_version "{self.generator_version}")
            (uuid "{str(uuid.uuid4())}")
            (paper "{self.paper_size}")
            (title_block
                (date "{datetime.datetime.now().strftime('%Y-%m-%d')}")
            )'''
            
            # Add library symbols
            content += self._generate_lib_symbols()
            
            # Add placed symbols
            for symbol in self.symbols:
                content += self._generate_symbol_instance(symbol)
            
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