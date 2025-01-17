import os

def parse_kicad_symbols(file_path: str):
    """Parse KiCad symbol file and extract symbol names and pins"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split content into lines and join with single spaces
    content = ' '.join(line.strip() for line in content.split('\n') if line.strip())
    
    def parse_parens(s):
        result = []
        current = result
        stack = []
        
        i = 0
        token = ''
        
        while i < len(s):
            char = s[i]
            
            if char == '(':
                if token:
                    current.append(token)
                    token = ''
                stack.append(current)
                new_list = []
                current.append(new_list)
                current = new_list
            elif char == ')':
                if token:
                    current.append(token)
                    token = ''
                if stack:
                    current = stack.pop()
            elif char.isspace():
                if token:
                    current.append(token)
                    token = ''
            else:
                token += char
            
            i += 1
            
        if token:
            current.append(token)
            
        return result

    def find_pin_number(pin_data):
        """Recursively find the pin number in the nested structure"""
        if not isinstance(pin_data, list):
            return None
        
        for item in pin_data:
            if isinstance(item, list) and item and item[0] == 'number':
                return item[1]
            elif isinstance(item, list):
                result = find_pin_number(item)
                if result:
                    return result
        return None

    def find_pin_name(pin_data):
        """Recursively find the pin name in the nested structure"""
        if not isinstance(pin_data, list):
            return None
        
        for item in pin_data:
            if isinstance(item, list) and item and item[0] == 'name':
                return item[1]
            elif isinstance(item, list):
                result = find_pin_name(item)
                if result:
                    return result
        return None

    def extract_pins(symbol_data):
        pins = []
        for item in symbol_data:
            if isinstance(item, list):
                # Look for pin definitions in the format (symbol "Name_1_1" ...)
                if item and item[0] == 'symbol' and '_1_1' in item[1]:
                    for subitem in item:
                        if isinstance(subitem, list) and subitem and subitem[0] == 'pin':
                            try:
                                pin_number = find_pin_number(subitem)
                                pin_name = find_pin_name(subitem)
                                pin_type = subitem[1]  # Type is usually the second element
                                
                                if pin_number:  # Only add if we found a pin number
                                    pins.append({
                                        'number': pin_number,
                                        'name': pin_name or '',
                                        'type': pin_type
                                    })
                            except Exception as e:
                                print(f"Error parsing pin: {e}")
                                continue
                # Recursively check nested structures
                elif isinstance(item, list):
                    pins.extend(extract_pins(item))
        return pins

    symbols = {}
    parsed = parse_parens(content)
    
    if parsed and parsed[0] and parsed[0][0] == 'kicad_symbol_lib':
        for section in parsed[0][1:]:
            if isinstance(section, list) and section and section[0] == 'symbol':
                # Get base symbol name (without _1_1 suffix)
                name = section[1]
                if isinstance(name, list):
                    name = name[0]
                if isinstance(name, str):
                    if '_1_1' in name or '_0_1' in name:
                        continue  # Skip subsections
                    name = name.strip('"')  # Remove quotes if present
                    
                    # Get pins
                    pins = extract_pins(section)
                    
                    if name not in symbols:
                        symbols[name] = {'pins': []}
                    symbols[name]['pins'] = pins

    return symbols

def main():
    # file_path = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym"
    # symbols = parse_kicad_symbols(file_path)
    def parse_all_kicad_symbols(directory_path: str):
        symbols = {}
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.kicad_sym'):
                    file_path = os.path.join(root, file)
                    print(f"Parsing file: {file_path}")  # Print out the file being parsed
                    file_symbols = parse_kicad_symbols(file_path)
                    symbols.update(file_symbols)
        return symbols

    directory_path = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
    symbols = parse_all_kicad_symbols(directory_path)
    
    output_file = "/Users/shanemattner/Desktop/Circuit_Forge/schematic_scraper_py_output.txt"
    with open(output_file, 'w') as f:
        # Write results in sorted order
        for name in sorted(symbols.keys()):
            data = symbols[name]
            f.write(f"\nSymbol: {name}\n")
            f.write(f"Pins ({len(data['pins'])}):\n")
            # Sort pins by number
            for pin in sorted(data['pins'], key=lambda x: int(x['number']) if x['number'].isdigit() else float('inf')):
                f.write(f"  {pin['number']}: {pin['name']} ({pin['type']})\n")

if __name__ == "__main__":
    main()