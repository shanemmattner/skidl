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
def regulator_circuit():
    """Create a voltage regulator circuit for testing with standard parameters."""
    reg = Part("Regulator_Linear", "NCP1117-3.3_SOT223", 
               ref="U2", 
               footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2")

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
        "regulator_circuit.kicad_sch"
    ]
    actual_sheets = [sheet["path"] for sheet in project_data["sheets"]]
    assert sorted(actual_sheets) == sorted(expected_sheets), \
        f"Sheet paths don't match: {actual_sheets} != {expected_sheets}"
    
    assert "classes" in project_data["net_settings"], "Missing net classes"
    net_classes = project_data["net_settings"]["classes"]
    assert len(net_classes) > 0, "No net classes defined"
    default_class = net_classes[0]
    assert default_class["name"] == "Default", "Missing default net class"

def get_property_value(props, prop_name):
    """Extract a property value from a list of s-expression properties."""
    for prop in props:
        if isinstance(prop, SExpr) and prop.token == 'property':
            if prop.get_attribute_value() == prop_name:
                value = prop.attributes[1] if len(prop.attributes) > 1 else None
                if value:
                    return value.strip('"')
    return None

def test_regulator_schematic_generation(temp_project_dir, schematic_parser):
    """
    Test generating a schematic with NCP1117-3.3V regulator component.
    Verifies the schematic structure, component placement, and properties.
    """
    # Create the circuit
    regulator_circuit()

    project_name = "test_regulator"
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=project_name,
        title="Test NCP1117-3.3V Regulator Schematic"
    )

    # Get project directory path
    project_dir = temp_project_dir / project_name

    # Verify schematic files
    schematic_path = project_dir / "regulator_circuit.kicad_sch"
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
    
    # Verify lib_symbols section exists and contains Regulator_Linear:NCP1117-3.3_SOT223
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section in generated schematic"
    
    # Find the regulator symbol definition
    gen_reg_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == 'Regulator_Linear:NCP1117-3.3_SOT223':
                gen_reg_symbol = child
                break
    
    assert gen_reg_symbol is not None, "Regulator symbol definition missing from lib_symbols"
    
    # Verify regulator instance
    symbol_instances = [child for child in generated_tree.attributes 
                       if isinstance(child, SExpr) and child.token == 'symbol']
    assert len(symbol_instances) > 0, "No symbol instances found in schematic"
    
    regulator_instance = None
    for sym in symbol_instances:
        for child in sym.attributes:
            if isinstance(child, SExpr) and child.token == 'lib_id':
                lib_id = child.get_attribute_value().strip('"')
                if lib_id == 'Regulator_Linear:NCP1117-3.3_SOT223':
                    regulator_instance = sym
                    break
    
    assert regulator_instance is not None, "Regulator instance not found in schematic"
    
    # Verify regulator properties
    props = [child for child in regulator_instance.attributes 
             if isinstance(child, SExpr) and child.token == 'property']
    
    # Check reference designator
    ref_value = get_property_value(props, 'Reference')
    assert ref_value == 'U2', f"Incorrect regulator reference: expected 'U2', got '{ref_value}'"
    
    # Check value property
    value = get_property_value(props, 'Value')
    expected_value = 'NCP1117-3.3_SOT223'
    assert value == expected_value, \
        f"Incorrect regulator value: expected '{expected_value}', got '{value}'"
    
    # Check footprint
    footprint = get_property_value(props, 'Footprint')
    expected_footprint = 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'
    assert footprint == expected_footprint, \
        f"Incorrect footprint: expected '{expected_footprint}', got '{footprint}'"

def test_error_handling():
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"