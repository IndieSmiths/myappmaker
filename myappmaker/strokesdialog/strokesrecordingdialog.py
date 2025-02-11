"""Facility with canvas to record strokes."""

### standard library imports

from collections import deque

from operator import itemgetter


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QGraphicsScene,
    QGraphicsView,
    QDialog,
    QVBoxLayout,
    QLabel,
)

from PySide6.QtGui import QPen, QPainterPath

from PySide6.QtCore import Qt, QTimer, QLine

## numpy

from numpy import array as numpy_array


### local imports
from .constants import STROKE_DIMENSION, STROKE_SIZE, STROKE_HALF_DIMENSION



### module level objs

STROKES = deque()
STROKE_PATH_PROXIES = []

get_first_item = itemgetter(0)
get_second_item = itemgetter(1)



### class definition

class StrokesRecordingScene(QGraphicsScene):

    def __init__(self, recording_dlg):

        super().__init__(0, 0, *STROKE_SIZE)

        self.recording_dlg = recording_dlg

        ### strokes timer

        stimer = self.strokes_timer = QTimer()
        stimer.timeout.connect(self.process_strokes)

        ###

        black_pen = QPen(Qt.black)
        black_pen.setWidth(1)

        hline = (

            QLine(
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
                STROKE_HALF_DIMENSION,
            )

        )

        self.hline_proxy = self.addLine(hline, black_pen)

        vline = (

            QLine(
                STROKE_HALF_DIMENSION,
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
            )

        )

        self.vline_proxy = self.addLine(vline, black_pen)

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
        self.strokes_timer.start(500)

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

        self.recording_dlg.stroke_display.update_and_save_strokes(offset_strokes)


class StrokesRecordingDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Strokes Recording")

        vlayout = QVBoxLayout()

        ### label

        self.label = QLabel('Draw widget below')
        vlayout.addWidget(self.label)

        ### recording scene and its view

        scene = self.scene = StrokesRecordingScene(recording_dlg=self)
        view = self.view = QGraphicsView(scene)
        vlayout.addWidget(self.view)

        self.setLayout(vlayout)

    def prepare_session(self, stroke_display):

        self.label.setText(stroke_display.widget_key)
        self.stroke_display = stroke_display
