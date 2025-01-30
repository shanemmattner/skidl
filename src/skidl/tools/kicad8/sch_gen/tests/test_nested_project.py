import pytest
import logging
from pathlib import Path
from skidl import *
from skidl.tools.kicad8.sch_gen.sexpr import SchematicParser, SExpr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
TESTS_DIR = Path(__file__).parent
REFERENCE_DIR = TESTS_DIR / "reference_schematics"
TEST_PROJECT_NAME = "test_nested_project"

@pytest.fixture(autouse=True)
def setup_circuit():
    """Reset the circuit before and after each test to ensure a clean state."""
    Circuit.reset(default_circuit)
    yield
    Circuit.reset(default_circuit)

@pytest.fixture
def schematic_parser():
    """Provide a SchematicParser instance for parsing KiCad schematics."""
    return SchematicParser()

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary directory for the project to ensure test isolation."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

@SubCircuit
def single_resistor():
    """Create a sheet with one resistor."""
    r1 = Part("Device", "R", 
              ref="R1",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r1.MFG = "0603WAF1002T5E"

@SubCircuit
def two_resistors_circuit():
    """Create a sheet with two resistors."""
    r1 = Part("Device", "R", 
              ref="R2",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r1.MFG = "0603WAF1002T5E"
    
    r2 = Part("Device", "R", 
              ref="R3",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r2.MFG = "0603WAF1002T5E"

def get_resistor_properties(instance_sexpr):
    """Extract resistor properties from a symbol instance s-expression."""
    properties = {}
    for child in instance_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if len(child.attributes) > 1:
                prop_value = child.attributes[1].strip('"')
                properties[prop_name] = prop_value
                logger.debug("Found property: %s = %s", prop_name, prop_value)
    return properties

def verify_resistor_properties(properties, ref, expected_value):
    """Verify that a resistor's properties match expected values."""
    logger.debug("Verifying properties for %s: %s", ref, properties)
    
    assert properties['Reference'] == ref, \
        f"Reference mismatch for {ref}: got {properties['Reference']}"
    assert properties['Value'] == expected_value, \
        f"Value mismatch for {ref}: expected {expected_value}, got {properties['Value']}"
    
    if 'Footprint' in properties:
        footprint = properties['Footprint']
        expected_footprint = "Resistor_SMD:R_0603_1608Metric"
        assert footprint == expected_footprint, \
            f"Footprint mismatch for {ref}: expected '{expected_footprint}', got '{footprint}'"

def verify_sheet_properties(sheet_sexpr, expected_name, expected_file):
    """Verify that a sheet's properties match expected values."""
    logger.debug("Verifying sheet properties for expected name: %s", expected_name)
    sheet_name = None
    sheet_file = None
    
    for child in sheet_sexpr.attributes:
        if isinstance(child, SExpr) and child.token == 'property':
            prop_name = child.get_attribute_value()
            if prop_name == 'Sheetname':
                sheet_name = child.attributes[1].strip('"') if len(child.attributes) > 1 else None
                logger.debug("Found sheet name: %s", sheet_name)
            elif prop_name == 'Sheetfile':
                sheet_file = child.attributes[1].strip('"') if len(child.attributes) > 1 else None
                logger.debug("Found sheet file: %s", sheet_file)
    
    assert sheet_name == expected_name, \
        f"Sheet name mismatch: expected '{expected_name}', got '{sheet_name}'"
    assert sheet_file == expected_file, \
        f"Sheet file mismatch: expected '{expected_file}', got '{sheet_file}'"

def verify_sheet_schematic(schematic_path, expected_refs):
    """Verify the contents of a sheet schematic file."""
    assert schematic_path.exists(), f"Sheet schematic not found at {schematic_path}"
    
    with open(schematic_path) as f:
        content = f.read()
        logger.debug("Sheet content:\n%s", content)
    
    tree = SchematicParser().parse(content)
    resistor_instances = {}
    
    for child in tree.attributes:
        if not isinstance(child, SExpr) or child.token != 'symbol':
            continue
            
        for prop in child.attributes:
            if (isinstance(prop, SExpr) and 
                prop.token == 'lib_id' and 
                prop.get_attribute_value().strip('"') == 'Device:R'):
                properties = get_resistor_properties(child)
                if 'Reference' in properties:
                    resistor_instances[properties['Reference']] = properties
                break
    
    found_refs = set(resistor_instances.keys())
    assert found_refs == expected_refs, \
        f"Resistor references mismatch in {schematic_path.name}: expected {expected_refs}, found {found_refs}"
    
    for ref in expected_refs:
        verify_resistor_properties(resistor_instances[ref], ref, "10k")

def test_nested_project_schematic(temp_project_dir, schematic_parser):
    """Test generating a hierarchical schematic with nested sheets."""
    # Create both subcircuits
    single_resistor()
    two_resistors_circuit()
    
    # Generate schematic
    generate_schematic(
        filepath=str(temp_project_dir),
        project_name=TEST_PROJECT_NAME,
        title="Nested Project Test"
    )

    # Verify main schematic path
    main_schematic_path = temp_project_dir / TEST_PROJECT_NAME / f"{TEST_PROJECT_NAME}.kicad_sch"
    assert main_schematic_path.exists(), f"Main schematic not generated at {main_schematic_path}"

    # Parse main schematic
    with open(main_schematic_path) as f:
        main_content = f.read()
        logger.debug("Main schematic content:\n%s", main_content)

    main_tree = schematic_parser.parse(main_content)
    sheets = []
    
    # Find all sheets
    for child in main_tree.attributes:
        if isinstance(child, SExpr) and child.token == 'sheet':
            sheets.append(child)
            logger.debug("Found sheet: %s", child)

    # Verify both sheets are present
    assert len(sheets) == 2, "Expected 2 sheets in main schematic"
    
    # Expected sheet configurations
    expected_sheets = [
        ("single_resistor", "single_resistor.kicad_sch"),
        ("two_resistors_circuit", "two_resistors_circuit.kicad_sch")
    ]
    
    # Verify each sheet's properties
    for i, (sheet_name, sheet_file) in enumerate(expected_sheets):
        verify_sheet_properties(sheets[i], sheet_name, sheet_file)
        
        # Verify the sheet's schematic contents
        sheet_path = temp_project_dir / TEST_PROJECT_NAME / sheet_file
        if sheet_name == "single_resistor":
            expected_refs = {"R1"}
        else:  # two_resistors_circuit
            expected_refs = {"R2", "R3"}
            
        verify_sheet_schematic(sheet_path, expected_refs)

def test_error_handling():
    """Test error handling for invalid library access."""
    with pytest.raises(Exception) as exc_info:
        Part("NonexistentLib", "NonexistentPart")
    assert "NonexistentLib" in str(exc_info.value), \
        "Error message should mention the nonexistent library name"