# Schematic File Format

[Documentation Link](https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html)

## Introduction

This documents the s-expression schematic file format for all versions of KiCad from 6.0.

Schematic files use the `.kicad_sch` extension.

## Instance Path

Because KiCad schematics can support multiple instances of the same schematic using hierarchical sheets, information for shared sheets is done using paths consisting of the universally unique identifiers that represent the hierarchical path for the sheet the instance separated by a forward slash ('/'). A typical instance path would look like:

`"/00000000-0000-0000-0000-00004b3a13a4/00000000-0000-0000-0000-00004b617b88"`

The first identifier must be the root sheet which is the same identifier as the root schematic file.

## Label and Pin Shapes

The table below defines the valid shape tokens global labels, hierarchical labels, and hierarchical sheet pins.

| Token | Definition | Image |
|-------|------------|-------|
| input | Label or pin is an input shape | images/label_shape_input |
| output | Label or pin is an output shape | images/label_shape_output |
| bidirectional | Label or pin is a bidirectional shape | images/label_shape_bidirectional |
| tri_state | Label or pin is a tri-state shape | images/label_shape_tristate |
| passive | Label or pin is a tri-state shape | images/label_shape_passive |

## Layout

A schematic file includes the following sections:

- Header
- Unique Identifier
- Page Settings
- Title Block Section
- Symbol Library Symbol Definition
- Junction Section
- No Connect Section
- Wire and Bus Section
- Image Section
- Graphical Line Section
- Graphical Text Section
- Local Label Section
- Global Label Section
- Symbol Section
- Hierarchical Sheet Section
- Root Sheet Instance Section

## Header Section

The `kicad_sch` token indicates that it is KiCad schematic file. This section is required.

> Third party scripts should not use eeschema as the generator identifier. Please use some other identifier so that bugs introduced by third party generators are not confused with a schematic file created by KiCad.

```
(kicad_sch
  (version VERSION)                                             
  (generator GENERATOR)                                         

  ;; contents of the schematic file...                          
)
```

- The version token attribute defines the schematic version using the YYYYMMDD date format.
- The generator token attribute defines the program used to write the file.
- The schematic sections go here.

## Unique Identifier Section

The uuid token defines the globally unique identifier that identifies the schematic.

```
  UNIQUE_IDENTIFIER                                             
```

**NOTE:** Only the root schematic identifier is used as the virtual root sheet identifier. All other identifiers belong to hierarchical sheet objects.

The UNIQUE_IDENTIFIER defines the universally unique identifier for the schematic file. This identifier is used when creating hierarchical sheet paths which are used to reference symbol instance data and hierarchical sheet instance information.

## Library Symbol Section

The lib_symbols token defines a symbol library contain all of the symbols used in the schematic.

```
  (lib_symbols
    SYMBOL_DEFINITIONS...                                       
  )
```

A list of 0 or more symbols.

## Junction Section

The junction token defines a junction in the schematic. The junction section will not exist if there are no junctions in the schematic.

```
  (junction
    POSITION_IDENTIFIER                                         
    (diameter DIAMETER)                                         
    (color R G B A)                                             
    UNIQUE_IDENTIFIER                                           
  )
```

- The POSITION_IDENTIFIER defines the X and Y coordinates of the junction.
- The diameter token attribute defines the DIAMETER of the junction. A diameter of 0 is the default diameter in the system settings.
- The color token attributes define the Red, Green, Blue, and Alpha transparency of the junction. If all four attributes are 0, the default junction color is used.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the junction.

## No Connect Section

The no_connect token defines a unused pin connection in the schematic. The no connect section will not exist if there are not any no connects in the schematic.

```
  (no_connect
    POSITION_IDENTIFIER                                         
    UNIQUE_IDENTIFIER                                           
  )
```

- The POSITION_IDENTIFIER defines the X and Y coordinates of the no connect.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the no connect.

## Bus Entry Section

The bus_entry token defines a bus entry in the schematic. The bus entry section will not exist if there are no bus entries in the schematic.

```
  (bus_entry
    POSITION_IDENTIFIER                                         
    (size X Y)                                                  
    STROKE_DEFINITION                                           
    UNIQUE_IDENTIFIER                                           
  )
```

