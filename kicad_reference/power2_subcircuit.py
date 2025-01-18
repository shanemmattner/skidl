@subcircuit
def power2(pwr_net):
    """Create a power2 subcircuit"""
    # Create power nets
    vcc_3v3 = Net('+3V3')
    vcc_3v3.drive = POWER
    
    # Create components
    u1 = Part("Regulator_Linear", "NCP1117-3.3_SOT223", footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    c2 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c1 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')

    # Connect power input side
    pwr_net & c1 & gnd
    pwr_net += u1['VI']
    
    # Connect power output side
    u1['VO'] += vcc_3v3
    vcc_3v3 & c2 & gnd
    
    # Connect ground
    u1['GND'] += gnd
    
    return vcc_3v3