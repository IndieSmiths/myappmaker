"""Facility for constants."""

### third-party imports

from PySide6.QtGui import QColor

from numpy import array as numpy_array



STROKE_DIMENSION = 300
STROKE_SIZE = (STROKE_DIMENSION,) * 2

STROKE_HALF_DIMENSION = STROKE_DIMENSION / 2

LIGHT_GREY_QCOLOR = QColor(230, 230, 230)


def yield_offset_numpy_arrays(strokes):
    """Yield stroke points moved so first one is at origin."""

    for points in strokes:

        x1, y1 = points[0]

        yield numpy_array(

            [
                (a - x1, b - y1)
                for a, b in points
            ]

        )
