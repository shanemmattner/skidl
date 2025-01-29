# src/skidl/tools/kicad8/sch_gen/tests/test_blank_sch.py

import os
import pytest
from pathlib import Path
import uuid
import re
from kiutils.schematic import Schematic
from skidl.tools.kicad8.sch_gen import gen_schematic
from skidl import Circuit

# Get the path to the reference_schematics directory relative to this test file
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"

@pytest.fixture
def reference_schematic():
    """Load the reference blank schematic"""
    ref_path = REFERENCE_DIR / "blank_schematic.kicad_sch"
    assert ref_path.exists(), f"Reference schematic not found at {ref_path}"
    return Schematic.from_file(str(ref_path))

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

def normalize_schematic_content(content: str) -> str:
    """
    Normalize schematic content for comparison by:
    1. Removing UUIDs which will be different each time
    2. Normalizing whitespace
    3. Removing generator version which isn't supported by kiutils
    """
    # Remove UUIDs
    content = re.sub(r'uuid "[^"]+"', 'uuid "NORMALIZED"', content)
    
    # Remove generator version
    content = re.sub(r'\(generator_version "[^"]+"\)\s*', '', content)
    
    # Normalize generator
    content = re.sub(r'\(generator "?eeschema"?\)', '(generator "eeschema")', content)
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\( ', '(', content)
    content = re.sub(r' \)', ')', content)
    
    # Remove any leading/trailing whitespace
    content = content.strip()
    
    return content

def test_blank_schematic_generation(temp_project_dir, reference_schematic):
    """
    Test that gen_schematic() generates a blank schematic matching our reference.
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
    
    # Load generated schematic
    generated_schematic = Schematic.from_file(str(generated_path))
    
    # Compare key attributes
    assert str(generated_schematic.version) == "20231120", \
        f"Version mismatch: got {generated_schematic.version}, expected 20231120"
    
    assert generated_schematic.paper == reference_schematic.paper, \
        f"Paper size mismatch: got {generated_schematic.paper}, expected {reference_schematic.paper}"
    
    # Verify lib_symbols exists and is empty
    assert hasattr(generated_schematic, 'libSymbols'), "Missing libSymbols section"
    assert len(generated_schematic.libSymbols) == 0, "libSymbols should be empty"
    
    # Compare raw content with normalization
    with open(generated_path) as f:
        generated_content = f.read()
    with open(REFERENCE_DIR / "blank_schematic.kicad_sch") as f:
        reference_content = f.read()
        
    normalized_generated = normalize_schematic_content(generated_content)
    normalized_reference = normalize_schematic_content(reference_content)
    
    assert normalized_generated == normalized_reference, \
        "Generated schematic content does not match reference"

def test_schematic_metadata(temp_project_dir):
    """
    Test that generated schematic has correct metadata
    """
    circuit = Circuit()
    
    # Generate schematic with specific metadata
    test_title = "Test Schematic"
    gen_schematic(
        circuit=circuit,
        filepath=str(temp_project_dir),
        project_name="test_meta",
        title=test_title
    )
    
    generated_path = temp_project_dir / "test_meta" / "test_meta.kicad_sch"
    schematic = Schematic.from_file(str(generated_path))
    
    # Verify metadata (only what kiutils actually supports)
    assert str(schematic.version) == "20231120", "Incorrect schematic version"
    assert schematic.generator == "eeschema", "Incorrect generator"
    assert schematic.paper == "A4", "Incorrect paper size"

def test_project_directory_structure(temp_project_dir):
    """
    Test that gen_schematic creates correct project directory structure
    """
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
    
  