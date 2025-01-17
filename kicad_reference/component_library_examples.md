This file contains examples of KiCad 8 components from various .kicad_sym libraries



From Device.kicad_sym:

R (basic resistor):
	(symbol "R"
		(pin_numbers hide)
		(pin_names
			(offset 0)
		)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "R"
			(at 2.032 0 90)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "R"
			(at 0 0 90)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at -1.778 0 90)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Resistor"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "R res resistor"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "R_*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "R_0_1"
			(rectangle
				(start -1.016 -2.54)
				(end 1.016 2.54)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "R_1_1"
			(pin passive line
				(at 0 3.81 270)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 -3.81 90)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_______

C (basic capacitor):
	(symbol "C"
		(pin_numbers hide)
		(pin_names
			(offset 0.254)
		)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "C"
			(at 0.635 2.54 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "C"
			(at 0.635 -2.54 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" ""
			(at 0.9652 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Unpolarized capacitor"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "cap capacitor"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "C_*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "C_0_1"
			(polyline
				(pts
					(xy -2.032 -0.762) (xy 2.032 -0.762)
				)
				(stroke
					(width 0.508)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -2.032 0.762) (xy 2.032 0.762)
				)
				(stroke
					(width 0.508)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "C_1_1"
			(pin passive line
				(at 0 3.81 270)
				(length 2.794)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 -3.81 90)
				(length 2.794)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_____

LED (shows orientation):
	(symbol "LED"
		(pin_numbers hide)
		(pin_names
			(offset 1.016) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "D"
			(at 0 2.54 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "LED"
			(at 0 -2.54 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Light emitting diode"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "LED diode"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "LED* LED_SMD:* LED_THT:*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "LED_0_1"
			(polyline
				(pts
					(xy -1.27 -1.27) (xy -1.27 1.27)
				)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -1.27 0) (xy 1.27 0)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)
				)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -3.048 -0.762) (xy -4.572 -2.286) (xy -3.81 -2.286) (xy -4.572 -2.286) (xy -4.572 -1.524)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -1.778 -0.762) (xy -3.302 -2.286) (xy -2.54 -2.286) (xy -3.302 -2.286) (xy -3.302 -1.524)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "LED_1_1"
			(pin passive line
				(at -3.81 0 0)
				(length 2.54)
				(name "K"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 3.81 0 180)
				(length 2.54)
				(name "A"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_____

Crystal (multi-unit component):
	(symbol "Crystal"
		(pin_numbers hide)
		(pin_names
			(offset 1.016) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "Y"
			(at 0 3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Crystal"
			(at 0 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Two pin crystal"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "quartz ceramic resonator oscillator"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "Crystal*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "Crystal_0_1"
			(rectangle
				(start -1.143 2.54)
				(end 1.143 -2.54)
				(stroke
					(width 0.3048)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -2.54 0) (xy -1.905 0)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -1.905 -1.27) (xy -1.905 1.27)
				)
				(stroke
					(width 0.508)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 1.905 -1.27) (xy 1.905 1.27)
				)
				(stroke
					(width 0.508)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 2.54 0) (xy 1.905 0)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "Crystal_1_1"
			(pin passive line
				(at -3.81 0 0)
				(length 1.27)
				(name "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 3.81 0 180)
				(length 1.27)
				(name "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_____


From power.kicad_sym:

	(symbol "GND"
		(power)
		(pin_numbers hide)
		(pin_names
			(offset 0) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "#PWR"
			(at 0 -6.35 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Value" "GND"
			(at 0 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Power symbol creates a global label with name \"GND\" , ground"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "global power"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "GND_0_1"
			(polyline
				(pts
					(xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "GND_1_1"
			(pin power_in line
				(at 0 0 270)
				(length 0)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_____

	(symbol "VCC"
		(power)
		(pin_numbers hide)
		(pin_names
			(offset 0) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "#PWR"
			(at 0 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Value" "VCC"
			(at 0 3.556 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Power symbol creates a global label with name \"VCC\""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "global power"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "VCC_0_1"
			(polyline
				(pts
					(xy -0.762 1.27) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 0) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 2.54) (xy 0.762 1.27)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "VCC_1_1"
			(pin power_in line
				(at 0 0 90)
				(length 0)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
______
	(symbol "+5V"
		(power)
		(pin_numbers hide)
		(pin_names
			(offset 0) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "#PWR"
			(at 0 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Value" "+5V"
			(at 0 3.556 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Power symbol creates a global label with name \"+5V\""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "global power"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "+5V_0_1"
			(polyline
				(pts
					(xy -0.762 1.27) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 0) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 2.54) (xy 0.762 1.27)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "+5V_1_1"
			(pin power_in line
				(at 0 0 90)
				(length 0)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
____

	(symbol "+3.3V"
		(power)
		(pin_numbers hide)
		(pin_names
			(offset 0) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "#PWR"
			(at 0 -3.81 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Value" "+3.3V"
			(at 0 3.556 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Power symbol creates a global label with name \"+3.3V\""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "global power"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "+3.3V_0_1"
			(polyline
				(pts
					(xy -0.762 1.27) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 0) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 2.54) (xy 0.762 1.27)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "+3.3V_1_1"
			(pin power_in line
				(at 0 0 90)
				(length 0)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_______


From Connector_Generic.kicad_sym:

Conn_01x04 (simple 4-pin connector):
(symbol "Conn_01x04"
		(pin_names
			(offset 1.016) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "J"
			(at 0 5.08 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Conn_01x04"
			(at 0 -7.62 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Generic connector, single row, 01x04, script generated (kicad-library-utils/schlib/autogen/connector/)"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "connector"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "Connector*:*_1x??_*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "Conn_01x04_1_1"
			(rectangle
				(start -1.27 -4.953)
				(end 0 -5.207)
				(stroke
					(width 0.1524)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(rectangle
				(start -1.27 -2.413)
				(end 0 -2.667)
				(stroke
					(width 0.1524)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(rectangle
				(start -1.27 0.127)
				(end 0 -0.127)
				(stroke
					(width 0.1524)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(rectangle
				(start -1.27 2.667)
				(end 0 2.413)
				(stroke
					(width 0.1524)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(rectangle
				(start -1.27 3.81)
				(end 1.27 -6.35)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type background)
				)
			)
			(pin passive line
				(at -5.08 2.54 0)
				(length 3.81)
				(name "Pin_1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 0 0)
				(length 3.81)
				(name "Pin_2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -2.54 0)
				(length 3.81)
				(name "Pin_3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -5.08 0)
				(length 3.81)
				(name "Pin_4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
_____

Conn_02x03_Odd_Even (2x3 grid connector):
(symbol "Conn_02x03_Odd_Even"
		(pin_names
			(offset 1.016) hide)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "J"
			(at 1.27 5.08 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Conn_02x03_Odd_Even"
			(at 1.27 -5.08 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "~"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Generic connector, double row, 02x03, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers), script generated (kicad-library-utils/schlib/autogen/connector/)"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "connector"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "Connector*:*_2x??_*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
____

from Regulator_Linear.kicad_sym


	(symbol "NCP1117-3.3_SOT223"
		(extends "AP1117-15")
		(property "Reference" "U"
			(at -3.81 3.175 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "NCP1117-3.3_SOT223"
			(at 0 3.175 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2"
			(at 0 5.08 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "http://www.onsemi.com/pub_link/Collateral/NCP1117-D.PDF"
			(at 2.54 -6.35 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "1A Low drop-out regulator, Fixed Output 3.3V, SOT-223"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_keywords" "REGULATOR LDO 3.3V"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "ki_fp_filters" "SOT?223*TabPin2*"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
	)