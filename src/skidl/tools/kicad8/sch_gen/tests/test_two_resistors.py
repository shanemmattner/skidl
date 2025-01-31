import pytest
import logging
from pathlib import Path
from skidl import *
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
TEST_PROJECT_NAME = "test_two_resistors"

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
def two_resistors_circuit():
    """Create a test circuit with two resistors with standard parameters."""
    r4 = Part("Device", "R", 
              ref="R4",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r4.MFG = "0603WAF1002T5E"
    
    r5 = Part("Device", "R", 
              ref="R5",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r5.MFG = "0603WAF1002T5E"

def get_resistor_properties(instance_sexpr):
    """
    Extract resistor properties from a symbol instance s-expression.
    
    Args:
        instance_sexpr: SExpr node representing a symbol instance
        
    Returns:
        Dictionary of property name-value pairs
    """
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
                logger.debug("Found property: %s = %s", prop_name, prop_value)
    return properties

def verify_resistor_properties(properties, ref, expected_value):
    """
    Verify that a resistor's properties match expected values.
    
    Args:
        properties: Dictionary of property name-value pairs
        ref: Expected reference designator
        expected_value: Expected resistance value
    
    Raises:
        AssertionError if properties don't match expectations
    """
    logger.debug("Verifying properties for %s: %s", ref, properties)
    
    assert properties['Reference'] == ref, \
        f"Reference mismatch for {ref}: got {properties['Reference']}"
    assert properties['Value'] == expected_value, \
        f"Value mismatch for {ref}: expected {expected_value}, got {properties['Value']}"
    
    if 'Footprint' in properties:
        footprint = properties['Footprint']
        expected_footprint = "Resistor_SMD:R_0603_1608Metric"
        assert footprint == expected_footprint, \
            f"Footprint mismatch for {ref}: expected '{expected_footprint}', got '{footprint}'"

def test_two_resistors_schematic(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with two resistors.
    Verifies schematic structure and both resistor instances.
    """
    # Create circuit with @SubCircuit decorator
    two_resistors_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="Two Resistors Test"
    )

    # Verify schematic path
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "two_resistors_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"

    # Load and parse schematic
    with open(schematic_path) as f:
        generated_content = f.read()
        logger.debug("Generated schematic content:\n%s", generated_content)

    generated_tree = schematic_parser.parse(generated_content)

    # Find all resistor instances
    resistor_instances = {}  # ref: properties mapping
    
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
            
        # Check if it's a resistor
        is_resistor = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'lib_id' and 
                prop.get_attribute_value().strip('"') == 'Device:R'):
                is_resistor = True
                break
                
        if is_resistor:
            properties = get_resistor_properties(child)
            if 'Reference' in properties:
                resistor_instances[properties['Reference']] = properties

    # Verify both resistors were found
    expected_refs = {"R4", "R5"}
    found_refs = set(resistor_instances.keys())
    assert found_refs == expected_refs, \
        f"Missing resistors: expected {expected_refs}, found {found_refs}"
    
    # Verify properties of each resistor
    for ref in expected_refs:
        assert ref in resistor_instances, f"Resistor {ref} not found in schematic"
        verify_resistor_properties(resistor_instances[ref], ref, "10k")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"