import skidl
from skidl import Part, generate_schematic
import os

def test_two_resistors():
    """Test generating a schematic with two resistors."""

    skidl.reset()  # Reset circuit

    r1 = Part("Device", "R", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Part("Device", "R", value="1k", footprint="Resistor_SMD:R_0603_1608Metric")

    assert r1.ref.startswith("R")
    assert r2.ref.startswith("R")
    assert r1.value == "10k"
    assert r2.value == "1k"

    output_file = "test_two_resistors.kicad_sch"
    generate_schematic(output_file)

    assert os.path.exists(output_file)
    os.remove(output_file)
