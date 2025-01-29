
"""
symbol_definitions.py

Data classes for representing parsed KiCad library symbols (pins, shapes, etc.).
Used to store structured data before flattening inheritance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PinDefinition:
    number: str
    # Child symbol might override "number"
    name: str = ""
    # Additional attributes like pin type, pin shape, orientation, length...
    # For brevity, we only store essential fields:
    pin_type: Optional[str] = None
    pin_shape: Optional[str] = None

@dataclass
class ShapeDefinition:
    shape_type: str  # e.g. "circle", "rectangle", "polyline", "arc", "pin"
    # For brevity, store raw lines or a more structured geometry object
    raw_s_expression: List[str] = field(default_factory=list)

@dataclass
class SymbolDefinition:
    name: str
    extends: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    pins: Dict[str, PinDefinition] = field(default_factory=dict)
    shapes: List[ShapeDefinition] = field(default_factory=list)

    # Once flattened, store an "is_flattened" or store the final s-expression
    flattened_s_expr: Optional[str] = None
    is_flattened: bool = False
