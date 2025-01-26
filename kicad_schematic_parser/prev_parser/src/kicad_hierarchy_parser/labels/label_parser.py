def parse_sheet_pins(sheet):
    """
    Parse pins from a schematic sheet and convert them to hierarchical label format.
    Sheet pins are treated as hierarchical labels since they serve the same purpose
    of connecting signals between different hierarchy levels.
    """
    sheet_pins = []
    
    # Get sheet name
    sheet_name = sheet.sheetName.value if hasattr(sheet, 'sheetName') else 'Unknown'
    
    # Extract pins from the sheet
    for pin in getattr(sheet, 'pins', []):
        sheet_pins.append({
            'text': pin.name,  # Pin name
            'shape': pin.connectionType.lower(),  # Pin type (input/output)
            'position': (float(pin.position.X), float(pin.position.Y)),  # Position coordinates
            'angle': float(pin.position.angle) if hasattr(pin.position, 'angle') else 0,  # Angle is optional
            'uuid': pin.uuid,
            'sheet_name': sheet_name  # Associate pin with its parent sheet
        })
    
    return sheet_pins

def parse_labels(schematic):
    """
    Parse different types of labels from the schematic
    """
    labels = {
        'local': [],
        'hierarchical': [],
        'power': []
    }
    
    # Parse local labels
    for label in schematic.labels:
        labels['local'].append({
            'text': label.text,
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        })
        
    # Parse hierarchical labels
    for label in schematic.hierarchicalLabels:
        labels['hierarchical'].append({
            'text': label.text,
            'shape': label.shape,  # input/output/bidirectional/etc
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        })
        
    # Parse sheet pins as hierarchical labels
    for sheet in schematic.sheets:
        sheet_pins = parse_sheet_pins(sheet)
        labels['hierarchical'].extend(sheet_pins)
    
    # Parse power symbols
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname == 'power':
            value_prop = next((prop for prop in symbol.properties if prop.key == 'Value'), None)
            if value_prop:
                labels['power'].append({
                    'text': value_prop.value,
                    'position': (symbol.position.X, symbol.position.Y),
                    'angle': symbol.position.angle
                })

    return labels
