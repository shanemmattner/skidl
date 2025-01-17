Symbol Library File Format
Introduction

This documents the s-expression symbol library file format for all versions of KiCad from 6.0.

    Symbol library files use the .kicad_sym extension.

    Symbol library files can define one or more symbols.

Layout

A symbol library file includes the following sections:

    Header

    Symbol Definition

Header Section

The kicad_symbol_lib token indicates that it is KiCad symbol library file. This section is required.
	Third party scripts should not use kicad_symbol_editor as the generator identifier. Please use some other identifier so that bugs introduced by third party generators are not confused with a footprint library file created by KiCad.

(kicad_symbol_lib
  (version VERSION)                                             
  (generator GENERATOR)                                         

  ;; contents of the symbol library file...                     
)

	The version token attribute defines the symbol library version using the YYYYMMDD date format.
	The generator token attribute defines the program used to write the file.
	The symbol definitions go here. Symbol library files can have zero or more symbols.
Symbol Section

The symbol token defines a symbol in the library.

  [SYMBOL_DEFINITION]                                        
  ...

	The SYMBOL_DEFINITION defines the symbol(s) in the library file.
Last Modified 2024-01-31
