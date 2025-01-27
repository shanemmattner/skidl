# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from skidl.logger import active_logger

def extract_subcircuit_components(subcircuit_module):
    """
    Extract all components from a subcircuit module.
    
    Args:
        subcircuit_module: The Python module containing the subcircuit definition
        
    Returns:
        list: A list of dictionaries containing component information with keys:
            - lib: Library name (e.g., 'Device', 'Connector')
            - name: Part name (e.g., 'R', 'C', 'USB_C_Plug_USB2.0')
            - value: Component value (e.g., '10uF', '5.1K')
            - footprint: KiCad footprint
            - tag: Unique identifier
            - sheet_name: KiCad sheet name
            - sheet_file: KiCad sheet file
    """
    try:
        # Get the source code of the module
        source = subcircuit_module.__file__
        with open(source, 'r') as f:
            code = f.read()
            
        # Simple parsing to find Part() declarations
        # This is a basic implementation that assumes clean formatting
        components = []
        lines = code.split('\n')
        for line in lines:
            if 'Part(' in line and '=' in line:
                # Extract component name and Part() arguments
                name, part_def = line.split('=', 1)
                name = name.strip()
                
                # Parse the Part() arguments
                # Remove 'Part(' and trailing ')'
                args = part_def.strip()[5:-1]
                
                # Split by comma but respect nested structures
                params = []
                current = ''
                nested = 0
                for char in args:
                    if char == '(' or char == '[' or char == '{':
                        nested += 1
                    elif char == ')' or char == ']' or char == '}':
                        nested -= 1
                    elif char == ',' and nested == 0:
                        params.append(current.strip())
                        current = ''
                        continue
                    current += char
                if current:
                    params.append(current.strip())
                
                # Convert parameters to a dictionary
                comp_info = {}
                for param in params:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        # Clean up the values
                        value = value.strip().strip("'").strip('"')
                        key = key.strip()
                        
                        # Map parameters to our standardized keys
                        key_mapping = {
                            'value': 'value',
                            'footprint': 'footprint',
                            'tag': 'tag',
                            'Sheetname': 'sheet_name',
                            'Sheetfile': 'sheet_file'
                        }
                        
                        if key in key_mapping:
                            comp_info[key_mapping[key]] = value
                    else:
                        # First two unnamed parameters are lib and name
                        param = param.strip().strip("'").strip('"')
                        if 'lib' not in comp_info:
                            comp_info['lib'] = param
                        elif 'name' not in comp_info:
                            comp_info['name'] = param
                
                components.append(comp_info)
                
        return components
        
    except Exception as e:
        active_logger.error(f"Error extracting components: {str(e)}")
        raise
