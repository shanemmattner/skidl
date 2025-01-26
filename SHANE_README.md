

## Run KiCAD schematic to netlist parser:

```
shanemattner@Shanes-MacBook-Pro skidl % /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export netlist -o example_kicad_project.net kicad_schematic_parser/example_kicad_project/example_kicad_project.kicad_sch
```

after aliasing:

```
shanemattner@Shanes-MacBook-Pro skidl % kicad-cli sch export netlist -o resistor_divider.net kicad_schematic_parser/example_kicad_project/resistor_divider.kicad_sch
```

after more aliasing:

```
kicad-to-netlist example_kicad_project.net example_kicad_project/example_kicad_project.kicad_sch
```