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
def capacitor_circuit():
    """Create a capacitor circuit for testing with standard parameters."""
    c = Part("Device", "C", ref="C1", value="10nF", footprint="C_0603_1608Metric")

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
        "capacitor_circuit.kicad_sch"
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
    Test generating a schematic with one capacitor component.
    Verifies the schematic structure, component placement, properties,
    and proper KiCad project file generation.
    """
    # Create the circuit
    capacitor_circuit()

    # Use different directory and project names to test naming logic
    project_name = "test_capacitor_alpha"
    project_dir_name = "capacitor_test_beta"
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir / project_dir_name),
        project_name=project_name,
        title="Test One Capacitor Schematic"
    )

    # Get project directory path
    project_dir = temp_project_dir / project_dir_name / project_name

    # Verify schematic files
    schematic_path = project_dir / "capacitor_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"

    main_schematic = project_dir / f"{project_name}.kicad_sch"
    assert main_schematic.exists(), f"Main schematic not generated at {main_schematic}"

    # Verify KiCad project file
    project_file = project_dir / f"{project_name}.kicad_pro"
    assert project_file.exists(), f"Project file not generated at {project_file}"

    # Parse and validate project file
    with open(project_file) as f:
        project_data = json.loads(f.read())
        logger.debug("Generated project file content:\n%s", json.dumps(project_data, indent=2))

    # Validate project file structure and content
    validate_kicad_pro_structure(project_data)
    validate_kicad_pro_content(project_data, project_name)
        
    # Parse and verify schematic content
    with open(schematic_path) as f:
        generated_content = f.read()
        logger.debug("Generated schematic content:\n%s", generated_content)
        
    # Parse into s-expression tree
    generated_tree = schematic_parser.parse(generated_content)
    
    # Verify lib_symbols section exists and contains Device:C
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find the capacitor symbol definition
    gen_c_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == 'Device:C':
                gen_c_symbol = child
                break
    
    assert gen_c_symbol is not None, "Device:C symbol definition missing from lib_symbols"
    
    # Verify capacitor instance
    symbol_instances = [child for child in generated_tree.attributes 
                       if isinstance(child, SExpr) and child.token == 'symbol']
    assert len(symbol_instances) > 0, "No symbol instances found in schematic"
    
    capacitor_instance = None
    for sym in symbol_instances:
        for child in sym.attributes:
            if isinstance(child, SExpr) and child.token == 'lib_id':
                lib_id = child.get_attribute_value().strip('"')
                if lib_id == 'Device:C':
                    capacitor_instance = sym
                    break
    
    assert capacitor_instance is not None, "Capacitor instance not found in schematic"
    
    # Verify capacitor properties
    props = [child for child in capacitor_instance.attributes 
             if isinstance(child, SExpr) and child.token == 'property']
    
    ref_value = get_property_value(props, 'Reference')
    assert ref_value == 'C1', f"Incorrect capacitor reference: expected 'C1', got '{ref_value}'"
    
    value = get_property_value(props, 'Value')
    assert value == '10nF', f"Incorrect capacitor value: expected '10nF', got '{value}'"
    
    footprint = get_property_value(props, 'Footprint')
    expected_footprint = 'C_0603_1608Metric'
    assert footprint == expected_footprint, \
        f"Incorrect footprint: expected '{expected_footprint}', got '{footprint}'"