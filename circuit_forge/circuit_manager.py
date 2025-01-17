# circuit_manager.py

from typing import Dict, List, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
from datetime import datetime

from .kicad_symbol_lib import KicadSymbolLib

class CircuitType(Enum):
    """Defines different types of circuits for organization and validation"""
    POWER = "power"
    DIGITAL = "digital"
    ANALOG = "analog"
    MIXED = "mixed"
    RF = "rf"
    INTERFACE = "interface"

@dataclass
class ComponentMetadata:
    """Structured metadata for components"""
    description: str = ""
    footprint: str = ""
    datasheet: str = ""
    keywords: List[str] = None
    max_voltage: str = ""
    max_current: str = ""
    temperature_range: str = ""

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
            
    def update(self, metadata_dict: Dict[str, Any]) -> None:
        """Update metadata fields from a dictionary"""
        for key, value in metadata_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

@dataclass
class CircuitMetadata:
    """Metadata for circuits and subcircuits"""
    name: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    circuit_type: CircuitType = CircuitType.MIXED
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

class CircuitElement(ABC):
    """Base class for circuit elements like nets and pins"""
    @abstractmethod
    def connect(self, other: 'CircuitElement') -> bool:
        """Connect this element to another"""
        pass

    @abstractmethod
    def disconnect(self, other: 'CircuitElement') -> bool:
        """Disconnect this element from another"""
        pass

class Net(CircuitElement):
    """Represents an electrical connection between component pins."""

    auto_increment_id = 1  # Class variable for generating unique net names
    
    @classmethod
    def reset_counter(cls):
        """Reset the auto-increment counter - useful for testing or new projects"""
        cls.auto_increment_id = 1

    def __init__(self, name: Optional[str] = None, net_type: str = "signal"):
        self.name = name or f"N$auto_{Net.auto_increment_id}"
        if not name:
            Net.auto_increment_id += 1
        self.pins: List['Pin'] = []
        self.metadata: Dict[str, Any] = {}
        self.net_type = net_type  # e.g., "power", "signal", "ground"
        self._frozen = False  # For critical nets that shouldn't be modified

    def freeze(self):
        """Prevent further modifications to the net"""
        self._frozen = True

    def unfreeze(self):
        """Allow modifications to the net"""
        self._frozen = False

    def connect(self, other: Union['Pin', 'Net']) -> bool:
        if self._frozen:
            raise ValueError(f"Cannot modify frozen net {self.name}")
        
        if isinstance(other, Pin):
            if other not in self.pins:
                self.pins.append(other)
                other.net = self
                return True
        elif isinstance(other, Net):
            if other is self:
                return False
            for pin in other.pins:
                self.connect(pin)
            other.name = self.name
            return True
        return False

    def disconnect(self, other: Union['Pin', 'Net']) -> bool:
        if self._frozen:
            raise ValueError(f"Cannot modify frozen net {self.name}")
            
        if isinstance(other, Pin):
            if other in self.pins:
                self.pins.remove(other)
                other.net = None
                return True
        elif isinstance(other, Net):
            if other is self:
                return False
            for pin in list(other.pins):  # Create copy of list to modify during iteration
                self.disconnect(pin)
            return True
        return False

    def __iadd__(self, other: Union['Pin', 'Net', List[Union['Pin', 'Net']]]) -> 'Net':
        if isinstance(other, (Pin, Net)):
            self.connect(other)
        elif isinstance(other, (list, tuple)):
            for item in other:
                self.connect(item)
        else:
            raise TypeError(f"Unsupported operand type(s) for +=: 'Net' and '{type(other).__name__}'")
        return self

    def __repr__(self):
        return f"Net('{self.name}', type='{self.net_type}', pins={len(self.pins)})"

