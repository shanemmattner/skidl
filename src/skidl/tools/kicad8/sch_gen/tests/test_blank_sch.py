import pytest
import logging
from pathlib import Path
from skidl import *
from skidl import Circuit
from skidl.tools.kicad8.sch_gen import gen_schematic
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the path to the reference_schematics directory relative to this test file
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
    """Provide a SchematicParser instance for schematic file parsing."""
    return SchematicParser()

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project to ensure test isolation."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

def test_blank_schematic_generation(temp_project_dir, schematic_parser):
    """
    Test that gen_schematic() generates a blank schematic matching our reference.
    Uses s-expression parsing for resilient comparison.
    """
    # Create empty circuit
    circuit = Circuit()
    
    # Generate schematic
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name="test_blank",
        title="Test Blank Schematic"
    )
    
    # Path to generated schematic
    generated_path = temp_project_dir / "test_blank" / "test_blank.kicad_sch"
    
    # Verify file was created
    assert generated_path.exists(), f"Generated schematic file not found at {generated_path}"
    
    # Load and parse both schematics
    with open(generated_path) as f:
        generated_content = f.read()
    with open(REFERENCE_DIR / "blank_schematic.kicad_sch") as f:
        reference_content = f.read()
        
    logger.debug("Generated schematic content:\n%s", generated_content)
    
    # Parse both into s-expression trees
    generated_tree = schematic_parser.parse(generated_content)
    reference_tree = schematic_parser.parse(reference_content)
    
    # Compare key elements using normalized attribute values
    version_match = (generated_tree.find('version').get_attribute_value() == 
                    reference_tree.find('version').get_attribute_value())
    assert version_match, "Generated schematic version does not match reference version"
            
    generator_match = (generated_tree.find('generator').get_attribute_value() == 
                      reference_tree.find('generator').get_attribute_value())
    assert generator_match, "Generated schematic generator does not match reference generator"
            
    # Compare paper size
    paper_match = (generated_tree.find('paper').get_attribute_value() == 
                  reference_tree.find('paper').get_attribute_value())
    assert paper_match, "Generated schematic paper size does not match reference"
            
    # Verify lib_symbols exists and is empty
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Generated schematic is missing required lib_symbols section"
    assert not gen_libs.attributes, "lib_symbols section should be empty in blank schematic"

def test_schematic_metadata(temp_project_dir):
    """
    Test that generated schematic contains correct metadata including
    version, generator info, and paper size.
    """
    circuit = Circuit()
    test_title = "Test Schematic"
    
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name="test_meta",
        title=test_title
    )
    
    generated_path = temp_project_dir / "test_meta" / "test_meta.kicad_sch"
    assert generated_path.exists(), f"Schematic file not generated at {generated_path}"
    
    # Parse and verify metadata
    with open(generated_path) as f:
        content = f.read()
    tree = SchematicParser().parse(content)
    
    assert str(tree.find('version').get_attribute_value()) == "20231120", \
        "Incorrect schematic version"
    assert tree.find('generator').get_attribute_value() == "eeschema", \
        "Incorrect generator"
    assert tree.find('paper').get_attribute_value() == "A4", \
        "Incorrect paper size"

def test_project_directory_structure(temp_project_dir):
    """
    Test that gen_schematic creates the expected project directory structure
    with all necessary files.
    """
    circuit = Circuit()
    project_name = "test_structure"
    
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name=project_name
    )
    
    project_dir = temp_project_dir / project_name
    
    # Verify project directory structure
    assert project_dir.is_dir(), \
        f"Project directory not created at {project_dir}"
    assert (project_dir / f"{project_name}.kicad_sch").exists(), \
        f"Main schematic file not created at {project_dir / f'{project_name}.kicad_sch'}"