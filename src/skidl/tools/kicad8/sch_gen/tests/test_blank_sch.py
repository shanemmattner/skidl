# file: tests/test_blank_sch.py
import os
from pathlib import Path
import pytest

from .conftest import parse_schematic_symbols, compare_symbol_dicts
from .fakeskidl import Circuit
from src.skidl.tools.kicad8.sch_gen.gen_schematic_v8 import gen_schematic

def test_generate_blank_schematic(output_dir):
    # Create an empty circuit: no parts => blank schematic
    c = Circuit()

    # Generate schematic
    gen_schematic(
        circuit=c,
        filepath=output_dir,
        project_name="blank_generated",
        title="Blank Schematic"
    )

    # The generator should produce <project_name>/<project_name>.kicad_sch
    generated_sch = output_dir / "blank_generated" / "blank_generated.kicad_sch"
    assert generated_sch.exists(), f"No schematic generated at {generated_sch}"

    # Compare with reference
    ref_file = Path(__file__).parent / "reference_schematics" / "blank_schematic.kicad_sch"
    assert ref_file.exists(), f"Reference file not found: {ref_file}"

    generated_symbols = parse_schematic_symbols(generated_sch)
    reference_symbols = parse_schematic_symbols(ref_file)
    compare_symbol_dicts(generated_symbols, reference_symbols)
    print("test_generate_blank_schematic passed!")
