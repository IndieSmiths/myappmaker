"""Facility for displaying individual strokes next to each other."""

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



### module-level objects

## svg renderer

SVG_RENDERER = (
    QSvgRenderer(
        QByteArray(
            get_not_found_icon_svg_text(STROKE_SIZE)
        )
    )
)

## pens and brush

TOP_STROKE_PEN = QPen()
TOP_STROKE_PEN.setWidth(4)
TOP_STROKE_PEN.setColor(Qt.black)

# although thicker, the pens below will be used to
# draw on a pixmap that will subsequently be scaled
# down to half its size

THICKER_TOP_STROKE_PEN = QPen()
THICKER_TOP_STROKE_PEN.setWidth(6)
THICKER_TOP_STROKE_PEN.setColor(Qt.black)

THICKER_BOTTOM_STROKE_PEN = QPen()
THICKER_BOTTOM_STROKE_PEN.setWidth(6)
THICKER_BOTTOM_STROKE_PEN.setColor(LIGHT_GREY_QCOLOR)

START_POINT_BRUSH = QBrush()
START_POINT_BRUSH.setColor(Qt.red)
START_POINT_BRUSH.setStyle(Qt.SolidPattern)


### utility function

def _get_stroke_bg(dash_thickness=2):
    """Create background pixmap to display stroke."""

    ### instantiate and fill pixmap

    pixmap = QPixmap(*STROKE_SIZE)
    pixmap.fill(Qt.white)

    ### create painter associated with it
    painter = QPainter(pixmap)

    ### define and associate dashed line pen with painter

    pen = QPen()
    pen.setWidth(dash_thickness)
    pen.setColor(LIGHT_GREY_QCOLOR)
    pen.setStyle(Qt.DashLine)

    painter.setPen(pen)

    ### draw perpendicular dashed lines crossing in the middle

    width = height = STROKE_DIMENSION
    half_width = half_height = STROKE_HALF_DIMENSION

    hline = 0, half_height, width, half_height
    vline = half_width, 0, half_width, height

    painter.drawLine(*hline)
    painter.drawLine(*vline)

    ### draw solid lines at the right and bottom edges to help
    ### separate the pixmap when it is used to draw strokes
    ### adjacent to each other

    pen.setStyle(Qt.SolidLine)

    half_thickness = dash_thickness / 2

    painter.setPen(pen)
    painter.drawLine(width-half_thickness, 0, width-half_thickness, height)
    painter.drawLine(0, height-half_thickness, width, height-half_thickness)

    ### finish drawing operations and return the pixmap

    painter.end()
    return pixmap


### class definition for strokes display panel widget

class StrokesDisplayPanel(QWidget):
    """Panel to display drawing and the different strokes that compose it."""

    ## placeholder class attribute for stroke backgrounds used

    stroke_bg = None
    thicker_stroke_bg = None

    def __init__(self, widget_key):
        """Initialize super class and setup widget contents."""

        ### initialize superclass
        super().__init__()

        ### if stroke backgrounds don't exist, create them

        if self.__class__.stroke_bg is None:

            self.__class__.stroke_bg = _get_stroke_bg(2)
            self.__class__.thicker_stroke_bg = _get_stroke_bg(4)

        ### create label used to hold pixmap wherein to draw this
        ### panel
        self.label = QLabel()

        ### store given widget key
        self.widget_key = widget_key

        ### use key to verify existence of strokes for specific
        ### widget associated with this panel;
        ###
        ### if such strokes exist, we draw them, otherwise we indicate
        ### the panel is empty by drawing a specific icon

        ## directory wherein to find data defining strokes (if data
        ## exists)

        self.strokes_dir = strokes_dir = (
            STROKES_DATA_DIR / f'{widget_key}_strokes_dir'
        )

        ## verify and add contents depending on existence of strokes

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
        """Create pixmap containing SVG icon indicating it is empty."""

        ### create pixmap with SVG icon drawn onto it

        pixmap = QPixmap(*STROKE_SIZE)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        SVG_RENDERER.render(painter)
        painter.end()

        ### apply it to the label
        self.label.setPixmap(pixmap)

        ### create layout for this panel with label added to it

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def init_strokes_display(self, stroke_paths):
        """Create pixmap showing drawing and each stroke that composes it."""

        ### load Python literals representing each stroke
        strokes = list(map(load_pyl, stroke_paths))

        ### update general map containing strokes for specific widget
        ### associated with this panel
        update_strokes_map(self.widget_key, strokes)

        ### create pixmap with the strokes and apply it to the label
        self.label.setPixmap(self.get_new_pixmap(strokes))

        ### create layout for this panel with label added to it

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_and_save_strokes(self, strokes):
        """Rebuild pixmap with updated strokes (and new formed drawing)."""

        ### update general map containing strokes for specific widget
        ### associated with this panel
        update_strokes_map(self.widget_key, strokes)

        ### delete folder holding data defining previous strokes and
        ### recreate it anew with data for new strokes

        ## delete and recreate folder

        strokes_dir = self.strokes_dir

        if strokes_dir.exists():
            rmtree(str(strokes_dir))

        strokes_dir.mkdir()

        ### save each stroke as a Python literal

        for index, points in enumerate(strokes):

            save_pyl(
                points,
                (strokes_dir / f'stroke_{index:>02}.pyl'),
            )

        ### finally set a new pixmap showing the updated strokes and
        ### full drawing they form
        self.label.setPixmap(self.get_new_pixmap(strokes))

    def get_new_pixmap(self, strokes):
        """Return new pixmap showing drawing and strokes that compose it."""

        ### create pixmap for drawing (full size strokes combined)

        full_size_drawing_pm = (
            get_pixmap_with_full_size_strokes_combined(strokes, self.stroke_bg)
        )

        ### create pixmap with all strokes at half their size distributed in
        ### a grid

        half_size_strokes_grid_pm = (

            get_pixmap_with_half_size_strokes_in_a_grid(
                strokes,
                self.thicker_stroke_bg,
            )

        )

        ### combine the two pixmaps into one new pixmap

        fw, fh = full_size_drawing_pm.size().toTuple()
        hw, hh = half_size_strokes_grid_pm.size().toTuple()

        width = fw + hw
        height = max(fh, hh)

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        painter.drawPixmap(0, 0, full_size_drawing_pm)
        painter.drawPixmap(STROKE_DIMENSION, 0, half_size_strokes_grid_pm)

        painter.end()

        ### return new pixmap
        return pixmap


