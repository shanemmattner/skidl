# file: tests/test_one_resistor.py
import os
from pathlib import Path
import pytest

from .conftest import parse_schematic_symbols, compare_symbol_dicts
from .fakeskidl import Circuit, Part
from src.skidl.tools.kicad8.sch_gen.gen_schematic_v8 import gen_schematic

def test_generate_one_resistor(output_dir):
    c = Circuit()
    # Add one resistor
    r4 = Part("Device", "R", "R4", "10k", footprint="Resistor_SMD:R_0603_1608Metric")
    c.add_part(r4)

    gen_schematic(
        circuit=c,
        filepath=output_dir,
        project_name="one_resistor_generated",
        title="One Resistor Test"
    )

    generated_sch = output_dir / "one_resistor_generated" / "one_resistor_generated.kicad_sch"
    assert generated_sch.exists(), "No schematic file was generated."

    ref_file = Path(__file__).parent / "reference_schematics" / "one_resistor.kicad_sch"
    assert ref_file.exists(), f"Reference file not found: {ref_file}"

    generated_symbols = parse_schematic_symbols(generated_sch)
    reference_symbols = parse_schematic_symbols(ref_file)
    compare_symbol_dicts(generated_symbols, reference_symbols)
    print("test_generate_one_resistor passed!")
