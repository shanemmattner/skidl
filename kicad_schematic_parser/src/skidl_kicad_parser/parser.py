import os
from kiutils.schematic import Schematic
from .components.component_parser import get_component_pins
from .connectivity.wire_parser import get_wire_connections, get_connected_points
from .connectivity.net_parser import calculate_pin_connectivity
from .labels.label_parser import parse_labels
from .connectivity.net_parser import build_sheet_hierarchy

def parse_hierarchical_sheets(schematic, base_path):
    """
    Recursively parse hierarchical sheets and merge results into the main schematic.
    """
    all_schematics = [schematic]

    for sheet in schematic.sheets:
        sheet_file = sheet.fileName.value
        if sheet_file:
            # Use base_path directly instead of dirname to resolve relative paths
            child_path = os.path.join(base_path, sheet_file)
            try:
                print(f"Trying to load sheet from: {child_path}")
                child_schematic = Schematic().from_file(child_path)
                # Pass the same base_path to maintain relative path resolution
                child_sheets = parse_hierarchical_sheets(child_schematic, base_path)
                all_schematics.extend(child_sheets)
            except Exception as e:
                print(f"Warning: Could not process sheet {sheet_file}: {str(e)}")

    return all_schematics

def analyze_schematic(schematic, base_path, debug=False):
    """
    Analyze schematic and generate comprehensive information about components, pins, and connectivity.
    """
    try:
        sheet_hierarchy = build_sheet_hierarchy(schematic, base_path)
    except Exception as e:
        print(f"Warning: Error building sheet hierarchy: {e}")
        sheet_hierarchy = {'root': {'path': base_path}}

    # Parse all schematics, including hierarchical ones
    try:
        all_schematics = parse_hierarchical_sheets(schematic, base_path)
    except Exception as e:
        print(f"Warning: Error parsing hierarchical sheets: {e}")
        all_schematics = [schematic]

    # Initialize empty data structures
    all_labels = {'local': [], 'hierarchical': [], 'power': []}
    all_wire_connections = []
    all_component_pins = {}

    # Process each schematic, handling potential errors
    for sch in all_schematics:
        try:
            labels = parse_labels(sch)
            all_labels['local'].extend(labels.get('local', []))
            all_labels['hierarchical'].extend(labels.get('hierarchical', []))
            all_labels['power'].extend(labels.get('power', []))
        except Exception as e:
            print(f"Warning: Error parsing labels: {e}")

        try:
            wire_connections = get_wire_connections(sch)
            all_wire_connections.extend(wire_connections)
        except Exception as e:
            print(f"Warning: Error parsing wire connections: {e}")

        try:
            component_pins = get_component_pins(sch)
            all_component_pins.update(component_pins)
        except Exception as e:
            print(f"Warning: Error parsing component pins: {e}")

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
                    
    netlist = calculate_pin_connectivity(all_component_pins, all_wire_connections, all_labels, sheet_hierarchy)

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
            print(f"\tSheet Pin: {label['text']} ({label['shape']}) on sheet '{label['sheet_name']}' at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        else:
            print(f"\tLabel: {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nPower Labels:")
    for label in all_labels['power']:
        print(f"\t{label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")

    # Print netlist
# Print netlist with sheet info
    print("\n=== Netlist ===")
    for net_name, net_info in netlist.items():
        print(f"\n{net_name}:")
        
        # Group pins by sheet
        pins_by_sheet = {}
        for pin_info in net_info.get('pins', []):
            sheet = pin_info.get('sheet', 'root')
            if sheet not in pins_by_sheet:
                pins_by_sheet[sheet] = []
            pins_by_sheet[sheet].append(pin_info)
        
        # Print pins grouped by sheet
        for sheet, pins in pins_by_sheet.items():
            print(f"\tSheet: {sheet}")
            for pin_info in pins:
                pin = pin_info['pin']
                component = pin_info['component']
                print(f"\t\t{component} Pin {pin['pin_number']} ({pin['pin_name']})")
        
        # Group labels by sheet
        if 'labels' in net_info:
            labels_by_type = {
                'power': [],
                'hierarchical': [], 
                'local': []
            }
            for label in net_info['labels']:
                label_type = label[0]
                if label_type in labels_by_type:
                    labels_by_type[label_type].append(label[1])
            
            # Print labels with type groups
            for label_type, labels in labels_by_type.items():
                if labels:
                    print(f"\t{label_type.capitalize()} Labels:")
                    for label in labels:
                        print(f"\t\t{label}")

    return schematic.sheets
