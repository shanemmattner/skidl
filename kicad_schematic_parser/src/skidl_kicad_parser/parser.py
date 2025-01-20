import os
from kiutils.schematic import Schematic
from .components.component_parser import get_component_pins
from .connectivity.wire_parser import get_wire_connections, get_connected_points
from .connectivity.net_parser import calculate_pin_connectivity
from .labels.label_parser import parse_labels

def parse_hierarchical_sheets(schematic, base_path):
    """
    Recursively parse hierarchical sheets and merge results into the main schematic.
    """
    all_schematics = [schematic]

    for sheet in schematic.sheets:
        sheet_file = next((prop.value for prop in sheet.properties if prop.key == "Sheetfile"), None)
        if sheet_file:
            child_path = os.path.join(base_path, sheet_file)
            try:
                child_schematic = Schematic().from_file(child_path)
                all_schematics.extend(parse_hierarchical_sheets(child_schematic, os.path.dirname(child_path)))
            except FileNotFoundError:
                print(f"Error: Unable to find hierarchical sheet file: {child_path}")

    return all_schematics

def analyze_schematic(schematic, base_path, debug=False):
    """
    Analyze schematic and generate comprehensive information about components, pins, and connectivity.
    """
    # Parse all schematics, including hierarchical ones
    all_schematics = parse_hierarchical_sheets(schematic, base_path)

    # Merge data across all schematics
    all_labels = {'local': [], 'hierarchical': [], 'power': []}
    all_wire_connections = []
    all_component_pins = {}

    for sch in all_schematics:
        labels = parse_labels(sch)
        all_labels['local'].extend(labels['local'])
        all_labels['hierarchical'].extend(labels['hierarchical'])
        all_labels['power'].extend(labels['power'])

        all_wire_connections.extend(get_wire_connections(sch))

        component_pins = get_component_pins(sch)
        all_component_pins.update(component_pins)

    # Generate netlist with debug info
    if debug:
        print("\n=== Debug: Wire Connections ===")
        for wire in all_wire_connections:
            print(f"Wire from ({wire[0][0]:.2f}, {wire[0][1]:.2f}) to ({wire[1][0]:.2f}, {wire[1][1]:.2f})")
            
        # print("\n=== Debug: Label Positions ===")
        for label_type in ['local', 'hierarchical', 'power']:
            # print(f"\n{label_type.capitalize()} Labels:")
            for label in all_labels[label_type]:
                # print(f"\t{label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
                # Find connected points for each label
                connected = get_connected_points(label['position'], all_wire_connections)
                # print("\tConnected points:")
                # for point in connected:
                #     print(f"\t\t({point[0]:.2f}, {point[1]:.2f})")
                    
    netlist = calculate_pin_connectivity(all_component_pins, all_wire_connections, all_labels)

    # Print sheet information
    print("\n=== Sheets ===")
    for sheet in schematic.sheets:
        print(f"\nSheet: {sheet.sheetName.value}")
        print(f"\tFile: {sheet.fileName.value}")
        print(f"\tUUID: {sheet.uuid}")

    # Print component information
    print("\n=== Components ===")
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname != 'power':  # Skip power symbols as they're handled separately
            print(f"\nComponent: {symbol.libraryNickname}/{symbol.entryName}")
            print("\tProperties:")
            for prop in symbol.properties:
                print(f"\t\t{prop.key}: {prop.value}")
            print(f"\tPosition: ({symbol.position.X}, {symbol.position.Y}), Angle: {symbol.position.angle}")
            
            if hasattr(symbol, 'unit'):
                print(f"Unit: {symbol.unit}")

    # Print pin information with more details
    print("\n=== Pin Details ===")
    for component, pins in all_component_pins.items():
        print(f"\nComponent: {component}")
        for pin in pins:
            print(f"\n\tPin {pin['pin_number']} ({pin['pin_name']}):")
            print(f"\t\tPosition: ({pin['absolute_position'][0]:.2f}, {pin['absolute_position'][1]:.2f})")
            print(f"\t\tType: {pin['electrical_type']}")
            if 'alternatePins' in pin:
                print("\t\tAlternate Functions:")
                for alt in pin['alternatePins']:
                    print(f"\t\t\t- {alt['pinName']} ({alt['electricalType']})")

    # Print graphical items
    # print("\n=== Graphical Items ===")
    # for item in schematic.graphicalItems:
    #     if hasattr(item, 'type'):
    #         print(f"\nType: {item.type}")
    #         if item.type == 'wire':
    #             print(f"\tStart: ({item.points[0].X}, {item.points[0].Y})")
    #             print(f"\tEnd: ({item.points[1].X}, {item.points[1].Y})")

    # Print labels
    print("\n=== Labels ===")
    print("\nLocal Labels:")
    for label in all_labels['local']:
        print(f"\t{label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nHierarchical Labels and Sheet Pins:")
    for label in all_labels['hierarchical']:
        if 'uuid' in label:  # This indicates it's a sheet pin
            print(f"\tSheet Pin: {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        else:
            print(f"\tLabel: {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nPower Labels:")
    for label in all_labels['power']:
        print(f"\t{label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")

    # Print netlist
    print("\n=== Netlist ===")
    for net_name, net_info in netlist.items():
        print(f"\n{net_name}:")
        
        # Print connected pins
        if 'pins' in net_info:
            for pin in net_info['pins']:
                print(f"\t{pin['component']} Pin {pin['pin_number']} ({pin['pin_name']})")
        
        # Print power labels
        if 'power_labels' in net_info and net_info['power_labels']:
            print("\tPower Labels:")
            for label in net_info['power_labels']:
                print(f"\t\t{label}")
                
        # Print hierarchical labels
        if 'hierarchical_labels' in net_info and net_info['hierarchical_labels']:
            print("\tHierarchical Labels:")
            for label in net_info['hierarchical_labels']:
                print(f"\t\t{label}")
                
        # Print local labels
        if 'local_labels' in net_info and net_info['local_labels']:
            print("\tLocal Labels:")
            for label in net_info['local_labels']:
                print(f"\t\t{label}")
