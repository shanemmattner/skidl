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
TEST_PROJECT_NAME = "test_four_resistors"

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
def four_resistors_circuit():
    """Create a test circuit with four resistors with standard parameters."""
    resistors = []
    for i in range(1, 5):  # Create R1 through R4
        r = Part("Device", "R", 
                ref=f"R{i}",
                value="10k", 
                footprint="Resistor_SMD:R_0603_1608Metric")
        r.MFG = "0603WAF1002T5E"
        resistors.append(r)

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

def validate_kicad_pro_structure(project_data):
    """
    Validate that a KiCad project file contains all required sections.
    
    Args:
        project_data: Parsed JSON data from .kicad_pro file
        
    Raises:
        AssertionError: If any required section is missing or invalid
    """
    # Check required top-level sections
    required_sections = [
        "board", "libraries", "meta", "net_settings",
        "pcbnew", "schematic", "sheets"
    ]
    for section in required_sections:
        assert section in project_data, f"Missing required section: {section}"
    
    # Validate meta section
    assert "version" in project_data["meta"], "Missing version in meta section"
    assert "filename" in project_data["meta"], "Missing filename in meta section"
    assert isinstance(project_data["meta"]["version"], int), "Version must be integer"
    
    # Validate sheets section
    assert isinstance(project_data["sheets"], list), "Sheets must be a list"
    for sheet in project_data["sheets"]:
        assert "path" in sheet, "Sheet missing path"
        assert "sheet_name" in sheet, "Sheet missing name"
        assert "id" in sheet, "Sheet missing id"
        # Verify UUID is valid
        try:
            uuid.UUID(sheet["id"])
        except ValueError:
            raise AssertionError(f"Invalid UUID in sheet: {sheet['id']}")

def validate_kicad_pro_content(project_data, project_name):
    """
    Validate the content of a KiCad project file matches expected values.
    
    Args:
        project_data: Parsed JSON data from .kicad_pro file
        project_name: Expected name of the project
        
    Raises:
        AssertionError: If content doesn't match expected values
    """
    # Check project filename
    expected_filename = f"{project_name}.kicad_pro"
    assert project_data["meta"]["filename"] == expected_filename, \
        f"Wrong filename in meta: {project_data['meta']['filename']} != {expected_filename}"
    
    # Check sheet paths
    expected_sheets = [
        f"{project_name}.kicad_sch",
        "four_resistors_circuit.kicad_sch"
    ]
    actual_sheets = [sheet["path"] for sheet in project_data["sheets"]]
    assert sorted(actual_sheets) == sorted(expected_sheets), \
        f"Sheet paths don't match: {actual_sheets} != {expected_sheets}"
    
    # Verify default net class exists
    assert "classes" in project_data["net_settings"], "Missing net classes"
    net_classes = project_data["net_settings"]["classes"]
    assert len(net_classes) > 0, "No net classes defined"
    default_class = net_classes[0]
    assert default_class["name"] == "Default", "Missing default net class"

def test_four_resistors_schematic(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with four resistors.
    Verifies schematic structure and all resistor instances.
    """
    # Create circuit with @SubCircuit decorator
    four_resistors_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="Four Resistors Test"
    )

    # Verify schematic path
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "four_resistors_circuit.kicad_sch"
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

    # Verify all four resistors were found
    expected_refs = {f"R{i}" for i in range(1, 5)}  # R1 through R4
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