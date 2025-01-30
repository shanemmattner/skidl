import pytest
from pathlib import Path
from skidl import Circuit, Part, generate_schematic, SubCircuit
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Constants
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
TEST_PROJECT_NAME = "test_two_resistors"

@pytest.fixture(autouse=True)
def setup_circuit():
    """Reset the circuit before each test"""
    from skidl import Circuit
    Circuit.reset(default_circuit)
    yield
    Circuit.reset(default_circuit)

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

def get_resistor_properties(instance_sexpr):
    """Helper to extract resistor properties from s-expression"""
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
                
                # Debug print
                print(f"Found property: {prop_name} = {prop_value}")
    return properties

def verify_resistor_properties(properties, ref, expected_value):
    """Helper to verify resistor properties"""
    # Debug print
    print(f"\nVerifying properties for {ref}:")
    print(f"All properties: {properties}")
    
    # Required properties
    assert properties['Reference'] == ref, f"Reference mismatch for {ref}"
    assert properties['Value'] == expected_value, f"Value mismatch for {ref}"
    
    # Optional properties with more detailed error messages
    if 'Footprint' in properties:
        footprint = properties['Footprint']
        assert footprint == "Resistor_SMD:R_0603_1608Metric", \
            f"Footprint mismatch for {ref}: expected 'Resistor_SMD:R_0603_1608Metric', got '{footprint}'"
    else:
        print(f"Warning: Footprint property not found for {ref}")

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

    # Debug: Print the schematic content
    with open(schematic_path) as f:
        print("\nGenerated schematic content:")
        print(f.read())

    # Load and parse generated schematic
    with open(schematic_path) as f:
        generated_content = f.read()

    generated_tree = schematic_parser.parse(generated_content)

    # Find all resistor instances
    resistor_instances = {}  # Will store ref: properties mapping
    
    for child in generated_tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
            
        # Check if it's a resistor
        is_resistor = False
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'lib_id' and 
                prop.get_attribute_value().strip('"') == 'Device:R'):
                is_resistor = True
                break
                
        if is_resistor:
            # Get properties for this resistor
            properties = get_resistor_properties(child)
            if 'Reference' in properties:
                resistor_instances[properties['Reference']] = properties

    # Verify we found both resistors
    expected_refs = {"R4", "R5"}
    found_refs = set(resistor_instances.keys())
    assert found_refs == expected_refs, f"Expected resistors {expected_refs}, but found {found_refs}"
    
    # Verify properties of each resistor
    for ref in expected_refs:
        assert ref in resistor_instances, f"Missing resistor {ref}"
        verify_resistor_properties(resistor_instances[ref], ref, "10k")

def test_error_handling(temp_project_dir):
    """Test error handling for invalid circuit configurations"""
    with pytest.raises(Exception) as exc_info:
        # Test with non-existent library
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value)