# file: tests/test_ncp1117_3v3.py
import os
from pathlib import Path
import pytest

from .conftest import parse_schematic_symbols, compare_symbol_dicts
from .fakeskidl import Circuit, Part
from src.skidl.tools.kicad8.sch_gen.gen_schematic_v8 import gen_schematic

def test_generate_ncp1117_3v3(output_dir):
    c = Circuit()
    # Single part from "Regulator_Linear" library
    u2 = Part("Regulator_Linear", "NCP1117-3.3_SOT223", "U2", "NCP1117-3.3_SOT223",
              footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2")
    c.add_part(u2)

    gen_schematic(
        circuit=c,
        filepath=output_dir,
        project_name="ncp1117_3v3_generated",
        title="NCP1117-3.3 Test"
    )

    generated_sch = output_dir / "ncp1117_3v3_generated" / "ncp1117_3v3_generated.kicad_sch"
    assert generated_sch.exists()

    ref_file = Path(__file__).parent / "reference_schematics" / "ncp1117-3v3.kicad_sch"
    assert ref_file.exists(), f"Reference file not found: {ref_file}"

    generated_symbols = parse_schematic_symbols(generated_sch)
    reference_symbols = parse_schematic_symbols(ref_file)
    compare_symbol_dicts(generated_symbols, reference_symbols)
    print("test_generate_ncp1117_3v3 passed!")
