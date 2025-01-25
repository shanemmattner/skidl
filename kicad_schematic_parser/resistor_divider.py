@subcircuit
def circuit(vin, vout):
    # Create components
    c10 = Part('Device', 'C', value='100nF')
    r10 = Part('Device', 'R', value='1k')
    r9 = Part('Device', 'R', value='2k')

    # Connect nets
    c10[2] += r10[2], GND
    r9[1] += vin
    c10[1] += r10[1], r9[2], vout