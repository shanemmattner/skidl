# src/skidl/tools/kicad8/sch_gen/tests/test_blank_sch.py

import pytest
from pathlib import Path
from skidl.tools.kicad8.sch_gen import gen_schematic
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr
from skidl import Circuit

# Get the path to the reference_schematics directory relative to this test file
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"

@pytest.fixture
def schematic_parser():
    """Fixture to provide SchematicParser instance"""
    return SchematicParser()

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project"""
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
    assert generated_path.exists(), "Generated schematic file not found"
    
    # Load and parse both schematics
    with open(generated_path) as f:
        generated_content = f.read()
    with open(REFERENCE_DIR / "blank_schematic.kicad_sch") as f:
        reference_content = f.read()
        
    # Parse both into s-expression trees
    generated_tree = schematic_parser.parse(generated_content)
    reference_tree = schematic_parser.parse(reference_content)
    
    # Compare key elements using normalized attribute values
    assert (generated_tree.find('version').get_attribute_value() == 
            reference_tree.find('version').get_attribute_value()), "Version mismatch"
            
    assert (generated_tree.find('generator').get_attribute_value() == 
            reference_tree.find('generator').get_attribute_value()), "Generator mismatch"
            
    # Compare paper size
    assert (generated_tree.find('paper').get_attribute_value() == 
            reference_tree.find('paper').get_attribute_value()), "Paper size mismatch"
            
    # Verify lib_symbols exists and is empty
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section"
    assert not gen_libs.attributes, "lib_symbols should be empty"

def test_schematic_structure(temp_project_dir, schematic_parser):
    """Test schematic has all required high-level sections"""
    circuit = Circuit()
    
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name="test_structure",
        title="Test Schematic Structure"
    )
    
    generated_path = temp_project_dir / "test_structure" / "test_structure.kicad_sch"
    
    # Load and parse schematic
    with open(generated_path) as f:
        content = f.read()
    
    tree = schematic_parser.parse(content)
    
    # Check required sections exist
    assert tree.find('version') is not None, "Missing version"
    assert tree.find('generator') is not None, "Missing generator"
    assert tree.find('paper') is not None, "Missing paper size"
    assert tree.find('lib_symbols') is not None, "Missing lib_symbols"

def test_project_directory_structure(temp_project_dir):
    """Test that gen_schematic creates correct project directory structure"""
    circuit = Circuit()
    project_name = "test_structure"
    
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name=project_name
    )
    
    project_dir = temp_project_dir / project_name
    
    # Verify project directory was created
    assert project_dir.is_dir(), "Project directory not created"
    
    # Verify schematic file exists
    assert (project_dir / f"{project_name}.kicad_sch").exists(), \
        "Main schematic file not created"