"""Facility with canvas to record strokes."""

### standard library import
from collections import deque


### third-party imports

## PySide6

from PySide6.QtWidgets import (
    QWidget,
    QLayout,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
)

from PySide6.QtGui import QPen, QPainterPath

from PySide6.QtCore import Qt, QTimer, QLine


### local imports

from .constants import (
    STROKE_DIMENSION,
    STROKE_SIZE,
    STROKE_HALF_DIMENSION,
    LIGHT_GREY_QCOLOR,
)



### module level objs

STROKES = deque()
STROKE_PATH_PROXIES = []


### class definition

class StrokesRecordingScene(QGraphicsScene):

    def __init__(self):

        super().__init__(0, 0, *STROKE_SIZE)

        ### strokes timer

        stimer = self.strokes_timer = QTimer()
        stimer.timeout.connect(self.process_strokes)

        ###

        self.setBackgroundBrush(Qt.white)

        ###

        dash_pen = QPen()
        dash_pen.setWidth(2)
        dash_pen.setStyle(Qt.DashLine)
        dash_pen.setColor(LIGHT_GREY_QCOLOR)

        hline = (

            QLine(
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
                STROKE_HALF_DIMENSION,
            )

        )

        self.hline_proxy = self.addLine(hline, dash_pen)

        vline = (

            QLine(
                STROKE_HALF_DIMENSION,
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
            )

        )

        self.vline_proxy = self.addLine(vline, dash_pen)

        ###

        self.strokes_pen = QPen(Qt.red)
        self.strokes_pen.setWidth(3)

        ###
        self.last_point = None

    def mouseMoveEvent(self, event):

        ### leave right away if left button is NOT pressed

        if not (event.buttons() & Qt.LeftButton):
            return

        ### grab/reference points locally

        point = event.scenePos()
        last_point = self.last_point

        ### get tuple of coordinates from current point
        coords = point.x(), point.y()

        ### if there's no last point, it means the user just began drawing a
        ### stroke

        if last_point is None:

            ### stop counter
            self.strokes_timer.stop()

            ### create a path and its QGraphics proxy to represent the stroke

            path = self.path = QPainterPath()
            self.path_proxy = self.addPath(path, self.strokes_pen)

            ### move path to current point and store such point as last one

            path.moveTo(*coords)
            self.last_point = point

            ### store coordinates in new list within STROKES
            STROKES.append([coords])

            ### store path proxy
            STROKE_PATH_PROXIES.append(self.path_proxy)

            ### then leave
            return

        ### if the points are too close, leave as well
        if (last_point - point).manhattanLength() <= 3:
            return


        ### otherwise, draw a line on our board and update its
        ### QGraphics proxy

        self.path.lineTo(point.x(), point.y())
        self.path_proxy.setPath(self.path)

        ### store coordinates
        STROKES[-1].append(coords)

        ### reference current point as last one
        self.last_point = point


    def mouseReleaseEvent(self, event):

        self.last_point = None
        self.strokes_timer.start(700)

    def process_strokes(self):

        ### remove path proxies

        self.strokes_timer.stop()

        for item in STROKE_PATH_PROXIES:
            self.removeItem(item)

        STROKE_PATH_PROXIES.clear()

        del self.path, self.path_proxy

        offset_strokes = []

        while STROKES:

            points = STROKES.popleft()

            offset_points = [
                (a - STROKE_HALF_DIMENSION, b - STROKE_HALF_DIMENSION)
                for a, b in points
            ]

            offset_strokes.append(offset_points)

        (
            self
            .stroke_display
            .update_and_save_strokes(offset_strokes)
        )



class StrokesRecordingPanel(QWidget):

    def __init__(self, parent=None):

        super().__init__()

        scene = self.scene = StrokesRecordingScene()
        self.view = QGraphicsView(scene)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

    def prepare(self, stroke_display):
        self.scene.stroke_display = stroke_display
