import pytest
from pathlib import Path
from skidl import Circuit, Part, generate_schematic, SubCircuit
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Get the path to the reference schematics directory
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"

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
def resistor_circuit():
    """Create a resistor circuit for testing"""
    r = Part("Device", "R", ref="R1", value="2.2k", 
             footprint="R_0603_1608Metric")

def get_property_value(props, prop_name):
    """Helper function to extract property value and strip quotes"""
    for prop in props:
        if isinstance(prop, SExpr) and prop.token == 'property':
            if prop.get_attribute_value() == prop_name:
                value = prop.attributes[1] if len(prop.attributes) > 1 else None
                if value:
                    # Strip quotes if present
                    return value.strip('"')
    return None

def test_schematic_generation(temp_project_dir, schematic_parser):
    """Test generating a schematic with one resistor"""
    # Create the circuit
    resistor_circuit()

    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name="resistor",
        title="Test One Resistor Schematic"
    )

    # The schematic is generated in a subdirectory with the circuit name
    schematic_path = temp_project_dir / "resistor" / "resistor_circuit.kicad_sch"
    assert schematic_path.exists(), f"Schematic file not found at {schematic_path}"

    # Also verify the main schematic file
    main_schematic = temp_project_dir / "resistor" / "resistor.kicad_sch"
    assert main_schematic.exists(), f"Main schematic file not found at {main_schematic}"

    # Print the generated schematic content for debugging
    with open(schematic_path) as f:
        generated_content = f.read()
        print("\nGenerated schematic content:")
        print(generated_content)
        
    with open(REFERENCE_DIR / "one_resistor.kicad_sch") as f:
        reference_content = f.read()
        print("\nReference schematic content:")
        print(reference_content)
        
    # Parse both into s-expression trees
    generated_tree = schematic_parser.parse(generated_content)
    reference_tree = schematic_parser.parse(reference_content)
    
    # Compare key elements
    assert (generated_tree.find('version').get_attribute_value() == 
            reference_tree.find('version').get_attribute_value()), "Version mismatch"
            
    assert (generated_tree.find('generator').get_attribute_value() == 
            reference_tree.find('generator').get_attribute_value()), "Generator mismatch"
    
    # Verify lib_symbols section exists and contains Device:R
    gen_libs = generated_tree.find('lib_symbols')
    assert gen_libs is not None, "Missing lib_symbols section"
    
    # Find the resistor symbol
    gen_r_symbol = None
    for child in gen_libs.attributes:
        if isinstance(child, SExpr) and child.token == 'symbol':
            symbol_name = child.get_attribute_value().strip('"')
            if symbol_name == 'Device:R':
                gen_r_symbol = child
                break
    
    assert gen_r_symbol is not None, "Device:R library symbol missing"
    
    # Verify symbol instance
    symbol_instances = [child for child in generated_tree.attributes 
                       if isinstance(child, SExpr) and child.token == 'symbol']
    assert len(symbol_instances) > 0, "No symbol instances found"
    
    resistor_instance = None
    for sym in symbol_instances:
        for child in sym.attributes:
            if isinstance(child, SExpr) and child.token == 'lib_id':
                lib_id = child.get_attribute_value().strip('"')
                if lib_id == 'Device:R':
                    resistor_instance = sym
                    break
    
    assert resistor_instance is not None, "Resistor instance not found"
    
    # Verify resistor properties
    props = [child for child in resistor_instance.attributes 
             if isinstance(child, SExpr) and child.token == 'property']
    
    ref_value = get_property_value(props, 'Reference')
    assert ref_value == 'R1', f"Incorrect reference designator: got {ref_value}"
    
    value = get_property_value(props, 'Value')
    assert value == '2.2k', f"Incorrect value: got {value}"
    
    footprint = get_property_value(props, 'Footprint')
    if footprint:  # Only check if footprint is present
        assert footprint == 'R_0603_1608Metric', f"Incorrect footprint: got {footprint}"