from skidl import *
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@SubCircuit
def single_resistor():
    """Create a sheet with one resistor."""
    logging.debug("\nCreating single_resistor circuit")
    r1 = Part("Device", "R", 
              ref="R1",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r1.MFG = "0603WAF1002T5E"
    logging.debug(f"Created resistor R1 with hierarchy: {getattr(r1, 'hierarchy', 'unknown')}")
    
    logging.debug("Calling two_resistors_circuit from single_resistor")
    two_resistors_circuit()

@SubCircuit
def two_resistors_circuit():
    """Create a sheet with two resistors."""
    logging.debug("\nCreating two_resistors_circuit")
    r2 = Part("Device", "R", 
              ref="R2",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r2.MFG = "0603WAF1002T5E"
    logging.debug(f"Created resistor R2 with hierarchy: {getattr(r2, 'hierarchy', 'unknown')}")
    
    r3 = Part("Device", "R", 
              ref="R3",
              value="10k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r3.MFG = "0603WAF1002T5E"
    logging.debug(f"Created resistor R3 with hierarchy: {getattr(r3, 'hierarchy', 'unknown')}")

logging.debug("\nStarting circuit creation")
single_resistor()


logging.debug("\nGenerating schematic")
generate_schematic(
    filepath="hierachy_test",
    project_name="testing_hierarchy", 
    title="Test 2 Resistor Schematic"
)