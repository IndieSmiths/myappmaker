
### standard library imports

from shutil import rmtree

from collections import defaultdict, deque

from itertools import repeat

from contextlib import suppress


### third-party imports

## PySide6

from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QLabel,
)

from PySide6.QtSvg import QSvgRenderer

from PySide6.QtCore import Qt, QByteArray, QPointF

from PySide6.QtGui import QPainter, QPixmap, QPen, QBrush

## numpy
from numpy import array as numpy_array


### local imports

from ..config import STROKES_DATA_DIR

from ..ourstdlibs.pyl import load_pyl, save_pyl

from .getnotfoundsvg import get_not_found_icon_svg_text

from .constants import (
    STROKE_SIZE,
    STROKE_DIMENSION,
    STROKE_HALF_DIMENSION,
    LIGHT_GREY_QCOLOR,
)



### strokes display widget definition

STROKES_MAP = defaultdict(dict)
#

NOT_FOUND_SVG_BYTE_ARRAY = (

    QByteArray(
        get_not_found_icon_svg_text(STROKE_SIZE)
    )

)

TOP_STROKE_PEN = QPen()
TOP_STROKE_PEN.setWidth(4)
TOP_STROKE_PEN.setColor(Qt.black)

BOTTOM_STROKE_PEN = QPen()
BOTTOM_STROKE_PEN.setWidth(4)
BOTTOM_STROKE_PEN.setColor(LIGHT_GREY_QCOLOR)

START_POINT_BRUSH = QBrush()
START_POINT_BRUSH.setColor(Qt.red)
START_POINT_BRUSH.setStyle(Qt.SolidPattern)


def _get_stroke_bg():

    bg = QPixmap(*STROKE_SIZE)
    bg.fill(Qt.white)
    painter = QPainter(bg)

    pen = QPen()
    pen.setWidth(2)
    pen.setColor(LIGHT_GREY_QCOLOR)
    pen.setStyle(Qt.DashLine)

    painter.setPen(pen)

    width = height = STROKE_DIMENSION
    half_width = half_height = STROKE_HALF_DIMENSION

    hline = 0, half_height, width, half_height
    vline = half_width, 0, half_width, height

    painter.drawLine(*hline)
    painter.drawLine(*vline)

    pen.setStyle(Qt.SolidLine)
    painter.setPen(pen)
    painter.drawLine(width-1, 0, width-1, height)
    painter.end()

    return bg


class StrokesDisplay(QWidget):

    stroke_bg = None

    def __init__(self, widget_key):

        super().__init__()

        ###
        if self.__class__.stroke_bg is None:
            self.__class__.stroke_bg = _get_stroke_bg()

        ###

        self.label = QLabel()

        self.widget_key = widget_key

        self.strokes_dir = strokes_dir = (
            STROKES_DATA_DIR / f'{widget_key}_strokes_dir'
        )

        if strokes_dir.exists():

            pyls = (
                sorted(
                    str(path)
                    for path in strokes_dir.glob('*.pyl')
                )
            )

            if pyls:
                self.init_strokes_display(pyls)

            else:
                self.init_empty_display()

        else:
            self.init_empty_display()


    def init_empty_display(self):

        # TODO perhaps this renderer can be created only once
        # and reused (if possible, as a top level object)
        renderer = QSvgRenderer(NOT_FOUND_SVG_BYTE_ARRAY)

        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)#, pixmap.rect())
        painter.end()
        self.label.setPixmap(pixmap)

        #svg_widget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)

        layout = QHBoxLayout()
        #layout.addWidget(svg_widget)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def init_strokes_display(self, stroke_paths):

        strokes = list(map(load_pyl, stroke_paths))
        update_strokes_map(self.widget_key, strokes)

        self.label.setPixmap(self.get_new_pixmap(strokes))

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_and_save_strokes(self, strokes):

        update_strokes_map(self.widget_key, strokes)

        strokes_dir = self.strokes_dir

        if strokes_dir.exists():
            rmtree(str(strokes_dir))

        strokes_dir.mkdir()

        for index, points in enumerate(strokes):

            save_pyl(
                points,
                (strokes_dir / f'stroke_{index:>02}.pyl'),
            )

        self.stroke_arrays = list(map(numpy_array, strokes))

        self.label.setPixmap(self.get_new_pixmap(strokes))

    def get_new_pixmap(self, strokes):

        n = len(strokes)
        width = n * STROKE_DIMENSION
        height = STROKE_DIMENSION

        pixmap = QPixmap(width, height)

        painter = QPainter(pixmap)
        painter.drawTiledPixmap(0, 0, width, height, self.stroke_bg)

        x_increment = -STROKE_HALF_DIMENSION
        y_increment = 150

        strokes_deque = deque(strokes)
        bottom_strokes = []

        while strokes_deque:

            top_stroke = strokes_deque.popleft()

            x_increment += STROKE_DIMENSION

            for points, pen, point_on_start in (

                *zip(
                    bottom_strokes,
                    repeat(BOTTOM_STROKE_PEN),
                    repeat(False),
                ),
                (top_stroke, TOP_STROKE_PEN, True),

            ):

                offset_points = [

                    QPointF(
                        a+x_increment,
                        b+y_increment,
                    )

                    for a, b in points

                ]

                painter.setPen(pen)
                painter.drawPolyline(offset_points)

                if point_on_start:

                    ###

                    painter.setPen(Qt.NoPen)
                    painter.setBrush(START_POINT_BRUSH)
                    painter.setOpacity(.6)

                    ###
                    painter.drawEllipse(QPointF(offset_points[0]), 8, 8)

                    ###

                    painter.setPen(Qt.SolidLine)
                    painter.setBrush(Qt.NoBrush)
                    painter.setOpacity(1.0)

            bottom_strokes.append(top_stroke)

        painter.end()

        return pixmap

def update_strokes_map(widget_key, strokes):

    for inner_map in STROKES_MAP.values():

        with suppress(KeyError):
            del inner_map[widget_key]

    ###
    orientations = get_strokes_orientations(strokes)

    ### offset strokes for easier comparison

    offset_strokes_arrays = []

    for points in strokes:

        xs, ys = zip(*points)

        left = min(xs)
        top = min(ys)

        offset_strokes_arrays.append(

            numpy_array(

                [
                    (a - left, b - top)
                    for a, b in points
                ]

            )

        )

    ###
    STROKES_MAP[orientations][widget_key] = offset_strokes_arrays


def get_strokes_orientations(strokes):

    orientations = []

    for points in strokes:

        xs, ys = zip(*points)

        left = min(xs)
        right = max(xs)

        width = right - left

        top = min(ys)
        bottom = max(ys)

        height = bottom - top

        if width * .7 > height:
            orientation = 'landscape'

        elif height * .7 > width:
            orientation = 'portrait'

        else:
            orientation = 'square'

        orientations.append(orientation)

    return tuple(orientations)

