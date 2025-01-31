"""Test symbol property handling in schematic generation."""

import os
import pytest
from ..kicad_writer import KicadSchematicWriter, SchematicSymbolInstance
from skidl import Part, KICAD8

def test_regulator_properties(tmp_path):
    """Test that regulator symbol properties are correctly preserved."""
    # Create output directory
    out_dir = tmp_path / "test_output"
    out_dir.mkdir()
    sch_file = out_dir / "test.kicad_sch"

    # Create schematic writer
    writer = KicadSchematicWriter(str(sch_file))

    # Create a regulator instance
    inst = SchematicSymbolInstance(
        lib_id="Regulator_Linear:NCP1117-3.3_SOT223",
        reference="U1",
        value="NCP1117-3.3_SOT223",
        position=(0.0, 0.0),
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    writer.add_symbol_instance(inst)

    # Generate schematic
    writer.generate()

    # Read generated file
    with open(sch_file) as f:
        content = f.read()

    # Verify properties
    assert 'property "Reference" "U"' in content
    assert 'property "Value" "NCP1117-3.3_SOT223"' in content
    assert 'property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2"' in content
    assert 'property "Description" "1A Low drop-out regulator, Fixed Output 3.3V, SOT-223"' in content
    assert 'property "ki_keywords" "REGULATOR LDO 3.3V"' in content

def test_resistor_properties(tmp_path):
    """Test that resistor symbol properties are correctly preserved."""
    # Create output directory
    out_dir = tmp_path / "test_output"
    out_dir.mkdir()
    sch_file = out_dir / "test.kicad_sch"

    # Create schematic writer
    writer = KicadSchematicWriter(str(sch_file))

    # Create a resistor instance
    inst = SchematicSymbolInstance(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(0.0, 0.0),
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    writer.add_symbol_instance(inst)

    # Generate schematic
    writer.generate()

    # Read generated file
    with open(sch_file) as f:
        content = f.read()

    # Verify properties
    assert 'property "Reference" "R"' in content
    assert 'property "Value" "10k"' in content
    assert 'property "Footprint" "Resistor_SMD:R_0603_1608Metric"' in content
    assert 'property "Description" "Resistor"' in content
    assert 'property "ki_keywords" "R res resistor"' in content