import pytest
import logging
import json
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
    """Create a test circuit with R, L, and C components."""
    r = Part("Device", "R_Small", ref="R1")
    l = Part("Device", "L_Small", ref="L1")
    c = Part("Device", "C_Small", ref="C1")

def get_rlc_properties(instance_sexpr):
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
                logger.debug("Found property: %s = %s", prop_name, prop_value)
    return properties

def verify_rlc_properties(properties, ref, expected_value):
    logger.debug("Verifying properties for %s: %s", ref, properties)
    assert properties['Reference'] == ref, \
        f"Reference mismatch for {ref}: got {properties['Reference']}"
    assert properties['Value'] == expected_value, \
        f"Value mismatch for {ref}: expected {expected_value}, got {properties['Value']}"

def test_rlc_parts_schematic(temp_project_dir, schematic_parser):
    """Test generating a schematic with RLC components."""
    rlc_parts_circuit()
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="RLC Parts Test"
    )
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "rlc_parts_circuit.kicad_sch"
    assert schematic_path.exists(), f"Circuit schematic not generated at {schematic_path}"
    project_file = temp_project_dir / TEST_PROJECT_NAME / f"{TEST_PROJECT_NAME}.kicad_pro"
    assert project_file.exists(), f"Project file not generated at {project_file}"
    with open(project_file) as f:
        project_data = json.loads(f.read())
        logger.debug("Generated project file content:\n%s", json.dumps(project_data, indent=2))
    validate_kicad_pro_structure(project_data)
    validate_kicad_pro_content(project_data, TEST_PROJECT_NAME)
    with open(schematic_path) as f:
        generated_content = f.read()
        logger.debug("Generated schematic content:\n%s", generated_content)
    generated_tree = schematic_parser.parse(generated_content)
    rlc_instances = {}
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
        is_rlc = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and
                prop.token == 'lib_id' and
                prop.get_attribute_value().strip('"') in ['Device:R_Small', 'Device:L_Small', 'Device:C_Small']):
                is_rlc = True
                break
        if is_rlc:
            properties = get_rlc_properties(child)
            if 'Reference' in properties:
                rlc_instances[properties['Reference']] = properties
    expected_refs = {"R1", "L1", "C1"}
    found_refs = set(rlc_instances.keys())
    assert found_refs == expected_refs, \
        f"Missing RLC component: expected {expected_refs}, found {found_refs}"
    for ref in expected_refs:
        assert ref in rlc_instances, f"RLC component {ref} not found in schematic"
        verify_rlc_properties(rlc_instances[ref], ref, "R_Small" if ref == "R1" else "L_Small" if ref == "L1" else "C_Small")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"