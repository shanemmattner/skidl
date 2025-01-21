from skidl import *

def convert_to_skidl(circuit_desc):
    # Initialize components and nets dictionaries
    components = {}
    nets = {}
    
    # Parse components and nets from the description
    current_component = None
    for line in circuit_desc.split('\n'):
        line = line.strip()
        
        # Component detection
        if line.startswith("Component:"):
            comp_info = line.split(": ")[1].split("/")
            lib_name = comp_info[0].strip()
            part_name = comp_info[1].strip()
            ref = line.split("Reference: ")[1].split(",")[0].strip()
            value = line.split("Value: ")[1].split(",")[0].strip()
            footprint = line.split("Footprint: ")[1].split(",")[0].strip()
            
            components[ref] = Part(lib_name, part_name, value=value, footprint=footprint)
            current_component = ref
        
        # Pin detection
        elif line.startswith("Pin ") and current_component:
            pin_info = line.split("(")[1].split(")")
            pin_num = pin_info[0].split()[0]
            pin_name = pin_info[0].split("(")[-1].strip()
            net_name = line.split("Net: ")[1].split(",")[0].strip()
            
            if net_name not in nets:
                nets[net_name] = Net(net_name)
            
            components[current_component][pin_num] += nets[net_name]
        
        # Net detection
        elif line.startswith("Net:"):
            net_name = line.split(": ")[1].strip()
            if net_name not in nets:
                nets[net_name] = Net(net_name)
    
    # Handle power nets
    power_nets = ['VCC', 'GND', '3V3', '5V']
    for net_name in power_nets:
        if net_name in nets:
            nets[net_name].drive = POWER
    
    return components, nets

def generate_skidl_code(components, nets):
    # Generate the SKiDL code structure
    code = "from skidl import *\n\n"
    
    # Add components
    code += "# Components\n"
    for ref, part in components.items():
        code += f"{ref} = Part('{part.lib}', '{part.name}', "
        code += f"value='{part.value}', footprint='{part.footprint}')\n"
    
    # Add nets
    code += "\n# Nets\n"
    for net_name, net in nets.items():
        code += f"{net_name} = Net('{net_name}')\n"
        if net_name in ['VCC', 'GND', '3V3', '5V']:
            code += f"{net_name}.drive = POWER\n"
    
    # Add connections
    code += "\n# Connections\n"
    for ref, part in components.items():
        for pin in part.pins:
            if pin.net:
                net_name = pin.net.name
                code += f"{ref}['{pin.num}'] += {net_name}\n"
    
    code += "\n# Generate Netlist\n"
    code += "generate_netlist()\n"
    
    return code

# Example usage:
circuit_description = """..."""  # Paste the full circuit description here

components, nets = convert_to_skidl(circuit_description)
skidl_code = generate_skidl_code(components, nets)

print(skidl_code)
