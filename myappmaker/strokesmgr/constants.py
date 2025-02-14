"""Facility for constants."""

### third-party imports

from PySide6.QtGui import QColor

from numpy import array as numpy_array



STROKE_DIMENSION = 300
STROKE_SIZE = (STROKE_DIMENSION,) * 2

STROKE_HALF_DIMENSION = STROKE_DIMENSION / 2

LIGHT_GREY_QCOLOR = QColor(230, 230, 230)


def yield_offset_numpy_arrays(strokes):
    """Yield strokes moved to origin.

    That is, their imaginary bounding box is moved so that their topleft
    is at the origin (0, 0).
    """

    for points in strokes:

        xs, ys = zip(*points)

        left = min(xs)
        top = min(ys)

        yield numpy_array(

            [
                (a - left, b - top)
                for a, b in points
            ]

        )
