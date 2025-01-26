# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Calculate bounding boxes for part symbols and hierarchical sheets.
"""

from collections import namedtuple

from skidl.logger import active_logger
from skidl.geometry import (
    Tx,
    BBox,
    Point,
    Vector,
    tx_rot_0,
    tx_rot_90,
    tx_rot_180,
    tx_rot_270,
    mils_per_mm,
    mms_per_mil,
)
from skidl.utilities import export_to_all
from .constants import HIER_TERM_SIZE, PIN_LABEL_FONT_SIZE
from skidl.geometry import BBox, Point, Tx, Vector


@export_to_all
def calc_symbol_bbox(part):
    """Calculate the bounding box for a part's symbol excluding pin labels.
    
    Args:
        part: Part whose bounding box is calculated.
    """
    part.bbox = BBox()

    # Return empty bbox if part has no drawing elements 
    if not hasattr(part, 'draw') or not part.draw:
        return

    # Get drawing data for this part's unit
    try:
        unit_num = getattr(part, 'unit_num', 0)  # Default to first unit
        unit_drawing = part.draw[unit_num]  # Get drawing data for this unit
    except (IndexError, KeyError):
        return  # Return empty bbox if no drawing data found

    # Add all drawing elements to bbox
    if 'draw' in unit_drawing:
        for shape in unit_drawing['draw']:
            if 'points' in shape:
                for x, y in shape['points']:
                    part.bbox.add(Point(x, y))

    # Add all pins to bbox
    if 'pins' in unit_drawing:
        for pin in unit_drawing['pins']:
            if 'pos' in pin:
                x, y = pin['pos']
                part.bbox.add(Point(x, y))

@export_to_all
def calc_hier_label_bbox(label, dir):
    """Calculate the bounding box for a hierarchical label.

    Args:
        label (str): String for the label.
        dir (str): Orientation ("U", "D", "L", "R").

    Returns:
        BBox: Bounding box for the label and hierarchical terminal.
    """

    raise NotImplementedError

    # Rotation matrices for each direction.
    lbl_tx = {
        "U": tx_rot_90,  # Pin on bottom pointing upwards.
        "D": tx_rot_270,  # Pin on top pointing down.
        "L": tx_rot_180,  # Pin on right pointing left.
        "R": tx_rot_0,  # Pin on left pointing right.
    }

    # Calculate length and height of label + hierarchical marker.
    lbl_len = len(label) * PIN_LABEL_FONT_SIZE + HIER_TERM_SIZE
    lbl_hgt = max(PIN_LABEL_FONT_SIZE, HIER_TERM_SIZE)

    # Create bbox for label on left followed by marker on right.
    bbox = BBox(Point(0, lbl_hgt / 2), Point(-lbl_len, -lbl_hgt / 2))

    # Rotate the bbox in the given direction.
    bbox *= lbl_tx[dir]

    return bbox
