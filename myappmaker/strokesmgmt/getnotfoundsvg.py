"""Tools to generate SVG text defining a "not found" icon."""

### standard library import
from math import sqrt


### third-party imports
from PySide6.QtCore import QPointF, QRect, QMargins


### local imports
from ..svgutils import get_ellipse_svg_text, get_line_svg_text



def get_not_found_icon_svg_text(size):
    """Return surface with icon representing an image not found.

    Icon is formed by an ellipse with a diagonal slash.

    Parameters
    ==========
    size (2-tuple of integers)
        Integers represent width and height of surface, respecively.
    """
    ### render an ellipse outline surface

    ## define ellipse data

    # outline thickness

    smaller_dimension = min(size)

    outline_thickness = (
        smaller_dimension // 10 if smaller_dimension > 10 else 1
    )

    # cx, cy, rx, ry

    cx, cy = (dimension/2 for dimension in size)

    width, height = size

    rx = (width - (outline_thickness*2)) / 2
    ry = (height - (outline_thickness*2)) / 2

    ## render

    *ellipse_svg_lines_minus_last, ellipse_svg_last_line = (

        get_ellipse_svg_text(
            cx,
            cy,
            rx,
            ry,
            outline_color='red',
            outline_width=outline_thickness,
        )

    ).splitlines()


    ### render a diagonal line surface

    ## find points of segment cutting ellipse

    rect = QRect(0, 0, *size)

    if outline_thickness > 1:

        deflation = -(outline_thickness + 6)

        rect.translate(-deflation, -deflation)

        new_width = rect.width() + deflation
        new_height = rect.height() + deflation

        rect.setWidth(new_width)
        rect.setHeight(new_height)

    p1, p2 = get_segment_points_cutting_ellipse(rect)

    x1, y1 = p1.toTuple()
    x2, y2 = p2.toTuple()

    ## render

    line_element_lines = (

        get_line_svg_text(
            x1,
            y1,
            x2,
            y2,
            outline_color='red',
            outline_width=outline_thickness,
        )

    ).splitlines()[1:-1]

    ###

    all_lines = ellipse_svg_lines_minus_last + line_element_lines
    all_lines.append(ellipse_svg_last_line)

    return '\n'.join(all_lines)



def get_segment_points_cutting_ellipse(rect):
    """Return points defining a segment that cuts an ellipse.

    Ideally, the segment would represent the points in a diagonal
    of the rectangle (bounding box of ellipse) that touches the
    ellipse outline. This should be the goal for a future update
    of this function.

    For now, I use an approximation by defining an arbitrary proportion
    of the semi-major axis of the ellipse (half the length of the
    largest axis) for the x or y coordinates of one of the points of
    the desired segment.

    This works fine, but must be updated to the ideal behaviour described
    earlier when I have the time to deepen my math knowledge in order
    to reproduce such behaviour.
    """
    ### apply different formulas depending on which is longer, the width
    ### or the length

    ## if width is longer or equal to height, the equation is...
    ## 
    ##  x²     y²
    ## ---- + ---- = 1
    ##  a²     b²
    ##
    ## where:
    ##
    ## a == half the major axis (half the width)
    ## b == half the minor axis (half the height)
    ## x == an arbitrary value as a proportion of a
    ## y == ? (the value we want to find)

    w, h = rect.size().toTuple()

    if w >= h:

        a = w / 2
        b = h / 2

        a_squared = a**2
        b_squared = b**2

        x = a * .71
        x_squared = x**2

        y_squared = (1 - (x_squared / a_squared)) * b_squared
        y = sqrt(y_squared)

    ## otherwise, if width is shorter than the height, the equation is...
    ## 
    ##  x²     y²
    ## ---- + ---- = 1
    ##  b²     a²
    ##
    ## where:
    ##
    ## a == half the major axis (half the height)
    ## b == half the minor axis (half the width)
    ## y == an arbitrary value as a proportion of a
    ## x == ? (the value we want to find)

    else:

        a = h / 2
        b = w / 2

        a_squared = a**2
        b_squared = b**2

        y = a * .65
        y_squared = y**2

        x_squared = (1 - (y_squared / a_squared)) * b_squared
        x = sqrt(x_squared)

    ### invert signal of y
    y = -y

    ### define first point, offset by the rect's center
    p1 = QPointF(x, y) + rect.center()

    ### define the second point as the inverted x and y
    ### coordinates, also offset by the rect's center
    p2 = QPointF(-x, -y) + rect.center()

    ### return the points
    return p1, p2
