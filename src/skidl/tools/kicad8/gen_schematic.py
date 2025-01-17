# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.


import datetime
import os.path
import re
import time
from collections import Counter, OrderedDict

from skidl.scriptinfo import get_script_name
from skidl.geometry import BBox, Point, Tx, Vector
from skidl.schematics.net_terminal import NetTerminal
from skidl.utilities import export_to_all
from .constants import BLK_INT_PAD, BOX_LABEL_FONT_SIZE, GRID, PIN_LABEL_FONT_SIZE
from .bboxes import calc_symbol_bbox, calc_hier_label_bbox
from skidl.schematics.place import PlacementFailure
from skidl.schematics.route import RoutingFailure
from skidl.utilities import rmv_attr


__all__ = []

"""
Functions for generating a KiCad EESCHEMA schematic.
"""


def bbox_to_eeschema(bbox, tx, name=None):
    """Create a bounding box using EESCHEMA graphic lines."""

    # Make sure the box corners are integers.
    bbox = (bbox * tx).round()

    graphic_box = []

    if name:
        # Place name at the lower-left corner of the box.
        name_pt = bbox.ul
        graphic_box.append(
            "Text Notes {} {} 0    {}  ~ 20\n{}".format(
                name_pt.x, name_pt.y, BOX_LABEL_FONT_SIZE, name
            )
        )

    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.lr.x, bbox.lr.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.lr.x, bbox.lr.y, bbox.ur.x, bbox.ur.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ur.x, bbox.ur.y, bbox.ul.x, bbox.ul.y)
    )
    graphic_box.append("Wire Notes Line")
    graphic_box.append(
        "	{} {} {} {}".format(bbox.ul.x, bbox.ul.y, bbox.ll.x, bbox.ll.y)
    )
    graphic_box.append("")  # For blank line at end.

    return "\n".join(graphic_box)


def net_to_eeschema(self, tx):
    """Generate the EESCHEMA code for the net terminal.

    Args:
        tx (Tx): Transformation matrix for the node containing this net terminal.

    Returns:
        str: EESCHEMA code string.
    """
    self.pins[0].stub = True
    self.pins[0].orientation = "R"
    return pin_label_to_eeschema(self.pins[0], tx)
    # return pin_label_to_eeschema(self.pins[0], tx) + bbox_to_eeschema(self.bbox, self.tx * tx)


def part_to_eeschema(part, tx):
    """Create EESCHEMA code for a part.

    Args:
        part (Part): SKiDL part.
        tx (Tx): Transformation matrix.

    Returns:
        string: EESCHEMA code for the part.

    Notes:
        https://en.wikibooks.org/wiki/Kicad/file_formats#Schematic_Files_Format
    """

    tx = part.tx * tx
    origin = tx.origin.round()
    time_hex = hex(int(time.time()))[2:]
    unit_num = getattr(part, "num", 1)

    eeschema = []
    eeschema.append("$Comp")
    lib = os.path.splitext(part.lib.filename)[0]
    eeschema.append("L {}:{} {}".format(lib, part.name, part.ref))
    eeschema.append("U {} 1 {}".format(unit_num, time_hex))
    eeschema.append("P {} {}".format(str(origin.x), str(origin.y)))

    # Add part symbols. For now we are only adding the designator
    n_F0 = 1
    for i in range(len(part.draw)):
        if re.search("^DrawF0", str(part.draw[i])):
            n_F0 = i
            break
    eeschema.append(
        'F 0 "{}" {} {} {} {} {} {} {}'.format(
            part.ref,
            part.draw[n_F0].orientation,
            str(origin.x + part.draw[n_F0].x),
            str(origin.y + part.draw[n_F0].y),
            part.draw[n_F0].size,
            "000",  # TODO: Refine this to match part def.
            part.draw[n_F0].halign,
            part.draw[n_F0].valign,
        )
    )

    # Part value.
    n_F1 = 1
    for i in range(len(part.draw)):
        if re.search("^DrawF1", str(part.draw[i])):
            n_F1 = i
            break
    eeschema.append(
        'F 1 "{}" {} {} {} {} {} {} {}'.format(
            str(part.value),
            part.draw[n_F1].orientation,
            str(origin.x + part.draw[n_F1].x),
            str(origin.y + part.draw[n_F1].y),
            part.draw[n_F1].size,
            "000",  # TODO: Refine this to match part def.
            part.draw[n_F1].halign,
            part.draw[n_F1].valign,
        )
    )

    # Part footprint.
    n_F2 = 2
    for i in range(len(part.draw)):
        if re.search("^DrawF2", str(part.draw[i])):
            n_F2 = i
            break
    eeschema.append(
        'F 2 "{}" {} {} {} {} {} {} {}'.format(
            part.footprint,
            part.draw[n_F2].orientation,
            str(origin.x + part.draw[n_F2].x),
            str(origin.y + part.draw[n_F2].y),
            part.draw[n_F2].size,
            "001",  # TODO: Refine this to match part def.
            part.draw[n_F2].halign,
            part.draw[n_F2].valign,
        )
    )
    eeschema.append("   1   {} {}".format(str(origin.x), str(origin.y)))
    eeschema.append("   {}  {}  {}  {}".format(tx.a, tx.b, tx.c, tx.d))
    eeschema.append("$EndComp")
    eeschema.append("")  # For blank line at end.

    # For debugging: draws a bounding box around a part.
    # eeschema.append(bbox_to_eeschema(part.bbox, tx))
    # eeschema.append(bbox_to_eeschema(part.place_bbox, tx))

    return "\n".join(eeschema)


