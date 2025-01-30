import pytest
import logging
from pathlib import Path
from skidl import *
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the path to the reference schematics directory
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"

@pytest.fixture(autouse=True)
def setup_circuit():
    """Reset the circuit before and after each test to ensure a clean state."""
    Circuit.reset(default_circuit)
    yield
    Circuit.reset(default_circuit)

@pytest.fixture
def schematic_parser():
    """Provide a SchematicParser instance for parsing KiCad schematics."""
    return SchematicParser()

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project to ensure test isolation."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

@SubCircuit
def resistor_circuit():
    """Create a resistor circuit for testing with standard parameters."""
    r = Part("Device", "R", ref="R1", value="2.2k", 
             footprint="R_0603_1608Metric")

def get_property_value(props, prop_name):
    """
    Extract a property value from a list of s-expression properties.
    
    Args:
        props: List of SExpr nodes representing properties
        prop_name: Name of the property to find
        
    Returns:
        String value of the property or None if not found
    """
    for prop in props:
        if isinstance(prop, SExpr) and prop.token == 'property':
            if prop.get_attribute_value() == prop_name:
                value = prop.attributes[1] if len(prop.attributes) > 1 else None
                if value:
                    return value.strip('"')
    return None

def test_schematic_generation(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with one resistor component.
    Verifies the schematic structure, component placement, and properties.
    """
    # Create the circuit
    resistor_circuit()

    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name="resistor",
        title="Test One Resistor Schematic"
    )

    # Verify schematic files
    schematic_path = temp_project_dir / "resistor" / "resistor_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"

    main_schematic = temp_project_dir / "resistor" / "resistor.kicad_sch"
    assert main_schematic.exists(), f"Main schematic not generated at {main_schematic}"
        
    # Parse and verify schematic content
    with open(schematic_path) as f:
        generated_content = f.read()
        logger.debug("Generated schematic content:\n%s", generated_content)
        
    # Parse into s-expression tree
    generated_tree = schematic_parser.parse(generated_content)
    
    # Verify lib_symbols section exists and contains Device:R
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find the resistor symbol definition
    gen_r_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == 'Device:R':
                gen_r_symbol = child
                break
    
    assert gen_r_symbol is not None, "Device:R symbol definition missing from lib_symbols"
    
    # Verify resistor instance
    symbol_instances = [child for child in generated_tree.attributes 
                       if isinstance(child, SExpr) and child.token == 'symbol']
    assert len(symbol_instances) > 0, "No symbol instances found in schematic"
    
    resistor_instance = None
    for sym in symbol_instances:
        for child in sym.attributes:
            if isinstance(child, SExpr) and child.token == 'lib_id':
                lib_id = child.get_attribute_value().strip('"')
                if lib_id == 'Device:R':
                    resistor_instance = sym
                    break
    
    assert resistor_instance is not None, "Resistor instance not found in schematic"
    
    # Verify resistor properties
    props = [child for child in resistor_instance.attributes 
             if isinstance(child, SExpr) and child.token == 'property']
    
    ref_value = get_property_value(props, 'Reference')
    assert ref_value == 'R1', f"Incorrect resistor reference: expected 'R1', got '{ref_value}'"
    
    value = get_property_value(props, 'Value')
    assert value == '2.2k', f"Incorrect resistor value: expected '2.2k', got '{value}'"
    
    footprint = get_property_value(props, 'Footprint')
    expected_footprint = 'R_0603_1608Metric'
    assert footprint == expected_footprint, \
        f"Incorrect footprint: expected '{expected_footprint}', got '{footprint}'"