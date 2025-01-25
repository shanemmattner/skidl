# -*- coding: utf-8 -*-
from skidl import *

@subcircuit
def 3v3_regulator(3v3_monitor, 5v_monitor, gnd, net_3v3, net_5v):
    # Components
    c2 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c3 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c5 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c9 = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    r2 = Part('Device', 'R', value='2k', footprint='Resistor_SMD:R_0603_1608Metric')
    r3 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric')
    r7 = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric')
    r8 = Part('Device', 'R', value='2k', footprint='Resistor_SMD:R_0603_1608Metric')
    u1 = Part('Regulator_Linear', 'NCP1117-3.3_SOT223', value='NCP1117-3.3_SOT223', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')

    # Connections
    net_3v3 += c2['1'], r8['1'], u1['2']
    net_5v += c3['1'], r2['1'], u1['3']
    3v3_monitor += c5['1'], r3['1'], r8['2']
    5v_monitor += c9['1'], r2['2'], r7['1']
    gnd += c2['2'], c3['2'], c5['2'], c9['2'], r3['2'], r7['2'], u1['1']
