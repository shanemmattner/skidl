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
TEST_PROJECT_NAME = "test_rlc_parts"

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
def rlc_parts_circuit():
    """Create a test circuit with R, L, and C components with standard parameters."""
    r = Part("Device", "R_Small", ref="R1", value="10k", 
             footprint="R_0603_1608Metric")
    l = Part("Device", "L_Small", ref="L1", value="100uH",
             footprint="L_0603_1608Metric")
    c = Part("Device", "C_Small", ref="C1", value="100nF",
             footprint="C_0603_1608Metric")

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

def validate_kicad_pro_structure(project_data):
    """
    Validate that a KiCad project file contains all required sections.
    """
    required_sections = [
        "board", "libraries", "meta", "net_settings",
        "pcbnew", "schematic", "sheets"
    ]
    for section in required_sections:
        assert section in project_data, f"Missing required section: {section}"
    
    assert "version" in project_data["meta"], "Missing version in meta section"
    assert "filename" in project_data["meta"], "Missing filename in meta section"
    assert isinstance(project_data["meta"]["version"], int), "Version must be integer"
    
    assert isinstance(project_data["sheets"], list), "Sheets must be a list"
    for sheet in project_data["sheets"]:
        assert "path" in sheet, "Sheet missing path"
        assert "sheet_name" in sheet, "Sheet missing name"
        assert "id" in sheet, "Sheet missing id"
        try:
            uuid.UUID(sheet["id"])
        except ValueError:
            raise AssertionError(f"Invalid UUID in sheet: {sheet['id']}")

def validate_kicad_pro_content(project_data, project_name):
    """
    Validate the content of a KiCad project file matches expected values.
    """
    expected_filename = f"{project_name}.kicad_pro"
    assert project_data["meta"]["filename"] == expected_filename, \
        f"Wrong filename in meta: {project_data['meta']['filename']} != {expected_filename}"
    
    expected_sheets = [
        f"{project_name}.kicad_sch",
        "rlc_parts_circuit.kicad_sch"
    ]
    actual_sheets = [sheet["path"] for sheet in project_data["sheets"]]
    assert sorted(actual_sheets) == sorted(expected_sheets), \
        f"Sheet paths don't match: {actual_sheets} != {expected_sheets}"
    
    assert "classes" in project_data["net_settings"], "Missing net classes"
    net_classes = project_data["net_settings"]["classes"]
    assert len(net_classes) > 0, "No net classes defined"
    default_class = net_classes[0]
    assert default_class["name"] == "Default", "Missing default net class"

def test_rlc_parts_schematic(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with RLC components.
    Verifies the schematic structure, component placement, properties,
    and proper KiCad project file generation.
    """
    # Create the circuit
    rlc_parts_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="RLC Parts Test"
    )

    # Get project directory path
    project_dir = temp_project_dir / TEST_PROJECT_NAME
    
    # Verify schematic files
    schematic_path = project_dir / "rlc_parts_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"

    main_schematic = project_dir / f"{TEST_PROJECT_NAME}.kicad_sch"
    assert main_schematic.exists(), f"Main schematic not generated at {main_schematic}"

    # Verify KiCad project file
    project_file = project_dir / f"{TEST_PROJECT_NAME}.kicad_pro"
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
    
    # Verify lib_symbols section exists
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find all RLC component instances
    symbol_instances = [child for child in generated_tree.attributes 
                       if isinstance(child, SExpr) and child.token == 'symbol']
    assert len(symbol_instances) == 3, "Expected exactly 3 components (R, L, C)"
    
    # Expected component properties
    expected_components = {
        'R1': {'lib_id': 'Device:R_Small', 'value': '10k', 'footprint': 'R_0603_1608Metric'},
        'L1': {'lib_id': 'Device:L_Small', 'value': '100uH', 'footprint': 'L_0603_1608Metric'},
        'C1': {'lib_id': 'Device:C_Small', 'value': '100nF', 'footprint': 'C_0603_1608Metric'}
    }
    
    # Verify each component
    found_components = set()
    for instance in symbol_instances:
        props = [child for child in instance.attributes 
                if isinstance(child, SExpr) and child.token == 'property']
        
        ref = get_property_value(props, 'Reference')
        assert ref in expected_components, f"Unexpected component reference: {ref}"
        
        # Verify lib_id
        lib_id = None
        for child in instance.attributes:
            if isinstance(child, SExpr) and child.token == 'lib_id':
                lib_id = child.get_attribute_value().strip('"')
                break
        assert lib_id == expected_components[ref]['lib_id'], \
            f"Wrong lib_id for {ref}: expected {expected_components[ref]['lib_id']}, got {lib_id}"
        
        # Verify value and footprint
        value = get_property_value(props, 'Value')
        assert value == expected_components[ref]['value'], \
            f"Wrong value for {ref}: expected {expected_components[ref]['value']}, got {value}"
        
        footprint = get_property_value(props, 'Footprint')
        assert footprint == expected_components[ref]['footprint'], \
            f"Wrong footprint for {ref}: expected {expected_components[ref]['footprint']}, got {footprint}"
        
        found_components.add(ref)
    
    # Verify all expected components were found
    assert found_components == set(expected_components.keys()), \
        f"Missing components: {set(expected_components.keys()) - found_components}"

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"