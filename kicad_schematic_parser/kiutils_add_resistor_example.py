#!/usr/bin/env python3

from kiutils.schematic import Schematic
from kiutils.items.common import Position, Effects, Property, Font, Justify
from kiutils.items.schitems import SchematicSymbol, SymbolProjectInstance, SymbolProjectPath
import uuid
import sys

def add_resistor(schematic_path):
    """
    Add a 10k 0603 resistor to a KiCad schematic at position (0,0)
    
    Args:
        schematic_path (str): Path to the KiCad schematic file
    """
    # Load schematic
    schematic = Schematic().from_file(schematic_path)
    
    # Generate UUIDs
    symbol_uuid = str(uuid.uuid4())
    pin1_uuid = str(uuid.uuid4())
    pin2_uuid = str(uuid.uuid4())
    
    # Create new resistor symbol
    resistor = SchematicSymbol(
        libraryNickname="Device",
        entryName="R",
        position=Position(X=0, Y=0, angle=0),  # Added angle
        unit=1,
        inBom=True,
        onBoard=True,
        dnp=False,  # Added dnp flag
        fieldsAutoplaced=True,  # Added fields_autoplaced
        uuid=symbol_uuid,
        properties=[
            Property(
                key="Reference", 
                value="R?",
                position=Position(X=2.54, Y=-1.27, angle=0),
                effects=Effects(font=Font(height=1.27, width=1.27), justify=Justify(horizontally="left"))
            ),
            Property(
                key="Value",
                value="10k",
                position=Position(X=2.54, Y=1.27, angle=0),
                effects=Effects(font=Font(height=1.27, width=1.27), justify=Justify(horizontally="left"))
            ),
            Property(
                key="Footprint",
                value="Resistor_SMD:R_0603_1608Metric",
                position=Position(X=-1.778, Y=0, angle=90),
                effects=Effects(font=Font(height=1.27, width=1.27))
            ),
            Property(
                key="Datasheet",
                value="~",
                position=Position(X=0, Y=0, angle=0),
                effects=Effects(font=Font(height=1.27, width=1.27))
            ),
            Property(
                key="Description",
                value="Resistor",
                position=Position(X=0, Y=0, angle=0),
                effects=Effects(font=Font(height=1.27, width=1.27))
            )
        ],
        pins={
            "1": pin1_uuid,
            "2": pin2_uuid
        }
    )
    
    # Add project instance information
    project_name = schematic_path.split('/')[-1].replace('.kicad_sch', '')
    resistor.instances = [
        SymbolProjectInstance(
            name=project_name,
            paths=[
                SymbolProjectPath(
                    reference="R?",
                    unit=1
                )
            ]
        )
    ]
    
    # Add to schematic
    schematic.schematicSymbols.append(resistor)
    
    # Save changes
    schematic.to_file()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 add_resistor.py <path_to_schematic>")
        sys.exit(1)
    
    add_resistor(sys.argv[1])
    print(f"Added 10k 0603 resistor at (0,0) to {sys.argv[1]}")
