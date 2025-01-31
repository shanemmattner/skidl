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
TEST_PROJECT_NAME = "test_esp32_s3"

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
def esp32_s3_circuit():
    """Create a test circuit with ESP32-S3 module."""
    esp32 = Part("RF_Module", "ESP32-S3-WROOM-1", 
                ref="U1",
                footprint="Module:ESP32-S3-WROOM-1")
    esp32.MFG = "Espressif"
    
def get_mcu_properties(instance_sexpr):
    """
    Extract MCU properties from a symbol instance s-expression.
    
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

def verify_mcu_properties(properties, ref, expected_value):
    """
    Verify that an MCU's properties match expected values.
    
    Args:
        properties: Dictionary of property name-value pairs
        ref: Expected reference designator
        expected_value: Expected module value
    
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
        expected_footprint = "Module:ESP32-S3-WROOM-1"
        assert footprint == expected_footprint, \
            f"Footprint mismatch for {ref}: expected '{expected_footprint}', got '{footprint}'"

def test_esp32_s3_schematic(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with ESP32-S3 module.
    Verifies schematic structure and module instance.
    """
    # Create circuit with @SubCircuit decorator
    esp32_s3_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="ESP32-S3 Test"
    )

    # Verify schematic path
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "esp32_s3_circuit.kicad_sch"
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
    
    # Verify lib_symbols section exists and contains RF_Module:ESP32-S3-WROOM-1
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find the ESP32-S3 symbol definition
    gen_esp32_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == 'RF_Module:ESP32-S3-WROOM-1':
                gen_esp32_symbol = child
                break
    
    assert gen_esp32_symbol is not None, "RF_Module:ESP32-S3-WROOM-1 symbol definition missing from lib_symbols"
    
    # Find ESP32-S3 instance
    mcu_instances = {}  # ref: properties mapping
    
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
            
        # Check if it's ESP32-S3
        is_esp32 = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'lib_id' and 
                prop.get_attribute_value().strip('"') == 'RF_Module:ESP32-S3-WROOM-1'):
                is_esp32 = True
                break
                
        if is_esp32:
            properties = get_mcu_properties(child)
            if 'Reference' in properties:
                mcu_instances[properties['Reference']] = properties

    # Verify ESP32-S3 was found
    expected_refs = {"U1"}
    found_refs = set(mcu_instances.keys())
    assert found_refs == expected_refs, \
        f"Missing MCU: expected {expected_refs}, found {found_refs}"
    
    # Verify properties of ESP32-S3
    for ref in expected_refs:
        assert ref in mcu_instances, f"MCU {ref} not found in schematic"
        verify_mcu_properties(mcu_instances[ref], ref, "ESP32-S3-WROOM-1")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"