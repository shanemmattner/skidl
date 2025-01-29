import skidl
from skidl import Part, generate_schematic
import os

def test_single_resistor():
    """Test generating a schematic with a single resistor."""
    
    # Reset circuit to avoid conflicts with other tests
    skidl.reset()

    # Create a resistor component
    r1 = Part("Device", "R", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")

    # Assertions: Ensure the resistor is correctly configured
    assert r1.ref.startswith("R")
    assert r1.value == "10k"
    assert r1.footprint == "Resistor_SMD:R_0603_1608Metric"

    # Generate schematic file
    output_file = "test_single_resistor.kicad_sch"
    generate_schematic(output_file)

    # Verify file is created
    assert os.path.exists(output_file)

    # Cleanup: Remove generated file
    os.remove(output_file)
