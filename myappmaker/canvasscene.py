"""Facility with canvas to add and organize widgets."""

### standard library imports

from collections import deque

from itertools import repeat

from operator import itemgetter

from statistics import mean


### third-party imports

## PySide

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem

from PySide6.QtGui import QBrush, QPen, QPainterPath

from PySide6.QtCore import Qt, QTimer

## scipy
from scipy.spatial.distance import directed_hausdorff


### local imports

from .strokesmgr.strokesdisplay import STROKES_MAP, get_strokes_orientations
from .strokesmgr.constants import yield_offset_numpy_arrays



### constants/module level objs

SIZE = (1280, 720)

STROKES = deque()
STROKE_PATH_PROXIES = []

get_first_item = itemgetter(0)



### class definition

class CanvasScene(QGraphicsScene):

    def __init__(self, show_message_on_status_bar):

        super().__init__(0, 0, *SIZE)

        self.show_message_on_status_bar = show_message_on_status_bar

        ### strokes timer

        stimer = self.strokes_timer = QTimer()
        stimer.timeout.connect(self.process_strokes)

        ### rect

        rect = QGraphicsRectItem(200, 200, 100, 100)

        brush = QBrush(Qt.blue)
        rect.setBrush(brush)

        pen = QPen(Qt.green)
        pen.setWidth(10)
        rect.setPen(pen)

        self.addItem(rect)

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

        ### check list of strokes for matches

        orientations = get_strokes_orientations(STROKES)

        key_to_strokes = STROKES_MAP[orientations]

        if key_to_strokes:

            your_strokes = list(yield_offset_numpy_arrays(STROKES))

            hdist_widget_key_pairs = sorted(

                (

                    (

                        mean(

                            max(
                                directed_hausdorff(stroke_a, stroke_b)[0],
                                directed_hausdorff(stroke_b, stroke_a)[0],
                            )

                            for stroke_a, stroke_b in zip(widget_strokes, your_strokes)

                        ),

                        widget_key,

                    )

                    for widget_key, widget_strokes in key_to_strokes.items()
                ),

                key=get_first_item,

            )

            chosen_widget = hdist_widget_key_pairs[0][1]
            hdists = [round(item[0]) for item in hdist_widget_key_pairs]
            no_of_widgets = len(key_to_strokes)

            message = (
                f"Chose {chosen_widget} (hausdorff distances = {hdists})"
                f" among {no_of_widgets} widgets."
            )

        else:
            message = "Strokes didn't match any known widget."

        ###

        self.show_message_on_status_bar(message, 2000)
        STROKES.clear()
