# -*- coding: utf-8 -*-
from skidl import *
from main import main

def create_circuit():
    # Create nets
    gnd = Net('GND')

    # Instantiate main circuit
    main()

if __name__ == "__main__":
    create_circuit()
    generate_netlist()