- The POSITION_IDENTIFIER defines the X and Y coordinates of the bus entry.
- The size token attributes define the X and Y distance of the end point from the position of the bus entry.
- The STROKE_DEFINITION defines how the bus entry is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the bus entry.

## Wire and Bus Section

The wire and bus tokens define wires and buses in the schematic. This section will not exist if there are no wires or buses in the schematic.

```
  (wire | bus
    COORDINATE_POINT_LIST                                       
    STROKE_DEFINITION                                           
    UNIQUE_IDENTIFIER                                           
  )
```

- The COORDINATE_POINT_LIST defines the list of X and Y coordinates of start and end points of the wire or bus.
- The STROKE_DEFINITION defines how the wire or bus is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the wire or bus.

## Image Section

See common Images section.

## Graphical Line Section

The polyline token defines one or more lines that may or may not represent a polygon. This section will not exist if there are no lines in the schematic.

```
  (polyline
    COORDINATE_POINT_LIST                                       
    STROKE_DEFINITION                                           
    UNIQUE_IDENTIFIER                                           
  )
```

- The COORDINATE_POINT_LIST defines the list of X/Y coordinates of to draw line(s) between. A minimum of two points is required.
- The STROKE_DEFINITION defines how the graphical line is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the graphical line.

## Graphical Text Section

The text token defines graphical text in a schematic.

```
  (text
    "TEXT"                                                      
    POSITION_IDENTIFIER                                         
    TEXT_EFFECTS                                                
    UNIQUE_IDENTIFIER                                           
  )
```

- The TEXT is a quoted string that defines the text.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the text.
- The TEXT_EFFECTS section defines how the text is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the graphical text.

## Local Label Section

The label token defines a wire or bus label name in a schematic.

```
  (label
    "TEXT"                                                      
    POSITION_IDENTIFIER                                         
    TEXT_EFFECTS                                                
    UNIQUE_IDENTIFIER                                           
  )
```

- The TEXT is a quoted string that defines the label.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the label.
- The TEXT_EFFECTS section defines how the label text is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the label.

## Global Label Section

The global_label token defines a label name that is visible across all schematics in a design. This section will not exist if no global labels are defined in the schematic.

```
  (global_label
    "TEXT"                                                      
    (shape SHAPE)                                               
    [(fields_autoplaced)]                                       
    POSITION_IDENTIFIER                                         
    TEXT_EFFECTS                                                
    UNIQUE_IDENTIFIER                                           
    PROPERTIES                                                  
  )
```

- The TEXT is a quoted string that defines the global label.
- The shape token attribute defines the way the global label is drawn. See table below for global label shapes.
- The optional fields_autoplaced is a flag that indicates that any PROPERTIES associated with the global label have been place automatically.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the label.
- The TEXT_EFFECTS section defines how the global label text is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the global label.
- The PROPERTIES section defines the properties of the global label. Currently, the only supported property is the inter-sheet reference.

## Hierarchical Label Section

The hierarchical_label section defines labels that are used by hierarchical sheets to define connections between sheet in hierarchical designs. This section will not exist if no global labels are defined in the schematic.

```
  (hierarchical_label
    "TEXT"                                                      
    (shape SHAPE)                                               
    POSITION_IDENTIFIER                                         
    TEXT_EFFECTS                                                
    UNIQUE_IDENTIFIER                                           
  )
```

- The TEXT is a quoted string that defines the hierarchical label.
- The shape token attribute defines the way the hierarchical label is drawn. See table above for hierarchical label shapes.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the label.
- The TEXT_EFFECTS section defines how the hierarchical label text is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the hierarchical label.

## Symbol Section

The symbol token in the symbol section of the schematic defines an instance of a symbol from the library symbol section of the schematic.

```
  (symbol
    "LIBRARY_IDENTIFIER"                                        
    POSITION_IDENTIFIER                                         
    (unit UNIT)                                                 
    (in_bom yes|no)                                             
    (on_board yes|no)                                           
    UNIQUE_IDENTIFIER                                           
    PROPERTIES                                                  
    (pin "1" (uuid e148648c-6605-4af1-832a-31eaf808c2f8))       
    (instances                                                  
      (project "PROJECT_NAME"                                   
        (path "PATH_INSTANCE"                                   
          (reference "REFERENCE")                               
          (unit UNIT)                                           
        )

        ;; Optional symbol instances for this `project`...
      )

      ;; Optional symbol instances for other `project`...
    )
  )
```

