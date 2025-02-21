"""Facility with canvas to add and organize widgets."""

### standard library imports

from collections import deque

from itertools import repeat

from operator import itemgetter


### third-party imports

## PySide

from PySide6.QtWidgets import QGraphicsScene

from PySide6.QtGui import QBrush, QPen, QPainterPath

from PySide6.QtCore import Qt, QTimer

## scipy
from scipy.spatial.distance import directed_hausdorff


### local imports

from .strokesmgr.utils import (
    STROKES_MAP,
    are_ratios_logs_similar,
    get_strokes_ratios_logs,
    get_offset_union_array,
)



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

        no_of_strokes = len(STROKES)

        possible_matches = STROKES_MAP[no_of_strokes]

        if possible_matches:

            union_of_strokes = sum(STROKES, [])

            your_ratios_logs = get_strokes_ratios_logs(union_of_strokes, STROKES)

            your_union_array = get_offset_union_array(union_of_strokes)

            # TODO allows this maximum log diff tolerance to be set by the user
            ratio_log_diff_tolerance = 0.6

            hdist_widget_key_pairs = sorted(

                (

                    ### item

                    (

                        max(
                            directed_hausdorff(your_union_array, widget_union_array)[0],
                            directed_hausdorff(widget_union_array, your_union_array)[0],
                        ),

                        widget_key,

                    )

                    ### source

                    for widget_key, (widget_ratios_logs, widget_union_array)
                    in possible_matches.items()

                    ## filter

                    if are_ratios_logs_similar(
                         your_ratios_logs,
                         widget_ratios_logs,
                         ratio_log_diff_tolerance,
                       )

                ),

                key=get_first_item,

            )

            # default message
            message = "Possible matches weren't similar enough."

            # check whether distances of best strokes are within
            # tolerable distance

            if hdist_widget_key_pairs:

                (avg_of_hd_distances, corresponding_widget) = (
                    hdist_widget_key_pairs[0]
                )
                no_of_widgets = len(possible_matches)

                # TODO allows this maximum tolerable hausdorff distance
                # to be set by the user
                maximum_tolerable_hausdorff_distance = 60

                if avg_of_hd_distances < maximum_tolerable_hausdorff_distance:

                    rounded_avg_hd = round(avg_of_hd_distances)

                    # overwrite message

                    message = (
                        f"Chose {corresponding_widget}"
                        f" (average hausdorff of strokes = ~{rounded_avg_hd})"
                        f" among {no_of_widgets} widgets."
                    )

                else:
                    message += "(hausdorff distance too large)"

            else:
                message += " (proportions didn't match)"

        else:
            message = "No widget with this stroke count"

        ###

        self.show_message_on_status_bar(message, 2500)
        STROKES.clear()
