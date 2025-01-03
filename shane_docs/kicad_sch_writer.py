"""KiCad schematic file writer module.

This module provides functionality to generate KiCad schematic (.kicad_sch) files.
It can create new schematics or modify existing ones with components, nets, and other elements.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Set
import uuid
import datetime
import os
from .kicad_symbol_lib import KicadSymbolLib


@dataclass
class SchematicNet:
    """Represents a net connection in the schematic.
    
    Handles both wires and buses with proper s-expression formatting.
    """
    name: str  # Net name (can be empty for unnamed wires)
    points: List[tuple[float, float]]  # List of (x,y) coordinates
    connected_pins: List[tuple[str, str]]  # List of (component_ref, pin_number)
    width: float = 0  # Line width (0 = default width)
    type: str = "default"  # Line type: default, bus
    uuid: Optional[str] = None  # UUID for the net instance
    style: str = "solid"  # Line style: solid, dash, dot, dashdot
    color: Optional[tuple[int, int, int, int]] = None  # RGBA color


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
        self.symbols = []
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

    def place_component(self, symbol: SchematicSymbol, x: float, y: float, rotation: float = 0) -> None:
        """Place a component on the schematic at the specified position and rotation."""
        if symbol.uuid is None:
            symbol.uuid = str(uuid.uuid4())
        symbol.position = (x, y)
        symbol.rotation = rotation
        self.symbols.append(symbol)
        self.required_symbols.add(symbol.lib_id)

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
        


from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
import math

@dataclass
class PlacementNode:
    """Represents a component's placement information"""
    component: 'Component'
    x: float = 0
    y: float = 0
    rotation: float = 0
    placed: bool = False
    connected_components: Set['Component'] = None
    
    def __post_init__(self):
        if self.connected_components is None:
            self.connected_components = set()

class ComponentPlacer:
    """Handles intelligent placement of components in a schematic"""
    
    def __init__(self, base_x: float = 50.0, base_y: float = 50.0):
        self.base_x = base_x
        self.base_y = base_y
        self.spacing_x = 30.0  # Horizontal spacing between components
        self.spacing_y = 25.0  # Vertical spacing between components
        self.placement_nodes: Dict[str, PlacementNode] = {}
        
    def analyze_connectivity(self, circuit: 'Circuit') -> None:
        """Build a connectivity graph from the circuit nets"""
        # Initialize placement nodes for each component
        self.placement_nodes = {
            comp.ref: PlacementNode(component=comp)
            for comp in circuit.components
        }
        
        # Analyze nets to build connectivity information
        for net in circuit.get_nets():  # Using get_nets() method instead of nets attribute
            connected_components = set()
            # Get all components connected by this net through their pins
            for pin in net.pins:  # Access pins directly from the Net object
                connected_components.add(pin.parent)
            
            # Update connectivity information for each component
            for comp in connected_components:
                node = self.placement_nodes[comp.ref]
                node.connected_components.update(
                    c for c in connected_components if c != comp
                )
    
    def _place_power_components(self) -> None:
        """Place power-related components (VCC, GND) at logical positions"""
        for ref, node in self.placement_nodes.items():
            if node.component.library == "power":
                if "+V" in node.component.name or "VCC" in node.component.name:
                    # Place voltage sources at the top
                    node.x = self.base_x
                    node.y = self.base_y
                    node.placed = True
                elif "GND" in node.component.name:
                    # Place ground at the bottom
                    node.x = self.base_x
                    node.y = self.base_y + self.spacing_y * 3
                    node.placed = True
    
    def _calculate_component_position(self, 
                                   node: PlacementNode, 
                                   placed_neighbors: List[PlacementNode]) -> Tuple[float, float, float]:
        """Calculate optimal position for a component based on its placed neighbors"""
        if not placed_neighbors:
            # If no placed neighbors, place relative to base position
            return self.base_x + self.spacing_x, self.base_y, 0
            
        # Calculate average position of connected components
        avg_x = sum(n.x for n in placed_neighbors) / len(placed_neighbors)
        avg_y = sum(n.y for n in placed_neighbors) / len(placed_neighbors)
        
        # Find a suitable position near the average that doesn't overlap
        angle = 0
        radius = self.spacing_x
        while angle < 2 * math.pi:
            x = avg_x + radius * math.cos(angle)
            y = avg_y + radius * math.sin(angle)
            
            # Check if position is clear
            position_clear = True
            for other_node in self.placement_nodes.values():
                if other_node.placed:
                    dist = math.sqrt((x - other_node.x)**2 + (y - other_node.y)**2)
                    if dist < self.spacing_x * 0.8:  # Allow some overlap margin
                        position_clear = False
                        break
            
            if position_clear:
                # Calculate rotation based on most important connection
                main_neighbor = placed_neighbors[0]
                rotation = math.degrees(math.atan2(y - main_neighbor.y, x - main_neighbor.x))
                # Snap rotation to 90-degree increments
                rotation = round(rotation / 90) * 90
                return x, y, rotation
                
            angle += math.pi / 4
            if angle >= 2 * math.pi:
                radius += self.spacing_x
                angle = 0
        
        # Fallback if no clear position found
        return avg_x + self.spacing_x * 2, avg_y, 0
    
    def place_components(self, circuit: 'Circuit') -> Dict[str, Tuple[float, float, float]]:
        """Place all components in the circuit and return their positions"""
        self.analyze_connectivity(circuit)
        self._place_power_components()
        
        # Place remaining components based on connectivity
        while True:
            # Find unplaced component with most placed neighbors
            best_score = -1
            next_to_place = None
            
            for ref, node in self.placement_nodes.items():
                if node.placed:
                    continue
                    
                # Count placed neighbors
                placed_neighbors = len([
                    c for c in node.connected_components
                    if self.placement_nodes[c.ref].placed
                ])
                
                if placed_neighbors > best_score:
                    best_score = placed_neighbors
                    next_to_place = node
            
            if next_to_place is None:
                # Place any remaining unplaced components
                for node in self.placement_nodes.values():
                    if not node.placed:
                        x = self.base_x + self.spacing_x * 2
                        y = self.base_y + self.spacing_y * 2
                        node.x, node.y, node.rotation = self._calculate_component_position(node, [])
                        node.placed = True
                break
                
            # Get placed neighbors for positioning
            placed_neighbors = [
                self.placement_nodes[c.ref]
                for c in next_to_place.connected_components
                if self.placement_nodes[c.ref].placed
            ]
            
            # Calculate position based on placed neighbors
            next_to_place.x, next_to_place.y, next_to_place.rotation = \
                self._calculate_component_position(next_to_place, placed_neighbors)
            next_to_place.placed = True
        
        # Return final component positions
        return {
            ref: (node.x, node.y, node.rotation)
            for ref, node in self.placement_nodes.items()
        }
    
def generate_kicad_schematic(circuit, output_file="output.kicad_sch") -> bool:
    """
    Generate a KiCad schematic from a Circuit object with intelligent component placement.
    Components are placed based on their connections to minimize wire crossings.
    
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
        
    # Generate the schematic file
    return writer.generate(output_file)