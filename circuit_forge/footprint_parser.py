import os
import sys

def parse_kicad_footprint(file_path: str):
    """Parse KiCad footprint file and extract pad information."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove comments and split content
    lines = [line.split('#')[0].strip() for line in content.split('\n') if line.strip()]
    content = ' '.join(lines)

    def parse_parens(s):
        # Similar parsing function as used for symbols
        # ...
        parsed = parse_parens(content)
        footprint_data = {}

    def extract_pads(data):
        pads = []
        for item in data:
            if isinstance(item, list) and item:
                if item[0] == 'pad':
                    pad_number = item[1].strip('"')
                    pad_type = item[2]
                    pad_shape = item[3]
                    pad_info = {'number': pad_number, 'type': pad_type, 'shape': pad_shape}
                    # Extract additional pad properties like size, layers, etc.
                    for subitem in item[4:]:
                        if isinstance(subitem, list) and subitem:
                            if subitem[0] == 'size':
                                pad_info['size'] = (float(subitem[1]), float(subitem[2]))
                            elif subitem[0] == 'layers':
                                pad_info['layers'] = subitem[1:]
                    pads.append(pad_info)
                else:
                    pads.extend(extract_pads(item))
        return pads

    footprint_data['pads'] = extract_pads(parsed)
    return footprint_data

def main():
    file_path = "/home/shane/shane/pcb_maker_5000/Resistor_SMD.pretty/R_0201_0603Metric.kicad_mod"
    footprint = parse_kicad_footprint(file_path)
    print(f"Pads ({len(footprint['pads'])}):")
    for pad in footprint['pads']:
        print(f"  Pad {pad['number']}: Type={pad['type']}, Shape={pad['shape']}, Size={pad.get('size')}, Layers={pad.get('layers')}")

if __name__ == "__main__":
    main()
