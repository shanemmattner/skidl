# KiCad Project File Configuration

## Issue
When generating KiCad projects with hierarchical sheets, the top-level schematic is not showing up in KiCad. This is because the project file (.kicad_pro) needs proper configuration to:
1. Reference the correct main schematic file
2. Define the sheet hierarchy structure

## Current Implementation
The current implementation in `gen_schematic_v8.py`:
- Successfully creates hierarchical sheet schematics
- Renames and sets up the main schematic file
- Does not update the project file configuration

## Required Changes

### Project File Updates
The following files need to be renamed to match the project name:
1. Project file: kicad_blank_project.kicad_pro -> resistor.kicad_pro
2. PCB file: kicad_blank_project.kicad_pcb -> resistor.kicad_pcb
3. Project Local Settings: kicad_blank_project.kicad_prl -> resistor.kicad_prl

The .kicad_pro file needs to be:
2. Updated with correct configuration:
```json
{
  "meta": {
    "filename": "resistor.kicad_pro",  // Update to match project name
    "version": 1
  },
  "sheets": [
    {
      "path": "resistor.kicad_sch",  // Main schematic
      "sheet_name": "",  // Root sheet has no name
      "id": "00000000-0000-0000-0000-000000000000"  // Unique ID
    },
    {
      "path": "resistor_circuit.kicad_sch",
      "sheet_name": "resistor_circuit",
      "id": "00000000-0000-0000-0000-000000000001"
    }
  ]
}
```

### Implementation Changes
Add new functionality in `gen_schematic_v8.py` after saving the main schematic:

1. Project File Renaming:
```python
old_project_path = os.path.join(project_dir, "kicad_blank_project.kicad_pro")
new_project_path = os.path.join(project_dir, f"{project_name}.kicad_pro")
if os.path.exists(old_project_path):
    os.rename(old_project_path, new_project_path)
```

2. Project Configuration Update:
```python
import json

def update_project_file(project_path, project_name, sheets):
    """Update KiCad project file configuration."""
    with open(project_path, 'r') as f:
        project_config = json.load(f)
    
    # Update meta filename
    project_config['meta']['filename'] = f"{project_name}.kicad_pro"
    
    # Update sheets configuration
    project_config['sheets'] = [
        {
            "path": f"{project_name}.kicad_sch",
            "sheet_name": "",
            "id": str(uuid.uuid4())
        }
    ]
    
    # Add hierarchical sheets
    for sheet_name in sheets:
        project_config['sheets'].append({
            "path": f"{sheet_name}.kicad_sch",
            "sheet_name": sheet_name,
            "id": str(uuid.uuid4())
        })
    
    # Write updated configuration
    with open(project_path, 'w') as f:
        json.dump(project_config, f, indent=2)
```

### Integration
Call the update function after saving the main schematic:
```python
try:
    main_sch.to_file(main_sch_path)
    active_logger.info(f"Added sheet symbols to main schematic at {main_sch_path}")
    
    # Update project configuration
    update_project_file(new_project_path, project_name, subcircuits)
except Exception as e:
    active_logger.error(f"Error updating project configuration: {str(e)}")
    raise
```

## Benefits
These changes will:
1. Ensure proper project configuration
2. Make the top-level schematic visible in KiCad
3. Maintain correct hierarchical sheet relationships
4. Support future project expansion with additional sheets

## Testing
Test cases should verify:
1. Project file is renamed correctly
2. Meta filename is updated
3. Sheet hierarchy is configured properly
4. KiCad can open and display the project correctly