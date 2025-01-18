@subcircuit
def resistor_divider(pwr_net):
    """Create a resistor_divider subcircuit"""
    # Create components
    r2 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')
    r1 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')

    # Create internal connection node
    r1_2_r2_1 = Net('R1_2-R2_1')

    # Connect the components
    pwr_net & r1 & r1_2_r2_1 & r2 & gnd

    # Return just the divider node, not all locals
    return r1_2_r2_1