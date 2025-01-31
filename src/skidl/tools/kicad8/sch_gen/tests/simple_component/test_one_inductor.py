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
TEST_PROJECT_NAME = "test_one_inductor"

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
def one_inductor_circuit():
    """Create a test circuit with one inductor."""
    ind = Part("Device", "L_Small", ref="L1")

def get_inductor_properties(instance_sexpr):
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
                logger.debug("Found property: %s = %s", prop_name, prop_value)
    return properties

def verify_inductor_properties(properties, ref, expected_value):
    logger.debug("Verifying properties for %s: %s", ref, properties)
    assert properties['Reference'] == ref, \
        f"Reference mismatch for {ref}: got {properties['Reference']}"
    assert properties['Value'] == expected_value, \
        f"Value mismatch for {ref}: expected {expected_value}, got {properties['Value']}"

def test_one_inductor_schematic(temp_project_dir, schematic_parser):
    """Test generating a schematic with one inductor."""
    one_inductor_circuit()
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="One Inductor Test"
    )
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "one_inductor_circuit.kicad_sch"
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
    ind_instances = {}
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
        is_ind = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and
                prop.token == 'lib_id' and
                prop.get_attribute_value().strip('"') == 'Device:L_Small'):
                is_ind = True
                break
        if is_ind:
            properties = get_inductor_properties(child)
            if 'Reference' in properties:
                ind_instances[properties['Reference']] = properties
    expected_refs = {"L1"}
    found_refs = set(ind_instances.keys())
    assert found_refs == expected_refs, \
        f"Missing inductor: expected {expected_refs}, found {found_refs}"
    for ref in expected_refs:
        assert ref in ind_instances, f"Inductor {ref} not found in schematic"
        verify_inductor_properties(ind_instances[ref], ref, "L_Small")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"