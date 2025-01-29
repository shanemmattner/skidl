# file: tests/conftest.py

import pytest
import os
from pathlib import Path

try:
    import kiutils
    from kiutils.schematic import Schematic
    KIUTILS_AVAILABLE = True
except ImportError:
    KIUTILS_AVAILABLE = False

@pytest.fixture
def output_dir(tmp_path):
    """
    A pytest fixture that returns a fresh temp directory for each test.
    """
    return tmp_path

def parse_schematic_symbols(sch_file):
    """Use kiutils to parse a .kicad_sch and return {ref: {lib_id, value, pin_count}}."""
    if not KIUTILS_AVAILABLE:
        raise RuntimeError("kiutils not installed; cannot parse .kicad_sch files.")

    schematic = Schematic.from_file(str(sch_file))
    found_symbols = {}
    for sym in schematic.symbols:
        ref = sym.properties.get("Reference", "")
        val = sym.properties.get("Value", "")
        lib_id = sym.libId
        pin_count = len(sym.pins)
        found_symbols[ref] = {
            "lib_id": lib_id,
            "value": val,
            "pin_count": pin_count,
        }
    return found_symbols

def compare_symbol_dicts(generated_symbols, reference_symbols):
    """Compare two {ref: {lib_id, value, pin_count}} dicts ignoring positions."""
    assert len(generated_symbols) == len(reference_symbols), (
        f"Symbol count mismatch. "
        f"Generated={len(generated_symbols)}, Reference={len(reference_symbols)}"
    )

    for ref, gen_info in generated_symbols.items():
        assert ref in reference_symbols, f"Generated part {ref} not found in reference."
        ref_info = reference_symbols[ref]

        # Compare only the symbol name portion if library paths differ.
        gen_symname = gen_info["lib_id"].split(":", 1)[-1]
        ref_symname = ref_info["lib_id"].split(":", 1)[-1]
        assert gen_symname == ref_symname, (
            f"Symbol mismatch for {ref}. Generated={gen_symname}, Reference={ref_symname}"
        )

        # Compare value
        assert gen_info["value"] == ref_info["value"], (
            f"Value mismatch for {ref}. Gen={gen_info['value']}, Ref={ref_info['value']}"
        )

        # Compare pin counts
        assert gen_info["pin_count"] == ref_info["pin_count"], (
            f"Pin count mismatch for {ref}. Gen={gen_info['pin_count']}, Ref={ref_info['pin_count']}"
        )
