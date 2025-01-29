import pytest
import os
import sys
import logging
import platform
from pathlib import Path
import re

from skidl import Circuit, Part, generate_schematic, SubCircuit

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)
os.environ['SKIDL_DEBUG'] = 'ALL'

# Get the path to the reference schematics directory
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
KICAD_BLANK_PROJECT_DIR = Path(__file__).parents[4] / "kicad_blank_project"

@SubCircuit
def resistor_circuit():
    """Create a resistor circuit for testing"""
    r = Part("Device", "R", ref="R1", value="2.2k", 
             footprint="R_0603_1608Metric")

def test_schematic_generation():
    """Test generating a schematic with one resistor"""
    # Create the circuit
    resistor_circuit()

    # Generate schematic
    generate_schematic(
        filepath=str(KICAD_BLANK_PROJECT_DIR),
        project_name="resistor",
        title="Test One Resistor Schematic"
    )

    # The schematic is generated in a subdirectory with the circuit name
    schematic_path = KICAD_BLANK_PROJECT_DIR / "resistor" / "resistor_circuit.kicad_sch"
    assert schematic_path.exists(), f"Schematic file not found at {schematic_path}"

    # Also verify the main schematic file
    main_schematic = KICAD_BLANK_PROJECT_DIR / "resistor" / "resistor.kicad_sch"
    assert main_schematic.exists(), f"Main schematic file not found at {main_schematic}"

    # Read the schematic file content
    with open(schematic_path, 'r') as f:
        schematic_content = f.read()

    # Verify KiCad schematic version and generator
    assert re.search(r'\(version 20231120\)', schematic_content), "Incorrect KiCad schematic version"
    assert re.search(r'\(generator "eeschema"\)', schematic_content), "Incorrect schematic generator"
    assert re.search(r'\(generator_version "8\.0"\)', schematic_content), "Incorrect generator version"

    # Verify Device:R library symbol is present
    assert re.search(r'\(lib_symbols\s*\(symbol "Device:R"', schematic_content), "Device:R library symbol missing"

    # Verify resistor properties
    assert re.search(r'\(property "Reference" "R1"', schematic_content), "Incorrect reference designator"
    assert re.search(r'\(property "Value" "2\.2k"', schematic_content), "Incorrect resistor value"
    assert re.search(r'\(property "Footprint" "R_0603_1608Metric"', schematic_content), "Incorrect footprint"

    # Print paths for debugging
    print(f"Generated circuit schematic at: {schematic_path}")
    print(f"Generated main schematic at: {main_schematic}")