- The LIBRARY_IDENTIFIER defines which symbol in the library symbol section of the schematic that this schematic symbol references.
- The POSITION_IDENTIFIER defines the X and Y coordinates and angle of rotation of the symbol.
- The unit token attribute defines which unit in the symbol library definition that the schematic symbol represents.
- The in_bom token attribute determines whether the schematic symbol appears in any bill of materials output.
- The on_board token attribute determines if the footprint associated with the symbol is exported to the board via the netlist.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the symbol. This is used to map the symbol the symbol instance information.
- The PROPERTIES section defines a list of symbol properties of the schematic symbol.
- The pin token attributes define pin-related information.
- The instances token defines a list of symbol instances grouped by project. Every symbol will have at least one instance.
- The project token attribute defines the name of the project to which the instance data belongs. There can be instance data from other projects when schematics are shared across multiple projects. The projects will be sorted by the PROJECT_NAME in alphabetical order.
- The path token attribute is the path to the sheet instance for the instance data.
- The reference token attribute is a string that defines the reference designator for the symbol instance.
- The unit token attribute is an integer ordinal that defines the symbol unit for the symbol instance. For symbols that do not define multiple units, this will always be 1.

## Hierarchical Sheet Section

The sheet token defines a hierarchical sheet of the schematic.

```
  (sheet
    POSITION_IDENTIFIER                                         
    (size WIDTH HEIGHT)                                         
    [(fields_autoplaced)]                                       
    STROKE_DEFINITION                                           
    FILL_DEFINITION                                             
    UNIQUE_IDENTIFIER                                           
    SHEET_NAME_PROPERTY                                         
    FILE_NAME_PROPERTY                                          
    HIERARCHICAL_PINS                                           
    (instances                                                  
      (project "PROJECT_NAME"                                   
        (path "PATH_INSTANCE"                                   
          (page "PAGE_NUMBER")                                  
        )

        ;; Optional sheet instances for this `project`...
      )

      ;; Optional sheet instances for other `project`...
    )
  )
```

- The POSITION_IDENTIFIER defines the X and Y coordinates and angle of rotation of the sheet in the schematic.
- The size token attributes define the WIDTH and HEIGHT of the sheet.
- The optional fields_autoplaced token indicates if the properties have been automatically placed.
- The STROKE_DEFINITION defines how the sheet outline is drawn.
- The FILL_DEFINITION defines how the sheet is filled.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the sheet. This is used to map the sheet symbol instance information and sheet instance information.
- The SHEET_PROPERTY_NAME is a property that defines the name of the sheet. This property is mandatory.
- The FILE_NAME_PROPERTY is a property that defines the file name of the sheet. This property is mandatory.
- The HIERARCHICAL_PINS section is a list of hierarchical pins that map a hierarchical label defined in the associated schematic file.
- The instances token defines a list of sheet instances grouped by project. Every sheet will have at least one instance.
- The project token attribute defines the name of the project to which the instance data belongs. There can be instance data from other projects when schematics are shared across multiple projects. The projects will be sorted by the PROJECT_NAME in alphabetical order.
- The path token attribute is the path to the sheet instance for the sheet instance data.
- The page token attribute is a string that defines the page number for the sheet instance.

## Hierarchical Sheet Pin Definition

The pin token in a sheet object defines an electrical connection between the sheet in a schematic with the hierarchical label defined in the associated schematic file.

```
  (pin
    "NAME"                                                      
    input | output | bidirectional | tri_state | passive        
    POSITION_IDENTIFIER                                         
    TEXT_EFFECTS                                                
    UNIQUE_IDENTIFIER                                           
  )
```

- The "NAME" attribute defines the name of the sheet pin. It must have an identically named hierarchical label in the associated schematic file.
- The electrical connect type token defines the type of electrical connect made by the sheet pin.
- The POSITION_IDENTIFIER defines the X and Y coordinates and angle of rotation of the pin in the sheet.
- The TEXT_EFFECTS section defines how the pin name text is drawn.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the pin.

## Root Sheet Instance Section

```
 (path
    "/"                                                         
    (page "PAGE")                                               
  )
```

- The instance path is always empty ("/") since there are no sheets pointing to the root sheet.
- The page token defines the page number of the root sheet. Page numbers can be any valid string.

---

*Last Modified 2023-12-29*