class Pin(CircuitElement):
    """Represents a single pin on a component."""

    def __init__(self, 
                 number: str, 
                 name: str, 
                 parent: 'Component',
                 electrical_type: str = 'passive',
                 graphic_style: str = 'line',
                 direction: str = 'bidirectional'):
        self.number = number
        self.name = name
        self.parent = parent
        self.net: Optional[Net] = None
        self.electrical_type = electrical_type
        self.graphic_style = graphic_style
        self.direction = direction
        self.metadata: Dict[str, Any] = {}

    def connect(self, other: Union['Pin', Net]) -> bool:
        if isinstance(other, Pin):
            if not self.net and not other.net:
                new_net = Net()
                new_net.connect(self)
                new_net.connect(other)
                return True
            elif self.net and not other.net:
                return self.net.connect(other)
            elif not self.net and other.net:
                return other.net.connect(self)
            elif self.net != other.net:
                return self.net.connect(other.net)
        elif isinstance(other, Net):
            return other.connect(self)
        return False

    def disconnect(self, other: Union['Pin', Net]) -> bool:
        if isinstance(other, Pin):
            if self.net and self.net == other.net:
                return self.net.disconnect(other)
        elif isinstance(other, Net):
            return other.disconnect(self)
        return False

    def __and__(self, other: Union['Pin', Net]) -> Optional[Net]:
        self.connect(other)
        return self.net or other.net if isinstance(other, Pin) else other

    def __repr__(self):
        return f"Pin('{self.number}:{self.name}', type='{self.electrical_type}')"

    def __str__(self):
        return f"{self.parent.ref}.{self.name}"

