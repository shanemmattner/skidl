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