def get_pixmap_with_full_size_strokes_combined(strokes, stroke_bg):
    """Return pixmap for drawing (full size strokes combined)"""

    ### instantiate and fill pixmap

    pixmap = QPixmap(STROKE_DIMENSION, STROKE_DIMENSION)
    pixmap.fill(Qt.white)

    ### create painter object to manipulate pixmap and draw background
    ### on it

    painter = QPainter(pixmap)
    painter.drawPixmap(0, 0, stroke_bg)

    ### draw each stroke on the pixmap, one on top of the other

    ## set a pre-made pen for the painter
    painter.setPen(TOP_STROKE_PEN)

    ## define offset for points so strokes are centered on the background
    offset = STROKE_HALF_DIMENSION

    ## draw each stroke as a polyline

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

    ### finish drawing operations and return the pixmap

    painter.end()
    return pixmap


def get_pixmap_with_half_size_strokes_in_a_grid(strokes, stroke_bg):

    ### define number of columns to use, then calculate the number of rows
    ### based on the number of columns available and the quantity of strokes

    ## columns
    no_of_cols = 5

    ## rows

    no_of_strokes = len(strokes)
    no_of_rows, remainder = divmod(no_of_strokes, no_of_cols)

    if remainder:
        no_of_rows += 1

    ### width is the dimension of one stroke times multiplied by either
    ### the quantity of columns (if we'll use all of them), or by the quantity
    ### of strokes (if their quantity is so small that we won't need to use
    ### all columns)

    will_use_all_columns = no_of_strokes > no_of_cols

    width = STROKE_DIMENSION * (

        no_of_cols
        if will_use_all_columns

        else no_of_strokes

    )

    ### height is the dimension of one stroke times the number of rows
    height = STROKE_DIMENSION * no_of_rows

    ### now create a pixmap filled with transparency and a painter object
    ### associated with it

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)

    ### draw strokes one by one on the pixmap as a grid

    ## use a deque to hold the strokes
    strokes_deque = deque(strokes)

    ## create a list to keep track of previous strokes, that is,
    ## the strokes drawn before the current one being draw;
    ##
    ## such strokes will be repeated using a lighter color under the
    ## current stroke, which will be drawn with a darker color on top of them
    previous_strokes = []

    ## start drawing while there are strokes

    # variables to keep track of row and column

    row = 0
    col = 0

    # index of last column
    last_column_index = no_of_cols - 1

    # loop wherein to draw each stroke

    while strokes_deque:

        ## if we are past the last column, advance one row and get back to
        ## the first column

        if col > last_column_index:

            row += 1
            col = 0

        ## calculate left and top positions wherein to draw this stroke
        ## in the grid

        left = col * STROKE_DIMENSION
        top = row * STROKE_DIMENSION

        ## start by drawing the background
        painter.drawPixmap(left, top, stroke_bg)

        ## reference the current stroke, which will be drawn on top
        ## of all the previous ones (if any)
        top_stroke = strokes_deque.popleft()

        ## calculate x and y offsets so strokes are drawn centered
        ## on this spot of the grid

        x_offset = (col * STROKE_DIMENSION) + STROKE_HALF_DIMENSION
        y_offset = (row * STROKE_DIMENSION) + STROKE_HALF_DIMENSION

        ## now draw each stroke, starting with the previous ones which
        ## are drawn with a lighter pen and ending with the current stroke,
        ## drawn on top of them with a darker color

        for points, pen, point_on_start in (

            ## previous strokes (if any) to be drawn with a lighter color

            *zip(
                previous_strokes,
                repeat(THICKER_BOTTOM_STROKE_PEN),
                repeat(False),
            ),

            ## top stroke to be drawn with a darker color
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

            ## the current/top stroke is the only one which is
            ## drawn with its first point highlighted, to indicate
            ## the spot from which the user begins drawing the stroke

            if point_on_start:

                ### set specific pen, brush and opacity

                painter.setPen(Qt.NoPen)
                painter.setBrush(START_POINT_BRUSH)
                painter.setOpacity(.6)

                ### draw the point
                painter.drawEllipse(QPointF(offset_points[0]), 8, 8)

                ### restore pen, brush and opacity

                painter.setPen(Qt.SolidLine)
                painter.setBrush(Qt.NoBrush)
                painter.setOpacity(1.0)

        ## store current stroke as a previous one for the next iteration
        ## (in case there are more strokes to draw)
        previous_strokes.append(top_stroke)

        ## advance one column
        col += 1

    ### finish drawing operations
    painter.end()

    ### finally get new pixmap which corresponds to original one scaled down
    ### to half its size and return it

    scaled_down_pixmap = pixmap.scaledToWidth(
        width/2,
        Qt.TransformationMode.SmoothTransformation, # transformation mode

    )

    return scaled_down_pixmap

