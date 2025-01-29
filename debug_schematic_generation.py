from skidl import *

@SubCircuit
def resistor():
    r = Part("Device", "R", footprint="R_0603_1608Metric", value="2.2k")

resistor()

generate_schematic()