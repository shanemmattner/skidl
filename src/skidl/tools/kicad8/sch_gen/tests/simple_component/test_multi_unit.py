import pytest
import logging
import json
import uuid
from pathlib import Path
from skidl import *
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
TEST_PROJECT_NAME = "test_multi_unit"

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
def multi_unit_circuit():
    """Create a test circuit with a multi-unit component."""
    # Create a multi-unit component (example: 74LS00 quad NAND gate)
    nand_gate = Part("74xx", "74LS00", 
                    ref="U1",
                    footprint="Package_DIP:DIP-14_W7.62mm")
    nand_gate.MFG = "Texas Instruments"
    
    # Connect inputs and outputs for testing
    nand_gate[1].A += Net('A1')
    nand_gate[1].B += Net('B1')
    nand_gate[1].Y += Net('Y1')
    
    nand_gate[2].A += Net('A2')
    nand_gate[2].B += Net('B2')
    nand_gate[2].Y += Net('Y2')

def get_multi_unit_properties(instance_sexpr):
    """
    Extract multi-unit component properties from a symbol instance s-expression.
    
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

def verify_multi_unit_properties(properties, ref, expected_value):
    """
    Verify that a multi-unit component's properties match expected values.
    
    Args:
        properties: Dictionary of property name-value pairs
        ref: Expected reference designator
        expected_value: Expected component value
    
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
        expected_footprint = "Package_DIP:DIP-14_W7.62mm"
        assert footprint == expected_footprint, \
            f"Footprint mismatch for {ref}: expected '{expected_footprint}', got '{footprint}'"

def test_multi_unit_schematic(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with a multi-unit component.
    Verifies schematic structure and component instance.
    """
    # Create circuit with @SubCircuit decorator
    multi_unit_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="Multi-Unit Test"
    )

    # Verify schematic path
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "multi_unit_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"

    # Verify KiCad project file
    project_file = temp_project_dir / TEST_PROJECT_NAME / f"{TEST_PROJECT_NAME}.kicad_pro"
    assert project_file.exists(), f"Project file not generated at {project_file}"

    # Parse and validate project file
    with open(project_file) as f:
        project_data = json.loads(f.read())
        logger.debug("Generated project file content:\n%s", json.dumps(project_data, indent=2))

    # Validate project file structure and content
    validate_kicad_pro_structure(project_data)
    validate_kicad_pro_content(project_data, TEST_PROJECT_NAME)
        
    # Parse and verify schematic content
    with open(schematic_path) as f:
        generated_content = f.read()
        logger.debug("Generated schematic content:\n%s", generated_content)
        
    # Parse into s-expression tree
    generated_tree = schematic_parser.parse(generated_content)
    
    # Verify lib_symbols section exists and contains 74xx:74LS00
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find the 74LS00 symbol definition
    gen_nand_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == '74xx:74LS00':
                gen_nand_symbol = child
                break
    
    assert gen_nand_symbol is not None, "74xx:74LS00 symbol definition missing from lib_symbols"
    
    # Find 74LS00 instances
    nand_instances = {}  # ref: properties mapping
    
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
            
        # Check if it's 74LS00
        is_nand = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'lib_id' and 
                prop.get_attribute_value().strip('"') == '74xx:74LS00'):
                is_nand = True
                break
                
        if is_nand:
            properties = get_multi_unit_properties(child)
            if 'Reference' in properties:
                nand_instances[properties['Reference']] = properties

    # Verify 74LS00 was found
    expected_refs = {"U1"}
    found_refs = set(nand_instances.keys())
    assert found_refs == expected_refs, \
        f"Missing 74LS00: expected {expected_refs}, found {found_refs}"
    
    # Verify properties of 74LS00
    for ref in expected_refs:
        assert ref in nand_instances, f"74LS00 {ref} not found in schematic"
        verify_multi_unit_properties(nand_instances[ref], ref, "74LS00")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"