class CircuitValidator:
    """Enhanced circuit validation system with configurable rules.
    
    The CircuitValidator provides a comprehensive validation framework for electronic circuits,
    organized into different categories like power, signals, components, etc. Each category
    contains specific validation rules that can be enabled or disabled as needed.
    """
    
    def __init__(self):
        """Initialize the validator with categorized validation rules."""
        self.validation_rules: Dict[str, List[Callable]] = {
            'power': [],           # Power distribution and regulation
            'signals': [],         # Signal integrity and routing
            'components': [],      # Component configuration and ratings
            'high_speed': [],      # High-speed interfaces and timing
            'safety': [],          # Safety and protection features
            'manufacturing': [],   # Manufacturing and assembly considerations
            'thermal': [],         # Thermal analysis and management
            'mechanical': []       # Mechanical and physical constraints
        }
        self._setup_default_validation_rules()
    
    def _setup_default_validation_rules(self):
        """Set up the default validation rules for each category."""
        # Power validation rules
        self.validation_rules['power'].extend([
            self._validate_power_nets,
            self._validate_power_pins,
            self._validate_decoupling,
            self._validate_power_regulators,
            self._validate_power_sequencing,
            self._validate_bulk_capacitance
        ])
        
        # Signal validation rules
        self.validation_rules['signals'].extend([
            self._validate_differential_pairs,
            self._validate_signal_terminations,
            self._validate_signal_returns,
            self._validate_unused_pins,
            self._validate_no_floating_inputs
        ])
        
        # Component validation rules
        self.validation_rules['components'].extend([
            self._validate_component_ratings,
            self._validate_reference_designators,
            self._validate_required_components,
            self._validate_component_values
        ])
        
        # High-speed validation rules
        self.validation_rules['high_speed'].extend([
            self._validate_clock_routing,
            self._validate_impedance_control,
            self._validate_length_matching,
            self._validate_clock_termination
        ])
        
        # Safety validation rules
        self.validation_rules['safety'].extend([
            self._validate_esd_protection,
            self._validate_overcurrent_protection,
            self._validate_reverse_voltage_protection,
            self._validate_safety_spacing
        ])
        
        # Manufacturing validation rules
        self.validation_rules['manufacturing'].extend([
            self._validate_test_points,
            self._validate_mounting_holes,
            self._validate_fiducial_marks,
            self._validate_component_spacing
        ])
        
        # Thermal validation rules
        self.validation_rules['thermal'].extend([
            self._validate_thermal_design,
            self._validate_component_spacing_thermal,
            self._validate_power_dissipation
        ])
        
        # Mechanical validation rules
        self.validation_rules['mechanical'].extend([
            self._validate_board_outline,
            self._validate_mounting_points,
            self._validate_connector_placement
        ])

    def _validate_power_nets(self, circuit: 'Circuit') -> List[str]:
        """Validate power net configuration and connections."""
        errors = []
        power_nets = [net for net in circuit.get_nets() 
                     if any(name in net.name.upper() 
                           for name in ['VDD', 'VCC', 'GND', 'VSS', 'VBUS'])]
        
        if not power_nets:
            errors.append("No power nets found in circuit")
            return errors
            
        for net in power_nets:
            # Check for unconnected power nets
            if not net.pins:
                errors.append(f"Power net {net.name} has no connections")
                
            # Check for single-point connection to ground
            if net.name.upper() in ['GND', 'VSS']:
                ground_components = set(pin.parent.ref for pin in net.pins)
                if len(ground_components) < 2:
                    errors.append(f"Ground net {net.name} may not be properly distributed")
                    
            # Check for power rail distribution
            if net.name.upper() in ['VDD', 'VCC', 'VBUS']:
                power_pins = [pin for pin in net.pins 
                            if pin.electrical_type in ['power_in', 'power_out']]
                if not power_pins:
                    errors.append(f"Power net {net.name} has no power input/output pins")
        
        return errors

    def _validate_power_pins(self, circuit: 'Circuit') -> List[str]:
        """Validate power pin connections and configurations."""
        errors = []
        
        for component in circuit.components:
            power_pins = [pin for pin in component.pins.values() 
                         if pin.electrical_type in ['power_in', 'power_out']]
            
            for pin in power_pins:
                # Check for unconnected power pins
                if not pin.net:
                    errors.append(f"Unconnected power pin: {str(pin)}")
                    continue
                    
                # Verify power pin is connected to appropriate net
                pin_name_upper = pin.name.upper()
                net_name_upper = pin.net.name.upper()
                
                if ('VDD' in pin_name_upper or 'VCC' in pin_name_upper) and \
                   not any(name in net_name_upper for name in ['VDD', 'VCC', 'VBUS']):
                    errors.append(f"Power pin {str(pin)} may be connected to wrong net: {pin.net.name}")
                    
                if ('GND' in pin_name_upper or 'VSS' in pin_name_upper) and \
                   not any(name in net_name_upper for name in ['GND', 'VSS']):
                    errors.append(f"Ground pin {str(pin)} may be connected to wrong net: {pin.net.name}")
        
        return errors

    def _validate_decoupling(self, circuit: 'Circuit') -> List[str]:
        """Validate decoupling capacitor placement and values."""
        errors = []
        power_pins = []
        
        # Collect all power pins
        for component in circuit.components:
            for pin in component.pins.values():
                if pin.electrical_type in ['power_in', 'power_out']:
                    power_pins.append(pin)
        
        # Check for decoupling capacitors near each power pin
        for pin in power_pins:
            # Find nearby capacitors (in a real implementation, this would use physical locations)
            caps = [comp for comp in circuit.components 
                   if comp.name == 'C' and 
                   any(p.net == pin.net for p in comp.pins.values())]
            
            if not caps:
                errors.append(f"No decoupling capacitors found for power pin {str(pin)}")
            else:
                # Verify decoupling capacitor values
                values = []
                for cap in caps:
                    try:
                        value = float(cap.parameters.get('Value', '0').replace('uF', ''))
                        values.append(value)
                    except ValueError:
                        errors.append(f"Invalid capacitor value for {cap.ref}")
                
                # Check for proper value distribution (typically want 0.1uF and 10uF)
                if not any(v >= 10 for v in values):
                    errors.append(f"No bulk decoupling (≥10uF) found for {str(pin)}")
                if not any(0.1 <= v <= 1 for v in values):
                    errors.append(f"No high-frequency decoupling (0.1-1uF) found for {str(pin)}")
        
        return errors

    def _validate_component_ratings(self, circuit: 'Circuit') -> List[str]:
        """Validate component ratings against operating conditions."""
        errors = []
        
        for component in circuit.components:
            # Voltage rating checks
            if hasattr(component.metadata, 'max_voltage') and component.metadata.max_voltage:
                try:
                    max_v = float(component.metadata.max_voltage.replace('V', ''))
                    # Add voltage analysis logic here
                except ValueError:
                    errors.append(f"Invalid voltage rating for {component.ref}")

            # Current rating checks
            if hasattr(component.metadata, 'max_current') and component.metadata.max_current:
                try:
                    max_i = float(component.metadata.max_current.replace('A', ''))
                    # Add current analysis logic here
                except ValueError:
                    errors.append(f"Invalid current rating for {component.ref}")

            # Temperature range checks
            if hasattr(component.metadata, 'temperature_range') and component.metadata.temperature_range:
                # Add temperature range validation logic here
                pass

        return errors

    def _validate_reference_designators(self, circuit: 'Circuit') -> List[str]:
        """Validate component reference designators."""
        errors = []
        refs = [c.ref for c in circuit.components]
        
        # Check for duplicate references
        if len(refs) != len(set(refs)):
            duplicates = [ref for ref in set(refs) if refs.count(ref) > 1]
            errors.extend(f"Duplicate reference designator: {ref}" for ref in duplicates)
        
        # Check reference format (letter followed by number)
        import re
        for ref in refs:
            if not re.match(r'^[A-Z]+\d+$', ref):
                errors.append(f"Invalid reference designator format: {ref}")
        
        return errors

    def add_rule(self, rule: Callable, category: str = 'components', name: str = None):
        """Add a custom validation rule to a specific category.
        
        Args:
            rule: Callable that takes a Circuit object and returns List[str] of errors
            category: Category to add the rule to (must exist)
            name: Optional name for the rule (defaults to function name)
        """
        if category not in self.validation_rules:
            raise ValueError(f"Invalid category: {category}")
            
        if name:
            rule.__name__ = name
            
        self.validation_rules[category].append(rule)

    def validate(self, circuit: 'Circuit', categories: List[str] = None) -> Dict[str, List[str]]:
        """Run validation rules on the circuit with optional category filtering.
        
        Args:
            circuit: Circuit object to validate
            categories: Optional list of categories to validate (defaults to all)
            
        Returns:
            Dictionary mapping categories to lists of error messages
        """
        results = {}
        
        # Determine which categories to validate
        if categories is None:
            categories = list(self.validation_rules.keys())
            
        # Run validations by category
        for category in categories:
            if category not in self.validation_rules:
                continue
                
            category_errors = []
            for rule in self.validation_rules[category]:
                try:
                    errors = rule(circuit)
                    if errors:
                        if isinstance(errors, list):
                            category_errors.extend(errors)
                        else:
                            category_errors.append(errors)
                except Exception as e:
                    category_errors.append(f"Error in {rule.__name__}: {str(e)}")
            
            if category_errors:
                results[category] = category_errors
                
        return results

    # Additional validation method stubs - these would need proper implementation
    def _validate_power_regulators(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_power_sequencing(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_bulk_capacitance(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_differential_pairs(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_signal_terminations(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_signal_returns(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_unused_pins(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_no_floating_inputs(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_required_components(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_component_values(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_clock_routing(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_impedance_control(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_length_matching(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_clock_termination(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_esd_protection(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_overcurrent_protection(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_reverse_voltage_protection(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_safety_spacing(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_test_points(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_mounting_holes(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_fiducial_marks(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_component_spacing(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_thermal_design(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_component_spacing_thermal(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_power_dissipation(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_board_outline(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_mounting_points(self, circuit: 'Circuit') -> List[str]:
        return []
        
    def _validate_connector_placement(self, circuit: 'Circuit') -> List[str]:
        return []


class Component:
    """Represents an electronic component in the circuit with enhanced metadata."""

    def __init__(self, 
                 library: str, 
                 name: str, 
                 parameters: Optional[Dict[str, Any]] = None,
                 symbol_lib: Optional[KicadSymbolLib] = None):
        self.ref = ''
        self.library = library
        self.name = name
        self.pins: Dict[str, Pin] = {}
        self.pin_names: Dict[str, str] = {}
        self.parameters: Dict[str, Any] = parameters or {}
        self.metadata = ComponentMetadata()
        self.symbol_lib = symbol_lib or KicadSymbolLib()

        self._load_component_info()

    def _load_component_info(self):
        """Load component information from KiCad library"""
        try:
            component_path = f"{self.library}:{self.name}"
            symbol_info = self.symbol_lib.get_symbol_info(component_path)

            if not symbol_info:
                raise ValueError(f"Component '{component_path}' not found in KiCad libraries")

            # Update metadata
            if symbol_info['properties'].get('Description'):
                self.metadata.description = symbol_info['properties']['Description'].strip('"')
            if symbol_info['properties'].get('Footprint'):
                self.metadata.footprint = symbol_info['properties']['Footprint'].strip('"')
            if symbol_info['properties'].get('Datasheet'):
                self.metadata.datasheet = symbol_info['properties']['Datasheet'].strip('"')
            if symbol_info['properties'].get('Keywords'):
                self.metadata.keywords = [k.strip() for k in symbol_info['properties']['Keywords'].strip('"').split(',')]

            # Create Pin objects
            for pin_info in symbol_info['pins']:
                pin_number = pin_info['number'].strip('"')
                pin_name = pin_info['name'].strip('"')
                
                if pin_name == "~":
                    pin_name = f"Pin_{pin_number}"

                pin = Pin(
                    number=pin_number,
                    name=pin_name,
                    parent=self,
                    electrical_type=pin_info.get('type', 'passive'),
                    graphic_style=pin_info.get('graphic_style', 'line')
                )
                self.pins[pin_number] = pin
                self.pin_names[pin_name] = pin_number

        except Exception as e:
            raise RuntimeError(f"Error loading component {self.name}: {str(e)}")

    def update_metadata(self, metadata_dict: Dict[str, Any]):
        """Update component metadata with new values"""
        self.metadata.update(metadata_dict)

    def __getitem__(self, item: str) -> Pin:
        try:
            if item in self.pins:
                return self.pins[item]
            elif item in self.pin_names:
                return self.pins[self.pin_names[item]]
            else:
                raise KeyError(item)
        except KeyError:
            available_pins = "\n".join(f"  Number: '{num}', Name: '{pin.name}'" 
                                     for num, pin in self.pins.items())
            raise KeyError(
                f"Pin '{item}' not found in component '{self.ref}' ({self.name}).\n"
                f"Available pins:\n{available_pins}"
            )

    def __repr__(self):
        return f"Component('{self.name}', ref='{self.ref}')"

class SubCircuit:
    """Represents a reusable circuit block with enhanced interfaces."""

    def __init__(self, name: str, circuit_type: CircuitType = CircuitType.MIXED):
        self.metadata = CircuitMetadata(name=name, circuit_type=circuit_type)
        self.circuit = Circuit(name=name, circuit_type=circuit_type)
        self.interface_nets: Dict[str, Net] = {}
        self.interface_pins: Dict[str, Pin] = {}
        self.dependencies: Set[SubCircuit] = set()
        self._frozen = False

    def expose_net(self, net: Net, interface_name: str):
        """Expose a net as part of the subcircuit's interface"""
        if self._frozen:
            raise ValueError(f"Cannot modify frozen subcircuit {self.metadata.name}")
        self.interface_nets[interface_name] = net

    def expose_pin(self, pin: Pin, interface_name: str):
        """Expose a pin as part of the subcircuit's interface"""
        if self._frozen:
            raise ValueError(f"Cannot modify frozen subcircuit {self.metadata.name}")
        self.interface_pins[interface_name] = pin

    def add_dependency(self, subcircuit: 'SubCircuit'):
        """Add a dependency on another subcircuit"""
        if subcircuit is self:
            raise ValueError("Cannot add subcircuit as its own dependency")
        self.dependencies.add(subcircuit)

    def freeze(self):
        """Prevent modifications to the subcircuit"""
        self._frozen = True
        self.circuit.freeze()

    def unfreeze(self):
        """Allow modifications to the subcircuit"""
        self._frozen = False
        self.circuit.unfreeze()

    def validate(self) -> List[str]:
        """Validate the subcircuit configuration"""
        errors = []
        
        # Check for required interface nets
        if not self.interface_nets and not self.interface_pins:
            errors.append(f"Subcircuit {self.metadata.name} has no interface nets or pins defined")
            
        # Validate dependencies
        for dep in self.dependencies:
            dep_errors = dep.validate()
            if dep_errors:
                errors.extend([f"Dependency {dep.metadata.name}: {err}" for err in dep_errors])
                
        # Validate internal circuit
        circuit_errors = self.circuit.validate()
        if circuit_errors:
            errors.extend(circuit_errors)
            
        return errors

    def add_to_circuit(self, parent_circuit: 'Circuit', prefix: str = ""):
        """Add this subcircuit to a parent circuit with optional reference prefix"""
        if self._frozen:
            raise ValueError(f"Cannot modify frozen subcircuit {self.metadata.name}")
            
        # Add dependencies first
        for dep in self.dependencies:
            dep.add_to_circuit(parent_circuit, prefix)

        # Add components with unique references
        for component in self.circuit.components:
            original_ref = component.ref
            prefix_char = original_ref[0]  # Get the reference prefix (U, C, R, etc.)
            
            # Get the current count for this prefix from the parent circuit
            current_count = parent_circuit.component_counts.get(prefix_char, 0)
            
            # Generate new reference
            if prefix:
                new_ref = f"{prefix}_{prefix_char}{current_count + 1}"
            else:
                new_ref = f"{prefix_char}{current_count + 1}"
                
            # Update the parent circuit's count for this prefix
            parent_circuit.component_counts[prefix_char] = current_count + 1
            
            # Update component reference
            component.ref = new_ref
            parent_circuit.add_component(component)
            
        # Add nets
        for net in self.circuit.get_nets():
            parent_circuit.add_net(net)
    def export_interface(self) -> Dict[str, Any]:
        """Export the subcircuit interface definition"""
        return {
            'name': self.metadata.name,
            'type': self.metadata.circuit_type.value,
            'interface_nets': {name: net.name for name, net in self.interface_nets.items()},
            'interface_pins': {name: str(pin) for name, pin in self.interface_pins.items()},
            'dependencies': [dep.metadata.name for dep in self.dependencies],
            'metadata': vars(self.metadata)
        }

    def __repr__(self):
        return f"SubCircuit('{self.metadata.name}', type='{self.metadata.circuit_type.value}')"

class Circuit:
    """Represents a complete circuit design with enhanced validation and organization."""

    def __init__(self, name: str = "main", circuit_type: CircuitType = CircuitType.MIXED):
        self.metadata = CircuitMetadata(name=name, circuit_type=circuit_type)
        self.components: List[Component] = []
        self.nets: Dict[str, Net] = {}
        self.component_counts: Dict[str, int] = {}
        self.subcircuits: List[SubCircuit] = []
        self.validator = CircuitValidator()
        self._frozen = False
        self._setup_default_validation_rules()

    def _setup_default_validation_rules(self):
        """Setup default circuit validation rules"""
        self.validator.add_rule(self._validate_power_connections)
        self.validator.add_rule(self._validate_pin_connections)
        self.validator.add_rule(self._validate_component_references)

    def _get_prefix(self, comp_type: str) -> str:
        """Get the reference designator prefix for a component type."""
        type_prefix_map = {
            'R': 'R',
            'C': 'C',
            'L': 'L',
            'Q': 'Q',
            'U': 'U',
            'D': 'D',
            'J': 'J',
            'Y': 'Y',
            'FB': 'FB',
            'P': 'P',
            'SW': 'SW',
            'LED': 'D',
            'IC': 'U',
            'ESP32': 'U',
            'LM1117DT': 'U',
            'USB': 'J',
            # Power component mapping
            '+3V3': '#PWR',
            '+5V': '#PWR',
            'GND': '#PWR',
            'GNDD': '#PWR',
            'VCC': '#PWR',
            'VSS': '#PWR',
            'VBUS': '#PWR',
        }
        return type_prefix_map.get(comp_type.upper(), 'U')


    def freeze(self):
        """Prevent modifications to the circuit"""
        self._frozen = True
        for net in self.nets.values():
            net.freeze()

    def unfreeze(self):
        """Allow modifications to the circuit"""
        self._frozen = False
        for net in self.nets.values():
            net.unfreeze()

    def add_component(self, component: Component) -> bool:
        """Add a component to the circuit with validation"""
        if self._frozen:
            raise ValueError("Cannot modify frozen circuit")
            
        if not component.ref:
            comp_type = component.name.split('_')[0]
            prefix = self._get_prefix(comp_type)
            count = self.component_counts.get(prefix, 0) + 1
            self.component_counts[prefix] = count
            component.ref = f"{prefix}{count}"
            
        if component.ref in [c.ref for c in self.components]:
            raise ValueError(f"Component reference '{component.ref}' already exists")
            
        self.components.append(component)
        return True

    def add_net(self, net: Net) -> bool:
        """Add a net to the circuit with validation"""
        if self._frozen:
            raise ValueError("Cannot modify frozen circuit")
            
        if net.name in self.nets:
            existing_net = self.nets[net.name]
            existing_net += net
            return False
        else:
            self.nets[net.name] = net
            return True

    def add_subcircuit(self, subcircuit: SubCircuit, prefix: str = ""):
        """Add a subcircuit to this circuit"""
        if self._frozen:
            raise ValueError("Cannot modify frozen circuit")
            
        subcircuit.add_to_circuit(self, prefix)
        self.subcircuits.append(subcircuit)

    def _validate_power_connections(self, circuit: 'Circuit') -> List[str]:
        """Validate power connections in the circuit"""
        errors = []
        power_nets = [net for net in circuit.get_nets() if net.net_type == "power"]
        
        if not power_nets:
            errors.append("No power nets found in circuit")
            
        for net in power_nets:
            if not net.pins:
                errors.append(f"Power net {net.name} has no connections")
                
        return errors

    def _validate_pin_connections(self, circuit: 'Circuit') -> List[str]:
        """Validate pin connections in the circuit"""
        errors = []
        for component in circuit.components:
            for pin in component.pins.values():
                if pin.electrical_type in ['power_in', 'power_out'] and not pin.net:
                    errors.append(f"Unconnected power pin: {str(pin)}")
        return errors

    def _validate_component_references(self, circuit: 'Circuit') -> List[str]:
        """Validate component reference designators"""
        errors = []
        refs = [c.ref for c in circuit.components]
        if len(refs) != len(set(refs)):
            errors.append("Duplicate component references found")
        return errors
    def validate(self) -> List[str]:
        """Run all validation rules on the circuit"""
        return self.validator.validate(self)

    def get_nets(self) -> List[Net]:
        """Get all nets in the circuit"""
        nets_set = set()
        for component in self.components:
            for pin in component.pins.values():
                if pin.net:
                    nets_set.add(pin.net)
        return list(nets_set)

    def export_circuit(self) -> str:
        """Export the circuit as JSON with enhanced metadata and proper enum handling"""
        circuit_data = {
            'metadata': {
                'name': self.metadata.name,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'version': self.metadata.version,
                'created_date': self.metadata.created_date,
                'modified_date': self.metadata.modified_date,
                'circuit_type': self.metadata.circuit_type.value,  # Convert enum to string
                'tags': self.metadata.tags,
                'properties': self.metadata.properties
            },
            'components': [],
            'nets': {},
            'subcircuits': []
        }

        # Export components
        for component in self.components:
            comp_info = {
                'ref': component.ref,
                'name': component.name,
                'library': component.library,
                'pins': {pin.number: pin.name for pin in component.pins.values()},
                'parameters': component.parameters,
                'metadata': {
                    'description': component.metadata.description,
                    'footprint': component.metadata.footprint,
                    'datasheet': component.metadata.datasheet,
                    'keywords': component.metadata.keywords,
                    'max_voltage': component.metadata.max_voltage,
                    'max_current': component.metadata.max_current,
                    'temperature_range': component.metadata.temperature_range
                }
            }
            circuit_data['components'].append(comp_info)

        # Export nets
        for net in self.get_nets():
            circuit_data['nets'][net.name] = {
                'connections': [f"{pin.parent.ref}.{pin.name}" for pin in net.pins],
                'metadata': net.metadata
            }

        # Export subcircuits
        for subcircuit in self.subcircuits:
            subcircuit_info = {
                'name': subcircuit.metadata.name,
                'type': subcircuit.metadata.circuit_type.value,  # Convert enum to string
                'interface_nets': {name: net.name for name, net in subcircuit.interface_nets.items()},
                'interface_pins': {name: str(pin) for name, pin in subcircuit.interface_pins.items()},
                'dependencies': [dep.metadata.name for dep in subcircuit.dependencies]
            }
            circuit_data['subcircuits'].append(subcircuit_info)

        return json.dumps(circuit_data, indent=4)
    def generate_circuit_report(self) -> str:
        """Generate a detailed circuit report"""
        report = []
        report.append(f"Circuit Report: {self.metadata.name}")
        report.append(f"Type: {self.metadata.circuit_type.value}")
        
        # Component information
        report.append("\nComponent Information:")
        for component in self.components:
            report.append(f"\n{component.ref} ({component.name}):")
            if component.metadata.description:
                report.append(f"  Description: {component.metadata.description}")
            if component.metadata.footprint:
                report.append(f"  Footprint: {component.metadata.footprint}")
            if component.metadata.max_voltage:
                report.append(f"  Max Voltage: {component.metadata.max_voltage}")
            if component.metadata.max_current:
                report.append(f"  Max Current: {component.metadata.max_current}")

        # Net connections
        report.append("\nNet Connections:")
        for net in self.get_nets():
            report.append(f"\nNet: {net.name} (Type: {net.net_type})")
            connections = {}
            for pin in net.pins:
                if pin.parent.ref not in connections:
                    connections[pin.parent.ref] = []
                connections[pin.parent.ref].append(pin.name)
                
            for ref, pins in sorted(connections.items()):
                report.append(f"  {ref}: {', '.join(pins)}")

        return "\n".join(report)

    def __repr__(self):
        return f"Circuit('{self.metadata.name}', components={len(self.components)}, nets={len(self.get_nets())})"
    def ERC(self) -> None:
        """
        Perform Electrical Rule Check on the circuit.
        Prints warnings to stdout.
        """
        errors = self.validate()
        
        if errors:
            print("ERC Warnings:")
            for error in errors:
                print(f"- {error}")
        else:
            print("No ERC warnings.")
    def generate_bom(self):
        """Generate and print Bill of Materials"""
        bom = {}
        for component in self.components:
            key = (component.library, component.name, frozenset(component.parameters.items()))

            if key in bom:
                bom[key]['quantity'] += 1
                bom[key]['refs'].append(component.ref)
            else:
                bom[key] = {
                    'library': component.library,
                    'name': component.name,
                    'parameters': component.parameters,
                    'quantity': 1,
                    'refs': [component.ref],
                    'manufacturer_part_number': component.parameters.get('MPN', ''),
                }

        print("\nBill of Materials:")
        print("{:<10} {:<30} {:<10} {:<20} {:<15}".format(
            'Quantity', 'Part', 'Library', 'Refs', 'MPN'))
        for item in bom.values():
            refs = ','.join(item['refs'])
            print("{:<10} {:<30} {:<10} {:<20} {:<15}".format(
                item['quantity'],
                item['name'],
                item['library'],
                refs,
                item['manufacturer_part_number']
            ))