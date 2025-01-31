from skidl import *

@SubCircuit
def single_resistor():
    """Create a sheet with one resistor."""
    r1 = Part("Device", "R", 
              ref="R1",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r1.MFG = "0603WAF1002T5E"
    two_resistors_circuit()

@SubCircuit
def two_resistors_circuit():
    """Create a sheet with two resistors."""
    r2 = Part("Device", "R", 
              ref="R2",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r2.MFG = "0603WAF1002T5E"
    
    r3 = Part("Device", "R", 
              ref="R3",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r3.MFG = "0603WAF1002T5E"

single_resistor()

generate_schematic(
    filepath="hierachy_test",
    project_name="testing_hierarchy", 
    title="Test 2 Resistor Schematic"
)