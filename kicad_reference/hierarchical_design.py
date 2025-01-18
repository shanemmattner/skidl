from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def resistor_divider(pwr_net):
    """Create a voltage divider subcircuit"""
    # Create resistors
    r1 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')
    r2 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')
    
    # Create internal connection node
    div_node = Net('R1_2-R2_1')
    
    # Connect the resistors
    pwr_net & r1 & div_node & r2 & gnd
    
    # Return just the divider node, not all locals
    return div_node

@subcircuit
def power2(vin):
    """Create a power regulation subcircuit"""
    # Create power nets
    vcc_3v3 = Net('+3V3')
    vcc_3v3.drive = POWER
    
    # Create components
    c1 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c2 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    u1 = Part("Regulator_Linear", "NCP1117-3.3_SOT223", footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    
    # Connect power input side
    vin & c1 & gnd
    vin += u1['VI']
    
    # Connect power output side
    u1['VO'] += vcc_3v3
    vcc_3v3 & c2 & gnd
    
    # Connect ground
    u1['GND'] += gnd
    
    return vcc_3v3

# Instantiate the power nets
vcc_5v = Net('+5V')
vcc_5v.drive = POWER

# Instantiate the subcircuits
vcc_3v3 = power2(vcc_5v)
div_node = resistor_divider(vcc_3v3)


# Generate netlist
generate_netlist()