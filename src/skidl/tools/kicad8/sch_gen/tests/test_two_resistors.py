import pytest
from pathlib import Path
from skidl import Circuit, Part, generate_schematic, SubCircuit
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Constants
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
TEST_PROJECT_NAME = "test_two_resistors"

@pytest.fixture
def schematic_parser():
    """Fixture to provide SchematicParser instance"""
    return SchematicParser()

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

@SubCircuit
def two_resistors_circuit():
    """Create a circuit with two resistors for testing"""
    r4 = Part("Device", "R", 
              ref="R4",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r4.MFG = "0603WAF1002T5E"
    
    r5 = Part("Device", "R", 
              ref="R5",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r5.MFG = "0603WAF1002T5E"

def verify_resistor_properties(instance_sexpr, ref, expected_value):
    """Helper to verify resistor properties in s-expression"""
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
    
    assert properties['Reference'] == ref, f"Reference mismatch for {ref}"
    assert properties['Value'] == expected_value, f"Value mismatch for {ref}"
    assert properties['Footprint'] == "Resistor_SMD:R_0603_1608Metric", f"Footprint mismatch for {ref}"

def test_two_resistors_schematic(temp_project_dir, schematic_parser):
    """Test generating a schematic with two resistors"""
    # Create circuit with @SubCircuit decorator
    two_resistors_circuit()
    
    # Generate schematic using default circuit
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="Two Resistors Test"
    )

    # Look for the correct schematic path
    schematic_path = temp_project_dir / TEST_PROJECT_NAME / "two_resistors_circuit.kicad_sch"
    assert schematic_path.exists(), f"Schematic file not found at {schematic_path}"

    # Load and parse both the generated and reference schematics
    with open(schematic_path) as f:
        generated_content = f.read()
        print("\nGenerated schematic content:")
        print(generated_content)

    with open(REFERENCE_DIR / "two_resistors.kicad_sch") as f:
        reference_content = f.read()
        print("\nReference schematic content:")
        print(reference_content)

    generated_tree = schematic_parser.parse(generated_content)
    reference_tree = schematic_parser.parse(reference_content)

    # Verify basic properties
    assert (generated_tree.find('version').get_attribute_value() == 
            reference_tree.find('version').get_attribute_value()), "Version mismatch"

    # Verify lib_symbols section and Device:R symbol
    lib_symbols = generated_tree.find('lib_symbols')
    assert lib_symbols is not None, "Missing lib_symbols section"
    
    r_symbol = None
    for child in lib_symbols.attributes:
        if (isinstance(child, SExpr) and 
            child.token == 'symbol' and 
            child.get_attribute_value().strip('"') == 'Device:R'):
            r_symbol = child
            break
            
    assert r_symbol is not None, "Device:R symbol not found"

    # Find and verify both resistor instances
    resistor_instances = []
    for child in generated_tree.attributes:
        if (isinstance(child, SExpr) and 
            child.token == 'symbol'):
            for prop in child.attributes:
                if (isinstance(prop, SExpr) and 
                    prop.token == 'lib_id' and 
                    prop.get_attribute_value().strip('"') == 'Device:R'):
                    resistor_instances.append(child)
                    
    assert len(resistor_instances) == 2, "Expected exactly 2 resistor instances"
    
    # Verify properties of each resistor
    resistors_verified = set()
    for instance in resistor_instances:
        for prop in instance.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'property' and 
                prop.get_attribute_value() == 'Reference'):
                ref = prop.attributes[1].strip('"')
                if ref in ['R4', 'R5']:
                    verify_resistor_properties(instance, ref, "10k")
                    resistors_verified.add(ref)
                    
    assert resistors_verified == {'R4', 'R5'}, "Not all resistors were verified"

def test_error_handling(temp_project_dir):
    """Test error handling for invalid circuit configurations"""
    with pytest.raises(Exception) as exc_info:
        # Test with non-existent library
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value)