import os
from kiutils.schematic import Schematic
from .components.component_parser import get_component_pins
from .connectivity.wire_parser import get_wire_connections
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

def analyze_schematic(schematic, base_path):
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

    # Generate netlist
    netlist = calculate_pin_connectivity(all_component_pins, all_wire_connections, all_labels)

    # Print component information
    print("\n=== Components ===")
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname != 'power':  # Skip power symbols as they're handled separately
            print(f"\nComponent: {symbol.libraryNickname}/{symbol.entryName}")
            print("Properties:")
            for prop in symbol.properties:
                print(f"  {prop.key}: {prop.value}")
            print(f"Position: ({symbol.position.X}, {symbol.position.Y}), Angle: {symbol.position.angle}")
            
            if hasattr(symbol, 'unit'):
                print(f"Unit: {symbol.unit}")

    # Print pin information with more details
    print("\n=== Pin Details ===")
    for component, pins in all_component_pins.items():
        print(f"\nComponent: {component}")
        for pin in pins:
            print(f"\n  Pin {pin['pin_number']} ({pin['pin_name']}):")
            print(f"    Position: ({pin['absolute_position'][0]:.2f}, {pin['absolute_position'][1]:.2f})")
            print(f"    Type: {pin['electrical_type']}")
            if 'alternatePins' in pin:
                print("    Alternate Functions:")
                for alt in pin['alternatePins']:
                    print(f"      - {alt['pinName']} ({alt['electricalType']})")

    # Print graphical items
    print("\n=== Graphical Items ===")
    for item in schematic.graphicalItems:
        if hasattr(item, 'type'):
            print(f"\nType: {item.type}")
            if item.type == 'wire':
                print(f"  Start: ({item.points[0].X}, {item.points[0].Y})")
                print(f"  End: ({item.points[1].X}, {item.points[1].Y})")

    # Print labels
    print("\n=== Labels ===")
    print("\nLocal Labels:")
    for label in all_labels['local']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nHierarchical Labels:")
    for label in all_labels['hierarchical']:
        print(f"  {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nPower Labels:")
    for label in all_labels['power']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")

    # Print netlist
    print("\n=== Netlist ===")
    for net_name, net_info in netlist.items():
        print(f"\n{net_name}:")
        
        # Print connected pins
        if 'pins' in net_info:
            for pin in net_info['pins']:
                print(f"  {pin['component']} Pin {pin['pin_number']} ({pin['pin_name']})")
        
        # Print power labels
        if 'power_labels' in net_info and net_info['power_labels']:
            print("  Power Labels:")
            for label in net_info['power_labels']:
                print(f"    {label}")
                
        # Print hierarchical labels
        if 'hierarchical_labels' in net_info and net_info['hierarchical_labels']:
            print("  Hierarchical Labels:")
            for label in net_info['hierarchical_labels']:
                print(f"    {label}")
                
        # Print local labels
        if 'local_labels' in net_info and net_info['local_labels']:
            print("  Local Labels:")
            for label in net_info['local_labels']:
                print(f"    {label}")
                
        # Print merged information
        if 'merged_from' in net_info:
            print("  Merged from nets:")
            for source_net in net_info['merged_from']:
                print(f"    {source_net}")
