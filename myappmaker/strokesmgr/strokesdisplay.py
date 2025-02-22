
### standard library imports

from shutil import rmtree

from collections import deque

from itertools import repeat


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


### local imports

from ..config import STROKES_DATA_DIR

from ..ourstdlibs.pyl import load_pyl, save_pyl

from .getnotfoundsvg import get_not_found_icon_svg_text

from .utils import update_strokes_map

from .constants import (
    STROKE_SIZE,
    STROKE_DIMENSION,
    STROKE_HALF_DIMENSION,
    LIGHT_GREY_QCOLOR,
)



### strokes display widget definition


SVG_RENDERER = (
    QSvgRenderer(
        QByteArray(
            get_not_found_icon_svg_text(STROKE_SIZE)
        )
    )
)

TOP_STROKE_PEN = QPen()
TOP_STROKE_PEN.setWidth(4)
TOP_STROKE_PEN.setColor(Qt.black)

THICKER_TOP_STROKE_PEN = QPen()
THICKER_TOP_STROKE_PEN.setWidth(6)
THICKER_TOP_STROKE_PEN.setColor(Qt.black)

THICKER_BOTTOM_STROKE_PEN = QPen()
THICKER_BOTTOM_STROKE_PEN.setWidth(6)
THICKER_BOTTOM_STROKE_PEN.setColor(LIGHT_GREY_QCOLOR)

START_POINT_BRUSH = QBrush()
START_POINT_BRUSH.setColor(Qt.red)
START_POINT_BRUSH.setStyle(Qt.SolidPattern)


def _get_stroke_bg(thickness=2):

    bg = QPixmap(*STROKE_SIZE)
    bg.fill(Qt.white)
    painter = QPainter(bg)

    pen = QPen()
    pen.setWidth(thickness)
    pen.setColor(LIGHT_GREY_QCOLOR)
    pen.setStyle(Qt.DashLine)

    painter.setPen(pen)

    width = height = STROKE_DIMENSION
    half_width = half_height = STROKE_HALF_DIMENSION

    hline = 0, half_height, width, half_height
    vline = half_width, 0, half_width, height

    painter.drawLine(*hline)
    painter.drawLine(*vline)

    ###

    pen.setStyle(Qt.SolidLine)

    half_thickness = thickness / 2

    painter.setPen(pen)
    painter.drawLine(width-half_thickness, 0, width-half_thickness, height)
    painter.drawLine(0, height-half_thickness, width, height-half_thickness)
    painter.end()

    return bg


class StrokesDisplay(QWidget):

    stroke_bg = None

    def __init__(self, widget_key):

        super().__init__()

        ###

        if self.__class__.stroke_bg is None:

            self.__class__.stroke_bg = _get_stroke_bg(2)
            self.__class__.thicker_stroke_bg = _get_stroke_bg(4)

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

        pixmap = QPixmap(*STROKE_SIZE)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        SVG_RENDERER.render(painter)
        painter.end()
        self.label.setPixmap(pixmap)

        layout = QHBoxLayout()
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

        ###

        strokes_dir = self.strokes_dir

        if strokes_dir.exists():
            rmtree(str(strokes_dir))

        strokes_dir.mkdir()

        ###

        for index, points in enumerate(strokes):

            save_pyl(
                points,
                (strokes_dir / f'stroke_{index:>02}.pyl'),
            )

        self.label.setPixmap(self.get_new_pixmap(strokes))

    def get_new_pixmap(self, strokes):

        full_size_strokes_pm = (
            get_full_size_strokes_pixmap(strokes, self.stroke_bg)
        )

        half_size_strokes_pm = (
            get_half_size_strokes_pixmap(strokes, self.thicker_stroke_bg)
        )

        fw, fh = full_size_strokes_pm.size().toTuple()
        hw, hh = half_size_strokes_pm.size().toTuple()

        width = fw + hw
        height = max(fh, hh)

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        painter.drawPixmap(0, 0, full_size_strokes_pm)
        painter.drawPixmap(STROKE_DIMENSION, 0, half_size_strokes_pm)
        painter.end()

        return pixmap


def get_full_size_strokes_pixmap(strokes, stroke_bg):

    pixmap = QPixmap(STROKE_DIMENSION, STROKE_DIMENSION)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.drawPixmap(0, 0, stroke_bg)

    painter.setPen(TOP_STROKE_PEN)

    offset = STROKE_HALF_DIMENSION

    for points in strokes:

        painter.drawPolyline(

            [

                QPointF(
                    a+offset,
                    b+offset,
                )

                for a, b in points

            ]

        )

    painter.end()

    return pixmap


def get_half_size_strokes_pixmap(strokes, stroke_bg):

    ### small strokes

    no_of_strokes = len(strokes)
    no_of_cols = 5
    no_of_rows, remainder = divmod(no_of_strokes, no_of_cols)

    if remainder:
        no_of_rows += 1

    ###

    width = (

        no_of_cols
        if no_of_strokes >= 6

        else no_of_strokes

    ) * STROKE_DIMENSION

    height = no_of_rows * STROKE_DIMENSION

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)

    ###

    strokes_deque = deque(strokes)
    bottom_strokes = []

    row = 0
    col = 0

    while strokes_deque:

        if col == no_of_cols:

            col = 0
            row += 1

        left = col * STROKE_DIMENSION
        top = row * STROKE_DIMENSION

        painter.drawPixmap(left, top, stroke_bg)

        top_stroke = strokes_deque.popleft()

        x_offset = (col * STROKE_DIMENSION) + STROKE_HALF_DIMENSION
        y_offset = (row * STROKE_DIMENSION) + STROKE_HALF_DIMENSION

        for points, pen, point_on_start in (

            *zip(
                bottom_strokes,
                repeat(THICKER_BOTTOM_STROKE_PEN),
                repeat(False),
            ),
            (top_stroke, THICKER_TOP_STROKE_PEN, True),

        ):

            offset_points = [

                QPointF(
                    a+x_offset,
                    b+y_offset,
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

        col += 1

    painter.end()

    tmode = Qt.TransformationMode.SmoothTransformation
    pixmap = pixmap.scaledToWidth(width/2, tmode)

    return pixmap