def wire_to_eeschema(net, wire, tx):
    """Create EESCHEMA code for a multi-segment wire.

    Args:
        net (Net): Net associated with the wire.
        wire (list): List of Segments for a wire.
        tx (Tx): transformation matrix for each point in the wire.

    Returns:
        string: Text to be placed into EESCHEMA file.
    """

    eeschema = []
    for segment in wire:
        eeschema.append("Wire Wire Line")
        w = (segment * tx).round()
        eeschema.append("  {} {} {} {}".format(w.p1.x, w.p1.y, w.p2.x, w.p2.y))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def junction_to_eeschema(net, junctions, tx):
    eeschema = []
    for junction in junctions:
        pt = (junction * tx).round()
        eeschema.append("Connection ~ {} {}".format(pt.x, pt.y))
    eeschema.append("")  # For blank line at end.
    return "\n".join(eeschema)


def power_part_to_eeschema(part, tx=Tx()):
    return ""  # REMOVE: Remove this.
    out = []
    for pin in part.pins:
        try:
            if not (pin.net is None):
                if pin.net.netclass == "Power":
                    # strip out the '_...' section from power nets
                    t = pin.net.name
                    u = t.split("_")
                    symbol_name = u[0]
                    # find the stub in the part
                    time_hex = hex(int(time.time()))[2:]
                    pin_pt = (part.origin + offset + Point(pin.x, pin.y)).round()
                    x, y = pin_pt.x, pin_pt.y
                    out.append("$Comp\n")
                    out.append("L power:{} #PWR?\n".format(symbol_name))
                    out.append("U 1 1 {}\n".format(time_hex))
                    out.append("P {} {}\n".format(str(x), str(y)))
                    # Add part symbols. For now we are only adding the designator
                    n_F0 = 1
                    for i in range(len(part.draw)):
                        if re.search("^DrawF0", str(part.draw[i])):
                            n_F0 = i
                            break
                    part_orientation = part.draw[n_F0].orientation
                    part_horizontal_align = part.draw[n_F0].halign
                    part_vertical_align = part.draw[n_F0].valign

                    # check if the pin orientation will clash with the power part
                    if "+" in symbol_name:
                        # voltage sources face up, so check if the pin is facing down (opposite logic y-axis)
                        if pin.orientation == "U":
                            orientation = [-1, 0, 0, 1]
                    elif "gnd" in symbol_name.lower():
                        # gnd points down so check if the pin is facing up (opposite logic y-axis)
                        if pin.orientation == "D":
                            orientation = [-1, 0, 0, 1]
                    out.append(
                        'F 0 "{}" {} {} {} {} {} {} {}\n'.format(
                            "#PWR?",
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "001",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append(
                        'F 1 "{}" {} {} {} {} {} {} {}\n'.format(
                            symbol_name,
                            part_orientation,
                            str(x + 25),
                            str(y + 25),
                            str(40),
                            "000",
                            part_horizontal_align,
                            part_vertical_align,
                        )
                    )
                    out.append("   1   {} {}\n".format(str(x), str(y)))
                    out.append(
                        "   {}   {}  {}  {}\n".format(
                            orientation[0],
                            orientation[1],
                            orientation[2],
                            orientation[3],
                        )
                    )
                    out.append("$EndComp\n")
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
    return "\n" + "".join(out)


# Sizes of EESCHEMA schematic pages from smallest to largest. Dimensions in mils.
A_sizes_list = [
    ("A4", BBox(Point(0, 0), Point(11693, 8268))),
    ("A3", BBox(Point(0, 0), Point(16535, 11693))),
    ("A2", BBox(Point(0, 0), Point(23386, 16535))),
    ("A1", BBox(Point(0, 0), Point(33110, 23386))),
    ("A0", BBox(Point(0, 0), Point(46811, 33110))),
]

# Create bounding box for each A size sheet.
A_sizes = OrderedDict(A_sizes_list)


def get_A_size(bbox):
    """Return the A-size page needed to fit the given bounding box."""

    width = bbox.w
    height = bbox.h * 1.25  # HACK: why 1.25?
    for A_size, page in A_sizes.items():
        if width < page.w and height < page.h:
            return A_size
    return "A0"  # Nothing fits, so use the largest available.


def calc_sheet_tx(bbox):
    """Compute the page size and positioning for this sheet."""
    A_size = get_A_size(bbox)
    page_bbox = bbox * Tx(d=-1)
    move_to_ctr = A_sizes[A_size].ctr.snap(GRID) - page_bbox.ctr.snap(GRID)
    move_tx = Tx(d=-1).move(move_to_ctr)
    return move_tx

def angle_to_dir(angle):
    """Convert angle in degrees to cardinal direction.
    
    Args:
        angle: Angle in degrees (0, 90, 180, 270)
        
    Returns:
        str: Cardinal direction ('R', 'U', 'L', 'D')
    """
    angle = int(angle) % 360
    return {
        0: 'R',    # Right
        90: 'U',   # Up 
        180: 'L',  # Left
        270: 'D'   # Down
    }[angle]

def calc_pin_dir(pin):
    """Calculate pin direction accounting for part transformation matrix."""

    # If pin has numeric angle orientation, convert it
    if hasattr(pin, 'angle'):
        return angle_to_dir(pin.angle)
        
    # If pin has string orientation, use it directly
    if hasattr(pin, 'orientation'):
        if pin.orientation in ('U', 'D', 'L', 'R'):
            return pin.orientation
        try:
            # Try converting numeric string to angle
            angle = float(pin.orientation)
            return angle_to_dir(angle)
        except (ValueError, TypeError):
            pass

    # Copy the part trans. matrix, but remove the translation vector, leaving only scaling/rotation stuff.
    tx = pin.part.tx
    tx = Tx(a=tx.a, b=tx.b, c=tx.c, d=tx.d)

    # Use the pin orientation to compute the pin direction vector.
    pin_vector = {
        "U": Point(0, 1),
        "D": Point(0, -1),
        "L": Point(-1, 0),
        "R": Point(1, 0),
    }[pin.orientation]

    # Rotate the direction vector using the part rotation matrix.
    pin_vector = pin_vector * tx

    # Create an integer tuple from the rotated direction vector.
    pin_vector = (int(round(pin_vector.x)), int(round(pin_vector.y)))

    # Return the pin orientation based on its rotated direction vector.
    return {
        (0, 1): "U",
        (0, -1): "D",
        (-1, 0): "L",
        (1, 0): "R",
    }[pin_vector]

@export_to_all
def pin_label_to_eeschema(pin, tx):
    """Create EESCHEMA text of net label attached to a pin."""

    if pin.stub is False or not pin.is_connected():
        # No label if pin is not connected or is connected to an explicit wire.
        return ""

    label_type = "HLabel"
    for pn in pin.net.pins:
        if pin.part.hierarchy.startswith(pn.part.hierarchy):
            continue
        if pn.part.hierarchy.startswith(pin.part.hierarchy):
            continue
        label_type = "GLabel"
        break

    part_tx = pin.part.tx * tx
    pt = pin.pt * part_tx

    pin_dir = calc_pin_dir(pin)
    orientation = {
        "R": 0,
        "D": 1,
        "L": 2,
        "U": 3,
    }[pin_dir]

    return "Text {} {} {} {}    {}   UnSpc ~ 0\n{}\n".format(
        label_type,
        int(round(pt.x)),
        int(round(pt.y)),
        orientation,
        PIN_LABEL_FONT_SIZE,
        pin.net.name,
    )


def create_eeschema_file(
    filename,
    contents,
    cur_sheet_num=1,
    total_sheet_num=1,
    title="Default",
    rev_major=0,
    rev_minor=1,
    year=datetime.date.today().year,
    month=datetime.date.today().month,
    day=datetime.date.today().day,
    A_size="A2",
):
    """Write EESCHEMA header, contents, and footer to a file."""

    with open(filename, "w") as f:
        f.write(
            "\n".join(
                (
                    "EESchema Schematic File Version 4",
                    "EELAYER 30 0",
                    "EELAYER END",
                    "$Descr {} {} {}".format(
                        A_size, A_sizes[A_size].max.x, A_sizes[A_size].max.y
                    ),
                    "encoding utf-8",
                    "Sheet {} {}".format(cur_sheet_num, total_sheet_num),
                    'Title "{}"'.format(title),
                    'Date "{}-{}-{}"'.format(year, month, day),
                    'Rev "v{}.{}"'.format(rev_major, rev_minor),
                    'Comp ""',
                    'Comment1 ""',
                    'Comment2 ""',
                    'Comment3 ""',
                    'Comment4 ""',
                    "$EndDescr",
                    "",
                    contents,
                    "$EndSCHEMATC",
                )
            )
        )


@export_to_all
def node_to_eeschema(node, sheet_tx=Tx()):
    """Convert node circuitry to an EESCHEMA sheet.

    Args:
        sheet_tx (Tx, optional): Scaling/translation matrix for sheet. Defaults to Tx().

    Returns:
        str: EESCHEMA text for the node circuitry.
    """

    from skidl import HIER_SEP

    # List to hold all the EESCHEMA code for this node.
    eeschema_code = []

    if node.flattened:
        # Create the transformation matrix for the placement of the parts in the node.
        tx = node.tx * sheet_tx
    else:
        # Unflattened nodes are placed in their own sheet, so compute
        # their bounding box as if they *were* flattened and use that to
        # find the transformation matrix for an appropriately-sized sheet.
        flattened_bbox = node.internal_bbox()
        tx = calc_sheet_tx(flattened_bbox)

    # Generate EESCHEMA code for each child of this node.
    for child in node.children.values():
        eeschema_code.append(node_to_eeschema(child, tx))

    # Generate EESCHEMA code for each part in the node.
    for part in node.parts:
        if isinstance(part, NetTerminal):
            eeschema_code.append(net_to_eeschema(part, tx=tx))
        else:
            eeschema_code.append(part_to_eeschema(part, tx=tx))

    # Generate EESCHEMA wiring code between the parts in the node.
    for net, wire in node.wires.items():
        wire_code = wire_to_eeschema(net, wire, tx=tx)
        eeschema_code.append(wire_code)
    for net, junctions in node.junctions.items():
        junction_code = junction_to_eeschema(net, junctions, tx=tx)
        eeschema_code.append(junction_code)

    # Generate power connections for the each part in the node.
    for part in node.parts:
        stub_code = power_part_to_eeschema(part, tx=tx)
        if len(stub_code) != 0:
            eeschema_code.append(stub_code)

    # Generate pin labels for stubbed nets on each part in the node.
    for part in node.parts:
        for pin in part:
            pin_label_code = pin_label_to_eeschema(pin, tx=tx)
            eeschema_code.append(pin_label_code)

    # Join EESCHEMA code into one big string.
    eeschema_code = "\n".join(eeschema_code)

    # If this node was flattened, then return the EESCHEMA code and surrounding box
    # for inclusion in the parent node.
    if node.flattened:

        # Generate the graphic box that surrounds the flattened hierarchical block of this node.
        block_name = node.name.split(HIER_SEP)[-1]
        pad = Vector(BLK_INT_PAD, BLK_INT_PAD)
        bbox_code = bbox_to_eeschema(node.bbox.resize(pad), tx, block_name)

        return "\n".join((eeschema_code, bbox_code))

    # Create a hierarchical sheet file for storing this unflattened node.
    A_size = get_A_size(flattened_bbox)
    filepath = os.path.join(node.filepath, node.sheet_filename)
    create_eeschema_file(filepath, eeschema_code, title=node.title, A_size=A_size)

    # Create the hierarchical sheet for insertion into the calling node sheet.
    bbox = (node.bbox * node.tx * sheet_tx).round()
    time_hex = hex(int(time.time()))[2:]
    return "\n".join(
        (
            "$Sheet",
            "S {} {} {} {}".format(bbox.ll.x, bbox.ll.y, bbox.w, bbox.h),
            "U {}".format(time_hex),
            'F0 "{}" {}'.format(node.name, node.name_sz),
            'F1 "{}" {}'.format(node.sheet_filename, node.filename_sz),
            "$EndSheet",
            "",
        )
    )


"""
Generate a KiCad EESCHEMA schematic from a Circuit object.
"""

# TODO: Handle symio attribute.

def preprocess_circuit(circuit, **options):
    """Add stuff to parts & nets for doing placement and routing of schematics."""
    from collections import Counter
    from skidl.geometry import BBox, Point, Tx, Vector
    from .bboxes import calc_symbol_bbox, calc_hier_label_bbox

    def units(part):
        if len(part.unit) == 0:
            return [part]
        else:
            return part.unit.values()

    def initialize(part):
        """Initialize part or its part units."""

        # Initialize the units of the part, or the part itself if it has no units.
        pin_limit = options.get("orientation_pin_limit", 44)
        for part_unit in units(part):
            # Initialize transform matrix.
            part_unit.tx = Tx.from_symtx(getattr(part_unit, "symtx", ""))

            # Lock part orientation if symtx was specified. Also lock parts with a lot of pins
            # since they're typically drawn the way they're supposed to be oriented.
            # And also lock single-pin parts because these are usually power/ground and
            # they shouldn't be flipped around.
            num_pins = len(part_unit.pins)
            part_unit.orientation_locked = getattr(part_unit, "symtx", False) or not (
                1 < num_pins <= pin_limit
            )

            # Assign pins from the parent part to the part unit.
            part_unit.grab_pins()

            # Initialize pin attributes used for generating schematics.
            for pin in part_unit:
                pin.pt = Point(pin.x, pin.y)
                pin.routed = False

    def rotate_power_pins(part):
        """Rotate a part based on the direction of its power pins.

        This function is to make sure that voltage sources face up and gnd pins
        face down.
        """

        # Don't rotate parts that are already explicitly rotated/flipped.
        if not getattr(part, "symtx", ""):
            return

        def is_pwr(net):
            return net_name.startswith("+")

        def is_gnd(net):
            return "gnd" in net_name.lower()

        dont_rotate_pin_cnt = options.get("dont_rotate_pin_count", 10000)

        for part_unit in units(part):
            # Don't rotate parts with too many pins.
            if len(part_unit) > dont_rotate_pin_cnt:
                return

            # Tally what rotation would make each pwr/gnd pin point up or down.
            rotation_tally = Counter()
            for pin in part_unit:
                net_name = getattr(pin.net, "name", "").lower()
                if is_gnd(net_name):
                    if pin.orientation == "U":
                        rotation_tally[0] += 1
                    if pin.orientation == "D":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[90] += 1
                    if pin.orientation == "R":
                        rotation_tally[270] += 1
                elif is_pwr(net_name):
                    if pin.orientation == "D":
                        rotation_tally[0] += 1
                    if pin.orientation == "U":
                        rotation_tally[180] += 1
                    if pin.orientation == "L":
                        rotation_tally[270] += 1
                    if pin.orientation == "R":
                        rotation_tally[90] += 1

            # Rotate the part unit in the direction with the most tallies.
            try:
                rotation = rotation_tally.most_common()[0][0]
            except IndexError:
                pass
            else:
                # Rotate part unit 90-degrees clockwise until the desired rotation is reached.
                tx_cw_90 = Tx(a=0, b=-1, c=1, d=0)  # 90-degree trans. matrix.
                for _ in range(int(round(rotation / 90))):
                    part_unit.tx = part_unit.tx * tx_cw_90

    def calc_part_bbox(part):
        """Calculate the labeled bounding boxes and store it in the part."""

        # Find part/unit bounding boxes excluding any net labels on pins.
        calc_symbol_bbox(part)

        for part_unit in units(part):
            # Expand the bounding box if it's too small in either dimension.
            resize_wh = Vector(0, 0)
            if part_unit.bbox.w < 100:
                resize_wh.x = (100 - part_unit.bbox.w) / 2
            if part_unit.bbox.h < 100:
                resize_wh.y = (100 - part_unit.bbox.h) / 2
            bare_bbox = part_unit.bbox.resize(resize_wh)

            # Find expanded bounding box that includes any hier labels attached to pins.
            part_unit.lbl_bbox = BBox()
            part_unit.lbl_bbox.add(bare_bbox)
            for pin in part_unit:
                if pin.stub:
                    # Find bounding box for net stub label attached to pin.
                    hlbl_bbox = calc_hier_label_bbox(pin.net.name, pin.orientation)
                    # Move the label bbox to the pin location.
                    hlbl_bbox *= Tx().move(pin.pt)
                    # Update the bbox for the labelled part with this pin label.
                    part_unit.lbl_bbox.add(hlbl_bbox)

            # Set the active bounding box to the labeled version.
            part_unit.bbox = part_unit.lbl_bbox

    # Pre-process parts
    for part in circuit.parts:
        # Initialize part attributes used for generating schematics.
        initialize(part)

        # Rotate parts. Power pins should face up. GND pins should face down.
        rotate_power_pins(part)

        # Compute bounding boxes around parts
        calc_part_bbox(part)

def finalize_parts_and_nets(circuit, **options):
    """Restore parts and nets after place & route is done."""

    # Remove any NetTerminals that were added.
    net_terminals = (p for p in circuit.parts if isinstance(p, NetTerminal))
    circuit.rmv_parts(*net_terminals)

    # Return pins from the part units to their parent part.
    for part in circuit.parts:
        part.grab_pins()

    # Remove some stuff added to parts during schematic generation process.
    rmv_attr(circuit.parts, ("force", "bbox", "lbl_bbox", "tx"))

# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import datetime
import os.path
import re
import time
import uuid
from collections import OrderedDict

from skidl.utilities import export_to_all
from .constants import BLK_INT_PAD, BOX_LABEL_FONT_SIZE, GRID, PIN_LABEL_FONT_SIZE

def generate_uuid():
    """Generate a UUID v4 string."""
    return str(uuid.uuid4())

def create_s_expr_file(
    filename,
    contents,
    version="20231120", # KiCad 8.0 schema version
    generator="skidl",
    title="SKiDL-Generated Schematic",
    company="",
    rev="",
    date=None,
    comment1="",
    comment2="",
    comment3="",
    comment4="",
    paper_size="A4",
    **kwargs
):
    """Create a KiCad 8 schematic file using s-expressions.
    
    Args:
        filename: Output filename
        contents: Schematic contents as s-expressions
        version: Schema version 
        generator: Generator name
        title: Schematic title
        company: Company name
        rev: Revision
        date: Date string (YYYY-MM-DD)
        comment1-4: Comments
        paper_size: Paper size (A4, A3, etc)
    """
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")

    # Main schematic structure
    schematic = f"""(kicad_sch
  (version {version})
  (generator {generator})
  (uuid {generate_uuid()})
  (paper {paper_size})
  (title_block
    (title "{title}")
    (date "{date}")
    (rev "{rev}")
    (company "{company}")
    (comment1 "{comment1}")
    (comment2 "{comment2}")  
    (comment3 "{comment3}")
    (comment4 "{comment4}")
  )
  
{contents}
)
"""
    with open(filename, "w") as f:
        f.write(schematic)

def symbol_to_s_expr(symbol, tx):
    """Convert a schematic symbol to s-expressions.
    
    Args:
        symbol: Symbol object
        tx: Transform matrix
    
    Returns:
        String of s-expressions
    """
    uuid_str = generate_uuid()
    pos = (symbol.pt * tx).round()
    
    s_expr = f"""(symbol
    (lib_id "{symbol.lib}:{symbol.name}")
    (at {pos.x} {pos.y} {tx.angle})
    (unit {getattr(symbol, 'unit', 1)})
    (in_bom yes)
    (on_board yes)
    (uuid {uuid_str})
    (property "Reference" "{symbol.ref}"
      (at {pos.x} {pos.y - 100} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{symbol.value}"
      (at {pos.x} {pos.y + 100} 0) 
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "{symbol.footprint}"
      (at {pos.x} {pos.y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
"""

    # Add pins
    for pin in symbol.pins:
        pin_pos = (pin.pt * tx).round()
        s_expr += f"""    (pin "{pin.num}" (uuid {generate_uuid()})
      (at {pin_pos.x} {pin_pos.y} {pin.angle})
    )
"""
        
    s_expr += ")\n"
    return s_expr

def wire_to_s_expr(wire, tx):
    """Convert a wire segment to s-expressions.
    
    Args:
        wire: Wire segment object
        tx: Transform matrix
    
    Returns: 
        String of s-expressions
    """
    start = (wire.p1 * tx).round()
    end = (wire.p2 * tx).round()
    
    return f"""(wire
    (pts
      (xy {start.x} {start.y})
      (xy {end.x} {end.y})
    )
    (stroke (width 0) (type default))
    (uuid {generate_uuid()})
  )
"""

def junction_to_s_expr(junction, tx):
    """Convert a junction to s-expressions.
    
    Args:
        junction: Junction point
        tx: Transform matrix
    
    Returns:
        String of s-expressions
    """
    pos = (junction * tx).round()
    
    return f"""(junction
    (at {pos.x} {pos.y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid {generate_uuid()})
  )
"""

def no_connect_to_s_expr(no_connect, tx):
    """Convert a no-connect marker to s-expressions.
    
    Args:
        no_connect: No connect point
        tx: Transform matrix
        
    Returns:
        String of s-expressions
    """
    pos = (no_connect * tx).round()
    
    return f"""(no_connect
    (at {pos.x} {pos.y})
    (uuid {generate_uuid()})
  )
"""

def hierarchical_sheet_to_s_expr(sheet, tx):
    """Convert a hierarchical sheet to s-expressions.
    
    Args:
        sheet: Sheet object
        tx: Transform matrix
        
    Returns:
        String of s-expressions
    """
    pos = (sheet.pt * tx).round()
    size = sheet.size.round()
    
    s_expr = f"""(sheet
    (at {pos.x} {pos.y})
    (size {size.x} {size.y})
    (stroke (width 0) (type solid))
    (fill (type none))
    (uuid {generate_uuid()})
    (property "Sheet name" "{sheet.name}"
      (at {pos.x} {pos.y - 50} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Sheet file" "{sheet.filename}"
      (at {pos.x} {pos.y + 50} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
"""

    # Add hierarchical pins
    for pin in sheet.pins:
        pin_pos = (pin.pt * tx).round()
        s_expr += f"""    (pin "{pin.name}" {pin.direction}
      (at {pin_pos.x} {pin_pos.y} {pin.angle})
      (effects (font (size 1.27 1.27)))
      (uuid {generate_uuid()})
    )
"""

    s_expr += ")\n"
    return s_expr

@export_to_all
def node_to_s_expr(node, sheet_tx=None):
    """Convert node circuitry to s-expressions for KiCad 8 schematic.
    
    Args:
        node: Node object containing circuit elements
        sheet_tx: Transform matrix for sheet placement
        
    Returns:
        String of s-expressions for schematic
    """
    if sheet_tx is None:
        sheet_tx = Tx()
        
    # Build up schematic contents
    contents = []
    
    # Add library symbols section if any are used
    if node.lib_symbols:
        contents.append("(lib_symbols")
        for symbol in node.lib_symbols:
            contents.append(symbol_to_s_expr(symbol, sheet_tx))
        contents.append(")")
            
    # Add junctions
    for net, junctions in node.junctions.items():
        for junction in junctions:
            contents.append(junction_to_s_expr(junction, sheet_tx))
            
    # Add no connects
    for no_connect in node.no_connects:
        contents.append(no_connect_to_s_expr(no_connect, sheet_tx))
        
    # Add wires
    for net, wires in node.wires.items():
        for wire in wires:
            contents.append(wire_to_s_expr(wire, sheet_tx))
            
    # Add symbols
    for symbol in node.symbols:
        contents.append(symbol_to_s_expr(symbol, sheet_tx))
        
    # Add hierarchical sheets 
    for sheet in node.sheets:
        contents.append(hierarchical_sheet_to_s_expr(sheet, sheet_tx))

    return "\n".join(contents)


from skidl.utilities import export_to_all
from skidl.geometry import BBox, Point, tx_rot_0, tx_rot_90, tx_rot_180, tx_rot_270

@export_to_all
def calc_hier_label_bbox(label, dir):
    """Calculate the bounding box for a hierarchical label.
    
    Args:
        label (str): String for the label.
        dir (str): Orientation ("U", "D", "L", "R").
        
    Returns:
        BBox: Bounding box for the label and hierarchical terminal.
    """
    # Rotation matrices for each direction.
    lbl_tx = {
        "U": tx_rot_90,    # Pin on bottom pointing upwards.
        "D": tx_rot_270,   # Pin on top pointing down.
        "L": tx_rot_180,   # Pin on right pointing left.
        "R": tx_rot_0,     # Pin on left pointing right.
    }

    # Calculate length and height of label + hierarchical marker.
    # For KiCad 8, we'll use the same proportions but scale them appropriately
    # These values may need adjustment based on KiCad 8's default scaling
    PIN_LABEL_FONT_SIZE = 50  # Default KiCad 8 font size
    HIER_TERM_SIZE = 100      # Size of hierarchical terminal marker

    lbl_len = len(label) * PIN_LABEL_FONT_SIZE + HIER_TERM_SIZE
    lbl_hgt = max(PIN_LABEL_FONT_SIZE, HIER_TERM_SIZE)

    # Create bbox for label on left followed by marker on right.
    # Note: In KiCad 8, the coordinate system remains consistent with KiCad 5
    bbox = BBox(Point(0, lbl_hgt / 2), Point(-lbl_len, -lbl_hgt / 2))

    # Rotate the bbox in the given direction.
    bbox *= lbl_tx[dir]

    return bbox


# -*- coding: utf-8 -*-

from skidl.utilities import export_to_all
import sexpdata

def convert_sexp(sexp):
    """Convert s-expression data to Python objects."""
    if isinstance(sexp, list):
        return [convert_sexp(item) for item in sexp]
    elif isinstance(sexp, sexpdata.Symbol):
        return str(sexp)
    else:
        return sexp

def process_pin(pin_data):
    """Process pin data from symbol file."""
    pin = {
        'type': 'pin',
        'name': '~',
        'number': '',
        'orientation': 'R',
        'length': 0,
        'x': 0,
        'y': 0
    }
    
    # Extract basic pin data
    pin['style'] = pin_data[1]  # passive, line etc
    
    # Find coordinates and orientation
    at_idx = next(i for i, x in enumerate(pin_data) if isinstance(x, list) and x[0] == 'at')
    at_data = pin_data[at_idx]
    pin['x'] = float(at_data[1])
    pin['y'] = float(at_data[2])
    if len(at_data) > 3:
        angle = float(at_data[3])
        if angle == 0:
            pin['orientation'] = 'R'
        elif angle == 90:
            pin['orientation'] = 'U'
        elif angle == 180:
            pin['orientation'] = 'L' 
        elif angle == 270:
            pin['orientation'] = 'D'
            
    # Get pin length
    length_idx = next(i for i, x in enumerate(pin_data) if isinstance(x, list) and x[0] == 'length')
    pin['length'] = float(pin_data[length_idx][1])
    
    # Get pin number
    num_idx = next(i for i, x in enumerate(pin_data) if isinstance(x, list) and x[0] == 'number')
    pin['number'] = str(pin_data[num_idx][1])
    
    # Get pin name
    name_idx = next(i for i, x in enumerate(pin_data) if isinstance(x, list) and x[0] == 'name')
    pin['name'] = str(pin_data[name_idx][1])
    
    return pin

def get_stroke_width(shape_data):
    """Get stroke width from shape data."""
    stroke_idx = next((i for i, x in enumerate(shape_data) if isinstance(x, list) and x[0] == 'stroke'), None)
    if stroke_idx is not None:
        stroke = shape_data[stroke_idx]
        width_idx = next((i for i, x in enumerate(stroke) if isinstance(x, list) and x[0] == 'width'), None)
        if width_idx is not None:
            return float(stroke[width_idx][1])
    return 0  # Default width if not specified

def process_shape(shape_data):
    """Process shape data (rectangle, polyline, arc etc) from symbol file."""
    shape_type = shape_data[0]
    shape = {
        'type': shape_type,
        'points': [],
        'width': get_stroke_width(shape_data)
    }
    
    if shape_type == 'rectangle':
        start = shape_data[next(i for i, x in enumerate(shape_data) if x[0] == 'start')]
        end = shape_data[next(i for i, x in enumerate(shape_data) if x[0] == 'end')]
        shape['points'] = [
            (float(start[1]), float(start[2])),
            (float(end[1]), float(start[2])),
            (float(end[1]), float(end[2])),
            (float(start[1]), float(end[2])),
            (float(start[1]), float(start[2]))
        ]
    
    elif shape_type == 'arc':
        # Extract arc parameters
        start = shape_data[next(i for i, x in enumerate(shape_data) if x[0] == 'start')]
        mid = shape_data[next(i for i, x in enumerate(shape_data) if x[0] == 'mid')]
        end = shape_data[next(i for i, x in enumerate(shape_data) if x[0] == 'end')]
        
        # Store arc points
        shape['points'] = [
            (float(start[1]), float(start[2])),
            (float(mid[1]), float(mid[2])),
            (float(end[1]), float(end[2]))
        ]
            
    return shape

def process_symbol_unit(unit_data):
    """Process a single symbol unit's data."""
    unit = {
        'drawing': [],
        'pins': [],
        'fields': {}
    }
    
    # Process all drawing elements in this unit
    for element in unit_data[2:]:
        if isinstance(element, list):
            if element[0] == 'pin':
                unit['pins'].append(process_pin(element))
            elif element[0] in ['rectangle', 'polyline', 'arc', 'circle']:
                unit['drawing'].append(process_shape(element))
                
    return unit

@export_to_all
def load_symbol_drawing_data(filename):
    """Load symbol drawing data from a KiCad 8 symbol library file.
    
    Args:
        filename: Path to .kicad_sym file
        
    Returns:
        dict: Dictionary mapping symbol names to their drawing data
    """
    with open(filename, 'r') as f:
        data = convert_sexp(sexpdata.load(f))
        
    symbols = {}
    
    # Process each symbol in the library
    for item in data[1:]:
        if isinstance(item, list) and item[0] == 'symbol':
            symbol_name = item[1]
            if '.' not in symbol_name:  # Skip unit symbols like "R_Small_0_1"
                # Get all units for this symbol
                units = {}
                
                # Find all the symbol unit definitions for this symbol
                for subitem in item[2:]:
                    if isinstance(subitem, list) and subitem[0] == 'symbol':
                        # Extract unit number from the name (e.g., "L_Small_0_1" -> 0)
                        unit_parts = subitem[1].split('_')
                        if len(unit_parts) >= 2:
                            try:
                                unit_num = int(unit_parts[-2])
                                if unit_num not in units:
                                    units[unit_num] = {
                                        'drawing': [],
                                        'pins': [],
                                        'fields': {}
                                    }
                                unit_data = process_symbol_unit(subitem)
                                units[unit_num]['drawing'].extend(unit_data['drawing'])
                                units[unit_num]['pins'].extend(unit_data['pins'])
                            except ValueError:
                                continue
                
                # Convert units dict to list ordered by unit number
                drawing_data = [units[i] for i in sorted(units.keys())]
                symbols[symbol_name] = drawing_data
                
    return symbols

@export_to_all 
def gen_schematic(
    circuit,
    filepath=".",
    top_name=None,
    title="SKiDL-Generated Schematic",
    flatness=0.0,
    retries=2,
    **options
):
    """Generate a KiCad 8 schematic from a circuit.
    
    Args:
        circuit: Circuit object
        filepath: Output directory
        top_name: Top sheet name
        title: Schematic title
        flatness: Hierarchy flattening factor (0-1)
        retries: Number of routing retries
        options: Additional options
    """
    from skidl.logger import active_logger
    from skidl.tools import tool_modules
    from skidl.schematics.node import Node
    from skidl.schematics.place import PlacementFailure
    from skidl.schematics.route import RoutingFailure
    
    if top_name is None:
        top_name = get_script_name()
        
    # Create node structure
    node = Node(circuit, tool_modules["kicad8"], filepath, top_name, title, flatness)

    # Try placement and routing
    for _ in range(retries):
        try:
            # Place parts
            node.place(**options)
            
            # Route connections
            node.route(**options)
            
            # Generate s-expressions
            contents = node_to_s_expr(node)
            
            # Write schematic file
            filename = os.path.join(filepath, top_name + ".kicad_sch")
            create_s_expr_file(filename, contents, title=title)
            
            return
            
        except (PlacementFailure, RoutingFailure):
            continue
            
    raise RoutingFailure("Failed to route schematic after {} attempts".format(retries))

# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from skidl.utilities import export_to_all

@export_to_all
def load_symbol_drawing_data(filename):
    """Load symbol drawing data from a KiCad 8 symbol library file.
    
    Args:
        filename: Path to .kicad_sym file
        
    Returns:
        dict: Dictionary mapping symbol names to their drawing data
    """
    import sexpdata
    
    with open(filename, 'r') as f:
        data = sexpdata.load(f)
        
    symbols = {}
    
    # Skip the first element which is 'kicad_symbol_lib
    for sym in data[1:]:
        if isinstance(sym, list) and len(sym) > 1 and sym[0] == sexpdata.Symbol('symbol'):
            # Get symbol name
            name = str(sym[1])
            if '.' in name:  # Handle unit symbols like "R.1"
                name = name.split('.')[0]
                
            # Create drawing data structure
            drawing = {
                'draw': [],
                'fields': {},
                'pins': []
            }
            
            # Parse all drawing elements in symbol
            for elem in sym[2:]:
                if isinstance(elem, list):
                    if elem[0] == sexpdata.Symbol('polyline'):
                        points = []
                        for pt in elem[1][1:]:  # Skip 'pts' symbol
                            if isinstance(pt, list) and pt[0] == sexpdata.Symbol('xy'):
                                x = float(str(pt[1]))
                                y = float(str(pt[2])) 
                                points.append((x,y))
                        if points:
                            drawing['draw'].append({
                                'type': 'polyline',
                                'points': points,
                                'width': 0.254
                            })
                    
                    elif elem[0] == sexpdata.Symbol('pin'):
                        pin = {
                            'name': str(elem[1]),
                            'num': str(elem[2]) if len(elem) > 2 else '',
                            'pos': (0,0),
                            'length': 2.54,
                            'orientation': 'R'  # Default right
                        }
                        
                        # Find position and orientation
                        for attr in elem:
                            if isinstance(attr, list):
                                if attr[0] == sexpdata.Symbol('at'):
                                    pin['pos'] = (float(str(attr[1])), float(str(attr[2])))
                                    if len(attr) > 3:
                                        angle = float(str(attr[3]))
                                        if angle == 0:
                                            pin['orientation'] = 'R'
                                        elif angle == 90:
                                            pin['orientation'] = 'U' 
                                        elif angle == 180:
                                            pin['orientation'] = 'L'
                                        elif angle == 270:
                                            pin['orientation'] = 'D'
                                            
                        drawing['pins'].append(pin)
            
            if name in symbols:
                # Merge drawing data for multi-unit symbols
                symbols[name]['draw'].extend(drawing['draw'])
                symbols[name]['pins'].extend(drawing['pins'])
            else:
                symbols[name] = drawing
                
    return symbols