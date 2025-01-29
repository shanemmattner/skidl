# file: tests/test_two_resistors.py
import os
from pathlib import Path
import pytest

from .conftest import parse_schematic_symbols, compare_symbol_dicts
from .fakeskidl import Circuit, Part
from src.skidl.tools.kicad8.sch_gen.gen_schematic_v8 import gen_schematic

def test_generate_two_resistors(output_dir):
    c = Circuit()
    r4 = Part("Device", "R", "R4", "10k", "Resistor_SMD:R_0603_1608Metric")
    r5 = Part("Device", "R", "R5", "10k", "Resistor_SMD:R_0603_1608Metric")
    c.add_part(r4)
    c.add_part(r5)

    gen_schematic(
        circuit=c,
        filepath=output_dir,
        project_name="two_resistors_generated",
        title="Two Resistors Test"
    )

    generated_sch = output_dir / "two_resistors_generated" / "two_resistors_generated.kicad_sch"
    assert generated_sch.exists(), "No schematic file was generated."

    ref_file = Path(__file__).parent / "reference_schematics" / "two_resistors.kicad_sch"
    assert ref_file.exists(), f"Reference file not found: {ref_file}"

    generated_symbols = parse_schematic_symbols(generated_sch)
    reference_symbols = parse_schematic_symbols(ref_file)
    compare_symbol_dicts(generated_symbols, reference_symbols)
    print("test_generate_two_resistors passed!")
