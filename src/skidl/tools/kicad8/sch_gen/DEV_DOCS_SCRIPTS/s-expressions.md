# KiCad S-Expression Format

[Link to Kicad Documentation](https://dev-docs.kicad.org/en/file-formats/sexpr-intro/)
## Introduction

KiCad uses an s-expression file format for symbol libraries, footprint libraries, schematics, printed circuit boards, and title block and border worksheets.

## Syntax

Syntax is based on the Specctra DSN file format.

- Token definitions are delimited by opening ( and closing ) parenthesis.
- All tokens are lowercase.
- Tokens cannot contain any white space characters or special characters other than the underscore '_' character.
- All strings are quoted using the double quote character (") and are UTF-8 encoded.
- Tokens can have zero or more attributes.
- Human readability is a design goal.

## Conventions

In order to use the file format documentation properly, there are a few notation conventions that must be understood:

- Token attributes are upper case descriptive names. For example (at X Y), X is the horizontal coordinate and Y is the vertical coordinate.
- Some tokens have a limited number of possible attribute values which are separated by a logical or character '|'. For example (visible yes|no) the only valid attributes for the visible token are yes or no.
- Some tokens have optional attributes which are enclosed in square braces. For example (paper A0 [portrait]) the page portrait setting is optional.

## Coordinates and Sizes

- All values are given in millimeters.
- Exponential floating point values are not used for readability purposes.
- All coordinates are relative to the origin of their containing object.

## Common Syntax

This section defines all syntax that is shared across the symbol library, footprint library, schematic, board, and work sheet file formats.

### Library Identifier

The schematic symbol library and printed circuit board footprint library file formats use library identifiers. Library identifiers are defined as a quoted string using the "LIBRARY_NICKNAME:ENTRY_NAME" format where "LIBRARY_NICKNAME" is the nickname of the library in the symbol or footprint library table and "ENTRY_NAME" is the name of the symbol or footprint in the library separated by a colon.

The "LIBRARY_NICKNAME" is not stored in the library files because a library cannot know what the assigned library table nickname is in advance. Only the "ENTRY_NAME" is saved in the library files.

### Position Identifier

The at token defines the positional coordinates and rotation of an object.

```
(at
  X                                                           
  Y                                                           
  [ANGLE]                                                     
)
```

- The X attribute defines the horizontal position of the object.
- The Y attribute defines the vertical position of the object.
- The optional ANGLE attribute defines the rotational angle of the object. Not all objects have rotational position definitions.
- Symbol text ANGLEs are stored in tenth's of a degree. All other ANGLEs are stored in degrees.

### Coordinate Point List

The pts token defines a list of X/Y coordinate points.

```
(pts
  (xy X Y)                                                    
  ...
  (xy X Y)
)
```

The xy token defines a single X and Y coordinate pair. The number of points is determined by the object type.

### Stroke Definition

The stroke token defines how the outlines of graphical objects are drawn.

```
(stroke
  (width WIDTH)                                               
  (type TYPE)                                                 
  (color R G B A)                                             
)
```

- The width token attribute defines the line width of the graphic object.
- The type token attribute defines the line style of the graphic object. Valid stroke line styles are:
  - dash
  - dash_dot
  - dash_dot_dot (from version 7)
  - dot
  - default
  - solid
- The color token attributes define the line red, green, blue, and alpha color settings.

### Text Effects

All text objects can have an optional effects section that defines how the text is displayed.

```
(effects
  (font                                                       
    [(face FACE_NAME)]                                        
    (size HEIGHT WIDTH)                                       
    [(thickness THICKNESS)]                                   
    [bold]                                                    
    [italic]                                                  
    [(line_spacing LINE_SPACING)]                             
  )
  [(justify [left | right] [top | bottom] [mirror])]          
  [hide]                                                      
)
```

- The font token attributes define how the text is shown.
- The optional face token indicates the font family. It should be a TrueType font family name or "KiCad Font" for the KiCad stroke font. (from version 7)
- The size token attributes define the font height and width.
- The thickness token attribute defines the line thickness of the font.
- The bold token specifies if the font should be bold.
- The italic token specifies if the font should be italicized.
- The line_spacing token specifies the spacing between lines as a ratio of standard line-spacing. (Not yet supported)
- The optional justify token attributes define if the text is justified horizontally right or left and/or vertically top or bottom and/or mirrored. If the justification is not defined, then the text is center justified both horizontally and vertically and not mirrored.
- The mirror token is only supported in the PCB Editor and Footprints.
- The optional hide token defines if the text is hidden.

### Page Settings

The paper token defines the drawing page size and orientation.

```
(paper
  PAPER_SIZE | WIDTH HEIGHT                                   
  [portrait]                                                  
)
```

- Valid pages sizes are A0, A1, A2, A3, A4, A5, A, B, C, D, and E or the WIDTH and HEIGHT attributes are used for custom user defined page sizes.
- The portrait token defines if the page is shown in the portrait mode. If not defined, the landscape page layout mode is used.

### Title Block

The title_block token defines the contents of the title block.

```
(title_block
  (title "TITLE")                                             
  (date "DATE")                                               
  (rev "REVISION")                                            
  (company "COMPANY_NAME")                                    
  (comment N "COMMENT")                                       
)
```

- The title token attribute is a quoted string that defines the document title.
- The date token attribute is a quoted string that defines the document date using the YYYY-MM-DD format.
- The rev token attribute is a quoted string that defines the document revision.
- The company token attribute is a quoted string that defines the document company name.
- The comment token attributes define the document comments where N is a number from 1 to 9 and COMMENT is a quoted string.

### Properties

The property token defines a key value pair for storing user defined information.

```
(property
  "KEY"                                                       
  "VALUE"                                                     
)
```

- The property key attribute is a string that defines the name of the property. Property keys must be unique.
- The property value attribute is a string associated with the key attribute.

### Universally Unique Identifier

The uuid token defines an universally unique identifier.

```
(uuid
  UUID                                                        
)
```

- The UUID attribute is a Version 4 (random) UUID that should be globally unique. KiCad UUIDs are generated using the mt19937 Mersenne Twister algorithm.
- Files converted from legacy versions of KiCad (prior to 6.0) have their locally-unique timestamps re-encoded in UUID format.

### Images

The image token defines an embedded image. This section will not exist if no images are present.

```
(image
  POSITION_IDENTIFIER                                         
  [(scale SCALAR)]                                            
  [(layer LAYER_DEFINITIONS)]                                 
  UNIQUE_IDENTIFIER                                           
  (data IMAGE_DATA)                                           
)
```

- The POSITION_IDENTIFIER defines the X and Y coordinates of the image.
- The optional scale token attribute defines the SCALE_FACTOR of the image.
- The layer token attribute defines the associated board layer of the image using one canonical layer name. Only used by board and footprint images.
- The UNIQUE_IDENTIFIER defines the universally unique identifier for the image.
- The data token attribute defines the image data in the portable network graphics format (PNG) encoded with MIME type base64.

## Board Common Syntax

This section defines all syntax that is shared across the footprint library and printed circuit board file formats.

### Board Coordinates

The minimum internal unit for printed circuit board and footprint files is one nanometer so there is maximum resolution of six decimal places or 0.000001 mm. Any precision beyond six places will be truncated.

### Layers

All drawable board and footprint objects exist on a layer which is defined in the drawable item definition. All layers can be renamed by the user.

Internally, all layer names are canonical. User defined layer names are only used for display and output purposes.

```
(layer
  LAYER_DEFINITION                                            
)
```

Layer definitions can be specified as a list of one or more canonical layer names or with a '*' wildcard to represent all layers that match the rest of the wildcard. For instance, *.Cu represents all of the copper layers. This only applies to canonical layers names.

### Layer Capacity

- 60 total layers
- 32 copper layers
- 8 paired technical layers for silk screen, solder mask, solder paste, and adhesive
- 4 user pre-defined layers for drawings, engineering change order (ECO), and comments
- 1 layer to define the board outline
- 1 layer to define the board margins
- 9 optional user definable layers

### Canonical Layer Names

| Canonical Name | Description |
|---------------|-------------|
| F.Cu | Front copper layer |
| In1.Cu | Inner copper layer 1 |
| In2.Cu | Inner copper layer 2 |
| In3.Cu | Inner copper layer 3 |
| In4.Cu | Inner copper layer 4 |
| In5.Cu | Inner copper layer 5 |
| In6.Cu | Inner copper layer 6 |
| In7.Cu | Inner copper layer 7 |
| In8.Cu | Inner copper layer 8 |
| In9.Cu | Inner copper layer 9 |
| In10.Cu | Inner copper layer 10 |
| In11.Cu | Inner copper layer 11 |
| In12.Cu | Inner copper layer 12 |
| In13.Cu | Inner copper layer 13 |
| In14.Cu | Inner copper layer 14 |
| In15.Cu | Inner copper layer 15 |
| In16.Cu | Inner copper layer 16 |
| In17.Cu | Inner copper layer 17 |
| In18.Cu | Inner copper layer 18 |
| In19.Cu | Inner copper layer 19 |
| In20.Cu | Inner copper layer 20 |
| In21.Cu | Inner copper layer 21 |
| In22.Cu | Inner copper layer 22 |
| In23.Cu | Inner copper layer 23 |
| In24.Cu | Inner copper layer 24 |
| In25.Cu | Inner copper layer 25 |
| In26.Cu | Inner copper layer 26 |
| In27.Cu | Inner copper layer 27 |
| In28.Cu | Inner copper layer 28 |
| In29.Cu | Inner copper layer 29 |
| In30.Cu | Inner copper layer 30 |
| B.Cu | Back copper layer |
| B.Adhes | Back adhesive layer |
| F.Adhes | Front adhesive layer |
| B.Paste | Back solder paste layer |
| F.Paste | Front solder paste layer |
| B.SilkS | Back silk screen layer |
| F.SilkS | Front silk screen layer |
| B.Mask | Back solder mask layer |
| F.Mask | Front solder mask layer |
| Dwgs.User | User drawing layer |
| Cmts.User | User comment layer |
| Eco1.User | User engineering change order layer 1 |
| Eco2.User | User engineering change order layer 2 |
| Edge.Cuts | Board outline layer |
| F.CrtYd | Footprint front courtyard layer |
| B.CrtYd | Footprint back courtyard layer |
| F.Fab | Footprint front fabrication layer |
| B.Fab | Footprint back fabrication layer |
| User.1 | User definable layer 1 |
| User.2 | User definable layer 2 |
| User.3 | User definable layer 3 |
| User.4 | User definable layer 4 |
| User.5 | User definable layer 5 |
| User.6 | User definable layer 6 |
| User.7 | User definable layer 7 |
| User.8 | User definable layer 8 |
| User.9 | User definable layer 9 |

## Footprint

The footprint token defines a footprint.

Prior to version 6, the footprint token was referred to as module.

```
(footprint
  ["LIBRARY_LINK"]                                            
  [locked]                                                    
  [placed]                                                    
  (layer LAYER_DEFINITIONS)                                   
  (tedit TIME_STAMP)                                          
  [(uuid UUID)]                                               
  [POSITION_IDENTIFIER]                                       
  [(descr "DESCRIPTION")]                                     
  [(tags "NAME")]                                             
  [(property "KEY" "VALUE") ...]                              
  (path "PATH")                                               
  [(autoplace_cost90 COST)]                                   
  [(autoplace_cost180 COST)]                                  
  [(solder_mask_margin MARGIN)]                               
  [(solder_paste_margin MARGIN)]                              
  [(solder_paste_ratio RATIO)]                                
  [(clearance CLEARANCE)]                                     
  [(zone_connect CONNECTION_TYPE)]                            
  [(thermal_width WIDTH)]                                     
  [(thermal_gap DISTANCE)]                                    
  [ATTRIBUTES]                                                
  [(private_layers LAYER_DEFINITIONS)]                        
  [(net_tie_pad_groups PAD_GROUP_DEFINITIONS)]                
  GRAPHIC_ITEMS...                                            
  PADS...                                                     
  ZONES...                                                    
  GROUPS...                                                   
  3D_MODEL                                                    
)
```

- The "LIBRARY_LINK" attribute defines the link to footprint library of the footprint. This only applies to footprints defined in the board file format.
- The optional locked token defines a flag to indicate the footprint cannot be edited.
- The optional placed token defines a flag to indicate that the footprint has not been placed.
- The layer token defines the canonical layer the footprint is placed.
- The tedit token defines a the last time the footprint was edited.
- The uuid token defines the unique identifier for the footprint. This only applies to footprints defined in the board file format.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotational angle of the footprint. This only applies to footprints defined in the board file format.
- The optional tags token defines a string of search tags for the footprint.
- The optional descr token defines a string containing the description of the footprint.
- The optional property token defines a property for the footprint.
- The path token defines the hierarchical path of the schematic symbol linked to the footprint. This only applies to footprints defined in the board file format.
- The optional autoplace_cost90 token defines the vertical cost of when using the automatic footprint placement tool. Valid values are integers 1 through 10. This only applies to footprints defined in the board file format.
- The optional autoplace_cost180 token defines the horizontal cost of when using the automatic footprint placement tool. Valid values are integers 1 through 10. This only applies to footprints defined in the board file format.
- The optional solder_mask_margin token defines the solder mask distance from all pads in the footprint. If not set, the board solder_mask_margin setting is used.
- The optional solder_paste_margin token defines the solder paste distance from all pads in the footprint. If not set, the board solder_paste_margin setting is used.
- The optional solder_paste_ratio token defines the percentage of the pad size used to define the solder paste for all pads in the footprint. If not set, the board solder_paste_ratio setting is used.
- The optional clearance token defines the clearance to all board copper objects for all pads in the footprint. If not set, the board clearance setting is used.
- The optional zone_connect token defines how all pads are connected to filled zone. If not defined, then the zone connect_pads setting is used. Valid connection types are integers values from 0 to 3 which defines:
  - 0 - Pads are not connect to zone.
  - 1 - Pads are connected to zone using thermal reliefs.
  - 2 - Pads are connected to zone using solid fill.
- The optional thermal_width token defined the thermal relief spoke width used for zone connections for all pads in the footprint. This only affects pads connected to zones with thermal reliefs. If not set, the zone thermal_width setting is used.
- The optional thermal_gap is the distance from the pad to the zone of thermal relief connections for all pads in the footprint. If not set, the zone thermal_gap setting is used. If not set, the zone thermal_gap setting is used.
- The optional attributes section defines the attributes of the footprint.
- An optional list of canonical layer names which are private to the footprint.
- An optional list of net-tie pad groups.
- The graphic objects section is a list of one or more graphical objects in the footprint. At a minimum, the reference designator and value text objects are defined. All other graphical objects are optional.
- The optional pads section is a list of pads in the footprint.
- The optional zones section is a list of keep out zones in the footprint.
- The optional groups section is a list of grouped objects in the footprint.
- The 3D model section defines the 3D model object associated with the footprint.

### Footprint Attributes

Footprint attr token defines the list of attributes of the footprint.

```
(attr
  TYPE                                                      
  [board_only]                                              
  [exclude_from_pos_files]                                  
  [exclude_from_bom]                                        
)
```

- The TYPE token defines the type of footprint. Valid footprint types are smd and through_hole.
- The optional board_only token indicates that the footprint is only defined in the board and has no reference to any schematic symbol.
- The optional exclude_from_pos_files token indicates that the footprint position information should not be included when creating position files.
- The optional exclude_from_bom token indicates that the footprint should be excluded when creating bill of materials (BOM) files.

### Net-tie Pad Groups

A space-separated list of quoted strings, each containing a comma-separated list of pad names. Nets attached to pads within a single pad-group are allowed to short.

### Footprint Graphics Items

Footprint graphical items define all of the drawing items that are used in the footprint definition. This includes text, text boxes, lines, rectangles, circles, arcs, polygons, curves, and dimensions.

Footprint graphic items starting with fp_ are not valid outside of a footprint definition.

### Footprint Images

See the images section. This section will not exist if there are no images on the footprint. Footprint images are not displayed on the PCB when a footprint is placed, only in the footprint editor.

### Footprint Text

The fp_text token defines text in a footprint definition.

```
(fp_text
  TYPE                                                      
  "TEXT"                                                    
  POSITION_IDENTIFIER                                       
  [unlocked]                                                
  (layer LAYER_DEFINITION)                                  
  [hide]                                                    
  (effects TEXT_EFFECTS)                                    
  (uuid UUID)                                               
)
```

- The TYPE attribute defines the type of text. Valid types are reference, value, and user.
- The "TEXT" attribute is a quoted string that defines the text.
- The POSITION_IDENTIFIER defines the X and Y position coordinates and optional orientation angle of the text.
- The optional unlocked token indicates if the text orientation can be anything other than the upright orientation.
- The layer token defines the canonical layer the text resides on.
- The optional [hide] token, defines if the text is hidden.
- The effects token defines how the text is displayed.
- The uuid token defines the unique identifier of the text object.

### Footprint Text Box

(from version 7)

The fp_text_box token defines a rectangle containing line-wrapped text.

```
(fp_text_box
  [locked]                                                    
  "TEXT"                                                      
  [(start X Y)]                                               
  [(end X Y)]                                                 
  [(pts (xy X Y) (xy X Y) (xy X Y) (xy X Y))]                 
  [(angle ROTATION)]                                          
  (layer LAYER_DEFINITION)                                    
  (uuid UUID)                                                 
  TEXT_EFFECTS                                                
  [STROKE_DEFINITION]                                         
  [(render_cache RENDER_CACHE)]                               
)
```

- The optional locked token specifies if the text box can be moved.
- The content of the text box
- The start token defines the top-left of a cardinally oriented text box.
- The end token defines the bottom-right of a cardinally oriented text box.
- The pts token defines the four corners of a non-cardianlly oriented text box. The corners must be in order, but the winding can be either direction.
- The optional angle token defines the rotation of the text box in degrees.
- The layer token defines the canonical layer the text box resides on.
- The uuid token defines the unique identifier of the text box.
- The TEXT_EFFECTS describe the style of the text in the text box.
- The STROKE_DEFINITION describes the style of an optional border to be drawn around the text box.
- If the TEXT_EFFECTS prescribe a TrueType font then a render cache should be given in case the font can not be found on the current system.
- If angle is not given, or is a cardinal angle (0, 90, 180 or 270), then the text box MUST have start and end tokens.
- If angle is given and is not a cardinal angle, then the text box MUST have a pts token (with 4 pts).

### Footprint Line

The fp_line token defines a graphic line in a footprint definition.

```
(fp_line
  (start X Y)                                               
  (end X Y)                                                 
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The start token defines the coordinates of the beginning of the line.
- The end token defines the coordinates of the end of the line.
- The layer token defines the canonical layer the line resides on.
- The width token defines the line width. (prior to version 7)
- The STROKE_DEFINITION describes the width and style of the line. (from version 7)
- The optional locked token defines if the line cannot be edited.
- The uuid token defines the unique identifier of the line object.

### Footprint Rectangle

The fp_rect token defines a graphic rectangle in a footprint definition.

```
(fp_rect
  (start X Y)                                               
  (end X Y)                                                 
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(fill yes | no)]                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The start token defines the coordinates of the upper left corner of the rectangle.
- The end token defines the coordinates of the low right corner of the rectangle.
- The layer token defines the canonical layer the rectangle resides on.
- The width token defines the line width of the rectangle. (prior to version 7)
- The STROKE_DEFINITION describes the line width and style of the rectangle. (from version 7)
- The optional fill token defines if the rectangle is filled. If not defined, the rectangle is not filled.
- The optional locked token defines if the rectangle cannot be edited.
- The uuid token defines the unique identifier of the rectangle object.

### Footprint Circle

The fp_circle token defines a graphic circle in a footprint definition.

```
(fp_circle
  (center X Y)                                              
  (end X Y)                                                 
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(fill yes | no)]                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The center token defines the coordinates of the center of the circle.
- The end token defines the coordinates of the end of the radius of the circle.
- The layer token defines the canonical layer the circle resides on.
- The width token defines the line width of the circle. (prior to version 7)
- The STROKE_DEFINITION describes the line width and style of the circle. (from version 7)
- The optional fill token defines if the circle is filled. If not defined, the circle is not filled.
- The optional locked token defines if the circle cannot be edited.
- The uuid token defines the unique identifier of the circle object.

### Footprint Arc

The fp_arc token defines a graphic arc in a footprint definition.

```
(fp_arc
  (start X Y)                                               
  (mid X Y)                                                 
  (end X Y)                                                 
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The start token defines the coordinates of the start position of the arc radius.
- The mid token defines the coordinates of the midpoint along the arc.
- The end token defines the coordinates of the end position of the arc radius.
- The layer token defines the canonical layer the arc resides on.
- The width token defines the line width of the arc. (prior to version 7)
- The STROKE_DEFINITION describes the line width and style of the arc. (from version 7)
- The optional locked token defines if the arc cannot be edited.
- The uuid token defines the unique identifier of the arc object.

### Footprint Polygon

The fp_poly token defines a graphic polygon in a footprint definition.

```
(fp_poly
  COORDINATE_POINT_LIST                                     
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(fill yes | no)]                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The COORDINATE_POINT_LIST defines the list of X/Y coordinates of the polygon outline.
- The layer token defines the canonical layer the polygon resides on.
- The width token defines the line width of the polygon. (prior to version 7)
- The STROKE_DEFINITION describes the line width and style of the polygon. (from version 7)
- The optional fill token defines if the polygon is filled. If not defined, the polygon is not filled.
- The optional locked token defines if the polygon cannot be edited.
- The uuid token defines the unique identifier of the polygon object.

### Footprint Curve

The fp_curve token defines a graphic Cubic Bezier curve in a footprint definition.

```
(fp_curve
  COORDINATE_POINT_LIST                                     
  (layer LAYER_DEFINITION)                                  
  (width WIDTH)                                             
  STROKE_DEFINITION                                         
  [(locked)]                                                
  (uuid UUID)                                               
)
```

- The COORDINATE_POINT_LIST defines the four X/Y coordinates of each point of the curve.
- The layer token defines the canonical layer the curve resides on.
- The width token defines the line width of the curve. (prior to version 7)
- The STROKE_DEFINITION describes the line width and style of the curve. (from version 7)
- The optional locked token defines if the curve cannot be edited.
- The uuid token defines the unique identifier of the curve object.

### Footprint Pad

The pad token defines a pad in a footprint definition.

```
(pad
  "NUMBER"                                                  
  TYPE                                                      
  SHAPE                                                     
  POSITION_IDENTIFIER                                       
  [(locked)]                                                
  (size X Y)                                                
  [(drill DRILL_DEFINITION)]                                
  (layers "CANONICAL_LAYER_LIST")                           
  [(property PROPERTY)]                                     
  [(remove_unused_layer)]                                   
  [(keep_end_layers)]                                       
  [(roundrect_rratio RATIO)]                                
  [(chamfer_ratio RATIO)]                                   
  [(chamfer CORNER_LIST)]                                   
  (net NUMBER "NAME")                                       
  (uuid UUID)                                               
  [(pinfunction "PIN_FUNCTION")]                            
  [(pintype "PIN_TYPE")]                                    
  [(die_length LENGTH)]                                     
  [(solder_mask_margin MARGIN)]                             
  [(solder_paste_margin MARGIN)]                            
  [(solder_paste_margin_ratio RATIO)]                       
  [(clearance CLEARANCE)]                                   
  [(zone_connect ZONE)]                                     
  [(thermal_width WIDTH)]                                   
  [(thermal_gap DISTANCE)]                                  
  [CUSTOM_PAD_OPTIONS]                                      
  [CUSTOM_PAD_PRIMITIVES]                                   
)
```

- The "NUMBER" attribute is the pad number.
- The pad TYPE can be defined as thru_hole, smd, connect, or np_thru_hole.
- The pad SHAPE can be defined as circle, rect, oval, trapezoid, roundrect, or custom.
- The POSITION_IDENTIFIER defines the X and Y coordinates and optional orientation angle of the pad.
- The optional locked token defines if the footprint pad can be edited.
- The size token defines the width and height of the pad.
- The optional pad DRILL_DEFINITION defines the pad drill requirements.
- The layers token defines the layer or layers the pad reside on.
- The optional property token defines any special properties for the pad. Valid properties are pad_prop_bga, pad_prop_fiducial_glob, pad_prop_fiducial_loc, pad_prop_testpoint, pad_prop_heatsink, pad_prop_heatsink, and pad_prop_castellated.
- The optional remove_unused_layer token specifies that the copper should be removed from any layers the pad is not connected to.
- The optional keep_end_layers token specifies that the top and bottom layers should be retained when removing the copper from unused layers.
- The optional roundrect_rratio token defines the scaling factor of the pad to corner radius for rounded rectangular and chamfered corner rectangular pads. The scaling factor is a number between 0 and 1.
- The optional chamfer_ratio token defines the scaling factor of the pad to chamfer size. The scaling factor is a number between 0 and 1.
- The optional chamfer token defines a list of one or more rectangular pad corners that get chamfered. Valid chamfer corner attributes are top_left, top_right, bottom_left, and bottom_right.
- The optional net token defines the integer number and name string of the net connection for the pad.
- The uuid token defines the unique identifier of the pad object.
- The optional pinfunction token attribute defines the associated schematic symbol pin name.
- The optional pintype token attribute defines the associated schematic pin electrical type.
- The optional die_length token attribute defines the die length between the component pad and physical chip inside the component package.
- The optional solder_mask_margin token attribute defines the distance between the pad and the solder mask for the pad. If not set, the footprint solder_mask_margin is used.
- The optional solder_paste_margin token attribute defines the distance the solder paste should be changed for the pad.
- The optional solder_paste_margin_ratio token attribute defines the percentage to reduce the pad outline by to generate the solder paste size.
- The optional clearance token attribute defines the clearance from all copper to the pad. If not set, the footprint clearance is used.
- The optional zone_connection token attribute defines type of zone connect for the pad. If not defined, the footprint zone_connection setting is used. Valid connection types are integers values from 0 to 3 which defines:
  - 0 - Pad is not connect to zone.
  - 1 - Pad is connected to zone using thermal relief.
  - 2 - Pad is connected to zone using solid fill.
- The optional thermal_width token attribute defines the thermal relief spoke width used for zone connection for the pad. This only affects a pad connected to a zone with a thermal relief. If not set, the footprint thermal_width setting is used.
- The optional thermal_gap token attribute defines the distance from the pad to the zone of the thermal relief connection for the pad. This only affects a pad connected to a zone with a thermal relief. If not set, the footprint thermal_gap setting is used.
- The optional custom pad options defines the options when a custom pad is defined.
- The optional custom pad primitives defines the drawing objects and options used to define a custom pad.

### Pad Drill Definition

The drill token defines the drill attributes for a footprint pad.

```
(drill
  [oval]                                                  
  DIAMETER                                                
  [WIDTH]                                                 
  [(offset X Y)]                                          
)
```

- The optional oval token defines if the drill is oval instead of round.
- The diameter attribute defines the drill diameter.
- The optional width attribute defines the width of the slot for oval drills.
- The optional offset token defines the drill offset coordinates from the center of the pad.

### Custom Pad Options

The optional options token attributes define the settings used for custom pads. This token is only used when a custom pad is defined.

```
(options
  (clearance CLEARANCE_TYPE)                              
  (anchor PAD_SHAPE)                                      
)
```

- The clearance token defines the type of clearance used for a custom pad. Valid clearance types are outline and convexhull.
- The anchor token defines the anchor pad shape of a custom pad. Valid anchor pad shapes are rect and circle.

### Custom Pad Primitives

The optional primitives token defines a list of graphical items used to define the outline of a custom pad shape. This token is only used when a custom pad is defined.

```
(primitives
  GRAPHIC_ITEMS...                                        
  (width WIDTH)                                           
  [(fill yes)]                                            
)
```

- The graphical items is a list of graphical lines, rectangles, arcs, circles, curves, polygons, and annotation bounding boxes that define the shape of the custom pad (annotation bounding boxes from version 7). The item definitions only include the geometrical information that defines the item. The annotation bounding box defines the location (and size) of the pad number and netname.
- The width token defines the line width of the graphical items.
- The optional fill token attribute yes indicates the geometry defined by the graphical items should be filled.

### Footprint 3D Model

The model token defines the 3D model associated with a footprint.

```
(model
  "3D_MODEL_FILE"                                           
  (at (xyz X Y Z))                                          
  (scale (xyz X Y Z))                                       
  (rotate (xyz X Y Z))                                      
)
```

- The 3D_MODEL_FILE attribute is the path and file name of the 3D model.
- The at token specifies the 3D position coordinates of the model relative to the footprint.
- The scale token specifies the model scale factor for each 3D axis.
- The rotate token specifies the model rotation for each 3D axis relative to the footprint.

### Graphic Items

The graphical items are footprint and board items that are outside of the connectivity items. This includes graphical items on technical, user, and copper layers. Graphical items are also used to define complex pad geometries.

### Graphical Text

The gr_text token defines graphical text.

```
(gr_text
  "TEXT"                                                      
  POSITION_INDENTIFIER                                        
  (layer LAYER_DEFINITION [knockout])                         
  (uuid UUID)                                                 
  (effects TEXT_EFFECTS)                                      
)
```

- The "TEXT" attribute is a quoted string that defines the text.
- The POSITION_IDENTIFER defines the X and Y coordinates and optional orientation angle of the text.
- The layer token defines the canonical layer the text resides on. It is optionally followed by a knockout token indicating the text should be knocked out.
- The uuid token defines the unique identifier of the text object.
- The TEXT_EFFECTS defines how the text is displayed.

### Graphical Text Box

(from version 7)

The gr_text_box token defines a rectangle containing line-wrapped text.

```
(gr_text_box
  [locked]                                                    
  "TEXT"                                                      
  [(start X Y)]                                               
  [(end X Y)]                                                 
  [(pts (xy X Y) (xy X Y) (xy X Y) (xy X Y))]                 
  [(angle ROTATION)]                                          
  (layer LAYER_DEFINITION)                                    
  (uuid UUID)                                                 
  TEXT_EFFECTS                                                
  [STROKE_DEFINITION]                                         
  [(render_cache RENDER_CACHE)]                               
)
```

- The optional locked token specifies if the text box can be moved.
- The content of the text box
- The start token defines the top-left of a cardinally oriented text box.
- The end token defines the bottom-right of a cardinally oriented text box.
- The pts token defines the four corners of a non-cardinally oriented text box. The corners must be in order, but the winding can be either direction.
- The optional angle token defines the rotation of the text box in degrees.
- The layer token defines the canonical layer the text box resides on.
- The uuid token defines the unique identifier of the text box.
- The TEXT_EFFECTS describe the style of the text in the text box.
- The STROKE_DEFINITION describes the style of an optional border to be drawn around the text box.
- If the TEXT_EFFECTS prescribe a TrueType font then a render cache should be given in case the font can not be found on the current system.
- If angle is not given, or is a cardinal angle (0, 90, 180 or 270), then the text box MUST have start and end tokens.
- If angle is given and is not a cardinal angle, then the text box MUST have a pts token (with 4 pts).

### Graphical Line

The gr_line token defines a graphical line.

```
(gr_line
  (start X Y)                                                 
  (end X Y)                                                   
  [(angle ANGLE)]                                             
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  (uuid UUID)                                                 
)
```

- The start token defines the coordinates of the beginning of the line.
- The end token defines the coordinates of the end of the line.
- The optional angle token defines the rotational angle of the line.
- The layer token defines the canonical layer the line resides on.
- The width token defines the line width.
- The uuid token defines the unique identifier of the line object.

### Graphical Rectangle

The gr_rect token defines a graphical rectangle.

```
(gr_rect
  (start X Y)                                                 
  (end X Y)                                                   
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  [(fill yes | no)]                                           
  (uuid UUID)                                                 
)
```

- The start token defines the coordinates of the upper left corner of the rectangle.
- The end token defines the coordinates of the low right corner of the rectangle.
- The layer token defines the canonical layer the rectangle resides on.
- The width token defines the line width of the rectangle.
- The optional fill token defines how the rectangle is filled. If not defined, the rectangle is not filled.
- The uuid token defines the unique identifier of the rectangle object.

### Graphical Circle

The gr_circle token defines a graphical circle.

```
(gr_circle
  (center X Y)                                                
  (end X Y)                                                   
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  [(fill yes | no)]                                           
  (uuid UUID)                                                 
)
```

- The center token defines the coordinates of the center of the circle.
- The end token defines the coordinates of the end of the radius of the circle.
- The layer token defines the canonical layer the circle resides on.
- The width token defines the line width of the circle.
- The optional fill token defines how the circle is filled. If not defined, the circle is not filled.
- The uuid token defines the unique identifier of the circle object.

### Graphical Arc

The gr_arc token defines a graphical arc.

```
(gr_arc
  (start X Y)                                                 
  (mid X Y)                                                   
  (end X Y)                                                   
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  (uuid UUID)                                                 
)
```

- The start token defines the coordinates of the start position of the arc radius.
- The mid token defines the coordinates of the midpoint along the arc.
- The end token defines the coordinates of the end position of the arc radius.
- The layer token defines the canonical layer the arc resides on.
- The width token defines the line width of the arc.
- The uuid token defines the unique identifier of the arc object.

### Graphical Polygon

The gr_poly token defines a graphical polygon.

```
(gr_poly
  COORDINATE_POINT_LIST                                       
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  [(fill yes | no)]                                           
  (uuid UUID)                                                 
)
```

- The COORDINATE_POINT_LIST defines the list of X/Y coordinates of the polygon outline.
- The layer token defines the canonical layer the polygon resides on.
- The width token defines the line width of the polygon.
- The optional fill token defines how the polygon is filled. If not defined, the polygon is not filled.
- The uuid token defines the unique identifier of the polygon object.

### Graphical Curve

The bezier token defines a graphic Cubic Bezier curve.

```
(bezier
  COORDINATE_POINT_LIST                                       
  (layer LAYER_DEFINITION)                                    
  (width WIDTH)                                               
  (uuid UUID)                                                 
)
```

- The COORDINATE_POINT_LIST defines the list of X/Y coordinates of the four points of the curve.
- The layer token defines the canonical layer the curve resides on.
- The width token defines the line width of the curve.
- The uuid token defines the unique identifier of the curve object.

### Annotation Bounding Box

(from version 7)

The gr_bbox token defines a bounding box inside which annotations (such as pad numbers and netnames) will be shown.

```
(gr_bbox
  (start X Y)                                                 
  (end X Y)                                                   
)
```

- The start token defines the coordinates of the upper left corner of the rectangle.
- The end token defines the coordinates of the low right corner of the rectangle.

### Dimension

The dimension token defines a dimension object.

```
(dimension
  [locked]                                                    
  (type DIMENSION_TYPE)                                       
  (layer LAYER_DEFINITION)                                    
  (uuid UUID)                                                 
  (pts (xy X Y) (xy X Y))                                     
  [(height HEIGHT)]                                           
  [(orientation ORIENTATION)]                                 
  [(leader_length LEADER_LENGTH)]                             
  [(gr_text GRAPHICAL_TEXT)]                                  
  [(format DIMENSION_FORMAT)]                                 
  (style DIMENSION_STYLE)                                     
)
```

- The optional locked token specifies if the dimension can be moved.
- The type token attribute defines the type of dimension. Valid dimension types are aligned, leader, center, orthogonal, and radial (radial from version 7).
- The layer token defines the canonical layer the polygon resides on.
- The uuid token defines the unique identifier of the dimension object.
- The pts token attributes define the list of xy coordinates of the dimension.
- The optional height token attribute defines the height of aligned dimensions.
- The optional orientation token attribute defines the rotation angle for orthogonal dimensions.
- The optional leader_length token attribute defines the distance from the marked radius to the knee for radial dimensions.
- The optional gr_text token attributes define the dimension text formatting for all dimension types except center dimensions.
- The optional format token attributes define the dimension formatting for all dimension types except center dimensions.
- The style token attributes define the dimension style information.

### Dimension Format

The format token attributes define the text formatting of the dimension.

```
(format
  [(prefix "PREFIX")]                                       
  [(suffix "SUFFIX")]                                       
  (units UNITS)                                             
  (units_format UNITS_FORMAT)                               
  (precision PRECISION)                                     
  [(override_value "VALUE")]                                
  [suppress_zeros]                                          
)
```

- The optional prefix token attribute defines the string to add to the beginning of the dimension text.
- The optional suffix token attribute defines the string to add to the end of the dimension text.
- The units token attribute defines the dimension units used to display the dimension text. Valid units are as follows:
  - 0 - Inches.
  - 1 - Mils.
  - 2 - Millimeters.
  - 3 - Automatic.
- The units_format token attribute defines how the unit's suffix is formatted. Valid units formats are as follows:
  - 0 - No suffix.
  - 1 - Bare suffix.
  - 2 - Wrap suffix in parenthesis.
- The precision token attribute defines the number of significant digits to display. From version 7, a precision above 5 indicates a units-scaled precision:
  - 6 - 0.00 in / 0 mils / 0.0 mm
  - 7 - 0.000 in / 0 mils / 0.00 mm
  - 8 - 0.0000 in / 0.0 mils / 0.000mm
  - 9 - 0.00000 in / 0.00 mils / 0.0000mm
- The optional override_value token attribute defines the text to substitute for the actual physical dimension.
- The optional suppress_zeros token removes all trailing zeros from the dimension text.

### Dimension Style

```
(style
  (thickness THICKNESS)                                     
  (arrow_length LENGTH)                                     
  (text_position_mode MODE)                                 
  [(extension_height HEIGHT)]                               
  [(text_frame TEXT_FRAME_TYPE)]                            
  [(extension_offset OFFSET)]                               
  [(keep_text_aligned yes | no)]                            
)
```

- The thickness token attribute defines the line thickness of the dimension.
- The arrow_length token attribute defines the length of the dimension arrows.
- The text_position_mode token attribute defines the position mode of the dimension text. Valid position modes are as follows:
  - 0 - Text is outside the dimension line.
  - 1 - Text is in line with the dimension line.
  - 2 - Text has been manually placed by the user.
- The optional extension_height token attribute defines the length of the extension lines past the dimension crossbar.
- The optional text_frame token attribute defines the style of the frame around the dimension text. This only applies to leader dimensions. Valid text frames are as follows:
  - 0 - No text frame.
  - 1 - Rectangle.
  - 2 - Circle.
  - 3 - Rounded rectangle.
- The optional extension_offset token attribute defines the distance from feature points to extension line start.
- The optional keep_text_aligned token indicates that the dimension text should be kept in line with the dimension crossbar. When not defined, the dimension text is shown horizontally regardless of the orientation of the dimension.

### Zone

The zone token defines a zone on the board or footprint. Zones serve two purposes in KiCad: filled copper zones and keep out areas.

```
(zone
  (net NET_NUMBER)                                            
  (net_name "NET_NAME")                                       
  (layer LAYER_DEFINITION)                                    
  (uuid UUID)                                                 
  [(name "NAME")]                                             
  (hatch STYLE PITCH)                                         
  [(priority PRIORITY)]                                       
  (connect_pads [CONNECTION_TYPE] (clearance CLEARANCE))      
  (min_thickness THICKNESS)                                   
  [(filled_areas_thickness no)]                               
  [ZONE_KEEPOUT_SETTINGS]                                     
  ZONE_FILL_SETTINGS                                          
  (polygon COORDINATE_POINT_LIST)                             
  [ZONE_FILL_POLYGONS...]                                     
  [ZONE_FILL_SEGMENTS...]                                     
)
```

- The net token attribute defines by the net ordinal number which net in the nets section that the zone is part of.
- The net_name token attribute defines the name of the net if the zone is not a keep out area. The net name attribute will be an empty string if the zone is a keep out area.
- The layer token defines the canonical layer the zone resides on.
- The uuid token defines the unique identifier of the zone object.
- The optional name token attribute defines the name of the zone if one has been assigned.
- The hatch token attributes define the zone outline display hatch style and pitch. Valid hatch styles are none, edge, and full.
- The optional priority attribute defines the zone priority if it is not zero.
- The connect_pads token attributes define the pad connection type and clearance. Valid pad connection types are thru_hole_only, full, and no. If the pad connection type is not defined, thermal relief pad connections are used.
- The min_thickness token attributed defines the minimum fill width allowed in the zone.
- The optional filled_areas_thickness attribute no specifies if the zone like width is not used when determining the zone fill area. This is to maintain compatibility with older board files that included the line thickness when performing zone fills when it is not defined.
- The optional zone keep out settings section defines the keep out items if the zone defines as a keep out area.
- The zone fill settings section defines how the zone is to be filled.
  - 0 - All footprint pads are not connect to zone.
  - 1 - All footprint pads are connected to zone using thermal relief.
  - 2 - All footprint pads are connected to zone using solid fill.
  - 3 - Only footprint through hole pads are connected to zone using thermal relief. Surface mount pads are connected using solid fill.
- The polygon token attribute defines the COORDINATE_POINT_LIST of X/Y coordinates of corner points of the polygon outline. the corners of the zone outline polygon.
- The optional zone fill polygons section defines all of the polygons used to fill the zone. This section will not exist if the zone has not been filled or is filled with segments.
- The optional zone fill segments section defines a list of track segments used to fill the zone. This is only used when boards prior to version 4 of KiCad are loaded.

### Zone Keep Out Settings

The optional keepout token attributes define which objects should be kept out of the zone. This section only applies to keep out zones.

```
(keepout
  (tracks KEEPOUT)                                          
  (vias KEEPOUT)                                            
  (pads KEEPOUT)                                            
  (copperpour KEEPOUT)                                      
  (footprints KEEPOUT)                                      
)
```

- The tracks token attribute defines whether or not tracks should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
- The vias token attribute defines whether or not vias should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
- The pads token attribute defines whether or not pads should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
- The copperpour token attribute defines whether or not copper pours should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
- The footprints token attribute defines whether or not footprints should be excluded from the keep out area. Valid attributes are allowed and not_allowed.

### Zone Fill Settings

The fill token attributes define how the zone is to be filled.

```
(fill
  [yes]                                                     
  [(mode FILL_MODE)]                                        
  (thermal_gap GAP)                                         
  (thermal_bridge_width WIDTH)                              
  [(smoothing STYLE)]                                       
  [(radius RADIUS)]                                         
  [(island_removal_mode MODE)]                              
  [(island_area_min AREA)]                                  
  [(hatch_thickness THICKNESS)]                             
  [(hatch_gap GAP)]                                         
  [(hatch_orientation ORIENTATION)]                         
  [(hatch_smoothing_level LEVEL)]                           
  [(hatch_smoothing_value VALUE)]                           
  [(hatch_border_algorithm TYPE)]                           
  [(hatch_min_hole_area AREA)]                              
)
```

- The yes token specifies if the zone should be filled. If not specified, the zone is not filled and no additional attributes are required.
- The optional mode token attribute defines how the zone is filled. The only valid fill mode is hatched. When not defined, the fill mode is solid.
- The optional thermal_gap token attribute defines the distance from the zone to all pad thermal relief connections to the zone.
- The optional thermal_bridge_width token attribute defines the spoke width for all pad thermal relief connection to the zone.
- The optional smoothing token attributes define the style of corner smoothing. Valid smoothing styles are chamfer and fillet.
- The optional radius token defines the radius of the corner smoothing.
- The optional island_removal_mode token attribute defines the island removal mode. Valid island removal modes are:
  - 0 - Always remove islands.
  - 1 - Never remove islands.
  - 2 - Minimum area island to allow.
- The optional island_area_min token attribute defines the minimum allowable zone island. This only valid when the remove islands mode is set to 2.
- The optional hatch_thickness token attribute defines the thickness for hatched fills.
- The optional hatch_gap token attribute defines the distance between lines for hatched fills.
- The optional hatch_orientation token attribute defines the line angle for hatched fills.
- The optional hatch_smoothing_level token attribute defines how hatch outlines are smoothed. Valid hatch smoothing levels are:
  - 0 - No smoothing.
  - 1 - Fillet.
  - 2 - Arc minimum.
  - 3 - Arc maximum.
- The optional hatch_smoothing_value token attribute defines the ratio between the hole and the chamfer/fillet size.
- The optional hatch_border_algorithm token attribute defines the if the zone line thickness is used when performing a hatch fill. Valid values for the hatch border algorithm are:
  - 0 - Use zone minimum thickness.
  - 1 - Use hatch thickness.
- The optional hatch_min_hole_area token attribute defines the minimum area a hatch file hole can be.

### Zone Fill Polygons

The filled_polygon token defines the polygons used to fill the zone. This token will not exist if the zone has not been filled.

```
(filled_polygon
  (layer LAYER_DEFINITION)                                  
  COORDINATE_POINT_LIST                                     
)
```

- The layer token attribute defines the canonical layer the zone fill resides on.
- The COORDINATE_POINT_LIST defines the list of polygon X/Y coordinates used to fill the zone.

### Zone Fill Segments

The filled_segments token defines the segments used to fill the zone. This is only used when loading boards prior to version 4 which filled zones with segments. Once the zone has been refilled, it will be filled with polygons and this token will not exist.

```
(fill_segments
  (layer LAYER_DEFINITION)                                  
  COORDINATED_POINT_LIST                                    
)
```

- The layer token attribute defines the canonical layer the zone fill resides on.
- The COORDINATE_POINT_LIST defines the list of X and Y coordinates of the segments used to fill the zone.

### Group

The group token defines a group of items.

```
(group
  "NAME"                                                      
  (id UUID)                                                   
  (members UUID1 ... UUIDN)                                   
)
```

- The name attribute defines the name of the group.
- The id token attribute defines the unique identifier of the group.
- The members token attributes define a list of unique identifiers of the objects belonging to the group.

## Schematic and Symbol Library Common Syntax

This section defines all syntax that is shared across the symbol library and schematic file formats.

### Schematic Coordinates

The minimum internal unit for schematic and symbol library files is one nanometer so there is maximum resolution of four decimal places or 0.0001 mm. Any precision beyond four places will be truncated.

### Symbol Unit Identifier

Symbol unit identifiers define how symbol units are identified. The unit identifier is a quoted string have the format "NAME_UNIT_STYLE". "NAME" is the parent symbol name. "UNIT" is an integer that identifies which unit the symbol represents. A "UNIT" value of zero (0) indicates that the symbol is common to all units. The "STYLE" indicates which body style the unit represents.

This identifier is a temporary solution until the full symbol inheritance model is implemented.

KiCad only supports two body styles so the only valid values for the "STYLE" are 1 and 2.

### Fill Definition

The fill token defines how schematic and symbol library graphical items are filled.

```
(fill
  (type none | outline | background)                          
)
```

The fill token attributes define how the arc is filled. The table below describes the fill type modes.

The table below defines the schematic and symbol graphical object fill modes.
| Token | Description |
|-------|-------------|
| none | Graphic item not filled. |
| outline | Graphic item filled with the line color. |
| background | Graphic filled with the theme background color. |

### Symbols

The symbol token defines a symbol or sub-unit of a parent symbol. There can be zero or more symbol tokens in a symbol library file.

```
(symbol
  "LIBRARY_ID" | "UNIT_ID"                                    
  [(extends "LIBRARY_ID")]                                    
  [(pin_numbers hide)]                                        
  [(pin_names [(offset OFFSET)] hide)]                        
  (in_bom yes | no)                                           
  (on_board yes | no)                                         
  SYMBOL_PROPERTIES...                                        
  GRAPHIC_ITEMS...                                            
  PINS...                                                     
  UNITS...                                                    
  [(unit_name "UNIT_NAME")]                                   
)
```

- Each symbol must have a unique "LIBRARY_ID" for each top level symbol in the library or a unique "UNIT_ID" for each unit embedded in a parent symbol. Library identifiers are only valid it top level symbols and unit identifiers are on valid as unit symbols inside a parent symbol.
- The optional extends token attribute defines the "LIBRARY_ID" of another symbol inside the current library from which to derive a new symbol. Extended symbols currently can only have different SYMBOL_PROPERTIES than their parent symbol.
- The optional pin_numbers token defines the visibility setting of the symbol pin numbers for the entire symbol. If not defined, the all of the pin numbers in the symbol are visible.
- The optional pin_names token defines the attributes for all of the pin names of the symbol. The optional offset token defines the pin name offset for all pin names of the symbol. If not defined, the pin name offset is 0.508mm (0.020"). If the pin_name token is not defined, the all symbol pins are shown with the default offset.
- The in_bom token, defines if a symbol is to be include in the bill of material output. The only valid attributes are yes and no.
- The on_board token, defines if a symbol is to be exported from the schematic to the printed circuit board. The only valid attributes are yes and no.
- The SYMBOL_PROPERTIES is a list of properties that define the symbol. The following properties are mandatory when defining a parent symbol: "Reference", "Value", "Footprint", and "Datasheet". All other properties are optional. Unit symbols cannot have any properties.
- The GRAPHIC ITEMS section is list of graphical arcs, circles, curves, lines, polygons, rectangles and text that define the symbol drawing. This section can be empty if the symbol has no graphical items.
- The PINS section is a list of pins that are used by the symbol. This section can be empty if the symbol does not have any pins.
- The optional UNITS can be one or more child symbol tokens embedded in a parent symbol.
- The optional unit_name token defines the display name of a subunit in the symbol editor and symbol chooser. It is only permitted for child symbol tokens embedded in a parent symbol.

### Symbol Properties

The property token defines a symbol property when used inside a symbol definition.
Symbol properties are different than general purpose properties defined above.

```
(property
  "KEY"                                                     
  "VALUE"                                                   
  (id N)                                                    
  POSITION_IDENTIFIER                                       
  TEXT_EFFECTS                                              
)
```

- The "KEY" string defines the name of the property and must be unique.
- The "VALUE" string defines the value of the property.
- The id token defines an integer ID for the property and must be unique.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the property.
- The TEXT_EFFECTS section defines how the text is displayed.

### Mandatory Symbol Properties

The table below defines the mandatory properties for parent symbols.

| Key | Ordinal | Description | Empty Allowed |
|-----|---------|-------------|---------------|
| Reference | 0 | Symbol reference designator | No |
| Value | 1 | Symbol value string | No |
| Footprint | 2 | Symbol footprint library identifier | Yes |
| Datasheet | 3 | Symbol datasheet link | Yes |

### Reserved Symbol Property Keys

The list below is the list of property keys reserve by KiCad and cannot be user for user defined properties.

- ki_keywords
- ki_description
- ki_locked
- ki_fp_filters

### Symbol Graphic Items

This section documents the various graphical objects used in symbol definitions.

### Symbol Arc

The arc token defines a graphical arc in a symbol definition.

```
(arc
  (start X Y)                                                 
  (mid X Y)                                                   
  (end X Y)                                                   
  STROKE_DEFINITION                                           
  FILL_DEFINITION                                             
)
```

- The start token defines the coordinates of start point of the arc.
- The mid token defines the coordinates of mid point of the arc.
- The end token defines the coordinates of end point of the arc.
- The STROKE_DEFINITION defines how the arc outline is drawn.
- The fill token attributes define how the arc is filled.

### Symbol Circle

The circle token defines a graphical circle in a symbol definition.

```
(circle
  (center X Y)                                                
  (radius RADIUS)                                             
  STROKE_DEFINITION                                           
  FILL_DEFINITION                                             
)
```

- The center token defines the coordinates of center point of the circle.
- The radius token defines the length of the radius of the circle.
- The STROKE_DEFINITION defines how the circle outline is drawn.
- The FILL_DEFINTION defines how the circle is filled.

### Symbol Curve

The bezier token defines a graphical Cubic Bezier curve.

```
(bezier
  COORDINATE_POINT_LIST                                       
  STROKE_DEFINITION                                           
  FILL_DEFINITION                                             
)
```

- The COORDINATE_POINT_LIST defines the four X/Y coordinates of each point of the curve.
- The STROKE_DEFINITION defines how the curve outline is drawn.
- The FILL_DEFINTION defines how the curve is filled.

### Symbol Line

The polyline token defines one or more graphical lines that may or may not define a polygon.

```
(polyline
  COORDINATE_POINT_LIST                                       
  STROKE_DEFINITION                                           
  FILL_DEFINITION                                             
)
```

- The COORDINATE_POINT_LIST defines the list of X/Y coordinates of the line(s). There must be a minimum of two points.
- The STROKE_DEFINITION defines how the polygon formed by the lines outline is drawn.
- The fill token attributes define how the polygon formed by the lines is filled.

### Symbol Rectangle

The rectangle token defines a graphical rectangle in a symbol definition.

```
(rectangle
  (start X Y)                                                 
  (end X Y)                                                   
  STROKE_DEFINITION                                           
  FILL_DEFINITION                                             
)
```

- The start token attributes define the coordinates of the start point of the rectangle.
- The end token attributes define the coordinates of the end point of the rectangle.
- The STROKE_DEFINITION defines how the rectangle outline is drawn.
- The FILL_DEFINTION defines how the rectangle is filled.

### Symbol Text

The text token defines graphical text in a symbol definition.

```
(text
  "TEXT"                                                      
  POSITION_IDENTIFIER                                         
  (effects TEXT_EFFECTS)                                      
)
```

- The "TEXT" attribute is a quoted string that defines the text.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the text.
- The TEXT_EFFECTS defines how the text is displayed.

### Symbol Pin

The pin token defines a pin in a symbol definition.

```
(pin
  PIN_ELECTRICAL_TYPE                                         
  PIN_GRAPHIC_STYLE                                           
  POSITION_IDENTIFIER                                         
  (length LENGTH)                                             
  (name "NAME" TEXT_EFFECTS)                                  
  (number "NUMBER" TEXT_EFFECTS)                              
)
```

- The PIN_ELECTRICAL_TYPE defines the pin electrical connection. See table below for valid pin electrical connection types and descriptions.
- The PIN_GRAPHICAL_STYLE defines the graphical style used to draw the pin. See table below for valid pin graphical styles and descriptions.
- The POSITION_IDENTIFIER defines the X and Y coordinates and rotation angle of the connection point of the pin relative to the symbol origin position. The only supported rotation angles for pins are 0, 90, 180, and 270 degrees.
- The length token attribute defines the LENGTH of the pin.
- The name token defines a quoted string containing the NAME of the pin and the TEXT_EFFECTS defines how the text is displayed.
- The number token defines a quoted string containing the NUMBER of the pin and the TEXT_EFFECTS defines how the text is displayed.

### Pin Electrical Types

The table below defines the pin electrical types.

| Token | Description |
|-------|-------------|
| input | Pin is an input. |
| output | Pin is an output. |
| bidirectional | Pin can be both input and output. |
| tri_state | Pin is a tri-state output. |
| passive | Pin is electrically passive. |
| free | Not internally connected. |
| unspecified | Pin does not have a specified electrical type. |
| power_in | Pin is a power input. |
| power_out | Pin is a power output. |
| open_collector | Pin is an open collector output. |
| open_emitter | Pin is an open emitter output. |
| no_connect | Pin has no electrical connection. |

### Pin Graphical Styles

The table below defines the pin graphical styles.

| Token | Description |
|-------|-------------|
| line | Normal pin shape |
| inverted | Inverted pin shape |
| clock | Clock pin shape |
| inverted_clock | Inverted clock pin shape |
| input_low | Active low input pin shape |
| clock_low | Active low clock pin shape |
| output_low | Active low output pin shape |
| edge_clock_high | Falling edge clock pin shape |
| non_logic | Non-logic pin shape |