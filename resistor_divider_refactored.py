# -*- coding: utf-8 -*-

from skidl import *


@subcircuit
def resistor_divider(vin, vout, gnd):
    # Components
    c10 = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0603_1608Metric")
    r9 = Part("Device", "R", value="2k", footprint="Resistor_SMD:R_0603_1608Metric") 
    r10 = Part("Device", "R", value="1k", footprint="Resistor_SMD:R_0603_1608Metric")

    # Connections
    vin += r9[1]
    vout += c10[1], r10[1], r9[2] 
    gnd += c10[2], r10[2]