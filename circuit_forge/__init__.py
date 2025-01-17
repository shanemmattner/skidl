"""
Main package for circuit_forge.

Provides top-level tools for analyzing circuits, managing components,
and integrating with KiCad. This __init__ file re-exports common
classes, functions, and constants for convenient imports elsewhere.
"""

# Import from circuit_analysis
from .circuit_analysis import (
    ValidationSeverity,
    LLMProvider,
    ClaudeProvider,
    ValidationRule,
    ValidationResult,
    CircuitHash,
    AnalysisConfig,
    ValidationManager,
    CircuitChangeDetector,
    CircuitAnalyzer,
)

# Import from circuit_manager
from .circuit_manager import (
    CircuitType,
    ComponentMetadata,
    CircuitMetadata,
    CircuitElement,
    Net,
    Pin,
    CircuitValidator,
    Component,
    SubCircuit,
    Circuit,
)

# Import from footprint_parser
from .footprint_parser import parse_kicad_footprint

# Import from kicad_sch_reader
from .kicad_sch_reader import KicadSchematicReader

# Import from kicad_sch_writer
from .kicad_sch_writer import (
    KicadSchematicWriter,
    SchematicSymbol,
    generate_kicad_schematic,
)

# Import from kicad_symbol_lib
from .kicad_symbol_lib import (
    PinElectricalType,
    PinGraphicalStyle,
    PinInfo,
    SymbolProperties,
    SymbolInfo,
    KicadSymbolLib,
)

# Import from schematic_scraper
from .schematic_scraper import parse_kicad_symbols


__all__ = [
    # circuit_analysis
    "ValidationSeverity",
    "LLMProvider",
    "ClaudeProvider",
    "ValidationRule",
    "ValidationResult",
    "CircuitHash",
    "AnalysisConfig",
    "ValidationManager",
    "CircuitChangeDetector",
    "CircuitAnalyzer",
    
    # circuit_manager
    "CircuitType",
    "ComponentMetadata",
    "CircuitMetadata",
    "CircuitElement",
    "Net",
    "Pin",
    "CircuitValidator",
    "Component",
    "SubCircuit",
    "Circuit",
    
    # footprint_parser
    "parse_kicad_footprint",
    
    # kicad_sch_reader
    "KicadSchematicReader",
    
    # kicad_sch_writer
    "KicadSchematicWriter",
    "SchematicSymbol",
    "generate_kicad_schematic",
    
    # kicad_symbol_lib
    "PinElectricalType",
    "PinGraphicalStyle",
    "PinInfo",
    "SymbolProperties",
    "SymbolInfo",
    "KicadSymbolLib",
    
    # schematic_scraper
    "parse_kicad_symbols",
]
