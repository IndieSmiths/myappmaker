"""Facility with canvas to add and organize widgets."""

### standard library import
from collections import deque


### third-party imports

## PySide

from PySide6.QtWidgets import QGraphicsScene

from PySide6.QtGui import QBrush, QPen, QPainterPath

from PySide6.QtCore import Qt


### local imports

from .strokesmgmt.utils import get_stroke_matches_data

from .widgets import (
    get_label,
    get_unchecked_check_box,
    get_checked_check_box,
)



### constants/module level objs

SIZE = (1280, 720)

STROKES = deque()
STROKE_PATH_PROXIES = []



### class definition

class CanvasScene(QGraphicsScene):

    def __init__(self, show_message_on_status_bar):

        super().__init__(0, 0, *SIZE)

        self.setBackgroundBrush(Qt.white)

        self.show_message_on_status_bar = show_message_on_status_bar
        ### 

        self.strokes_pen = QPen(Qt.red)
        self.strokes_pen.setWidth(3)

        ###

        self.last_point = None
        self.watch_out_for_shift_release = False

    def mouseMoveEvent(self, event):

        ### leave right away if either...
        ### - mouse left button is NOT pressed
        ### - shift key is NOT pressed

        if (
            not (event.buttons() & Qt.LeftButton)
            or not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            return

        ###
        self.watch_out_for_shift_release = True

        ### grab/reference points locally

        point = event.scenePos()
        last_point = self.last_point

        ### get tuple of coordinates from current point
        coords = point.x(), point.y()

        ### if there's no last point, it means the user just began drawing a
        ### stroke

        if last_point is None:

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

    def keyReleaseEvent(self, event):

        if (
            event.key() == Qt.Key.Key_Shift
            and self.watch_out_for_shift_release
        ):

            self.watch_out_for_shift_release = False
            self.process_strokes()

    def process_strokes(self):

        ### remove path proxies

        for item in STROKE_PATH_PROXIES:
            self.removeItem(item)

        STROKE_PATH_PROXIES.clear()

        del self.path, self.path_proxy

        ### check list of strokes for matches

        match_data = get_stroke_matches_data(STROKES)

        STROKES.clear()

        if match_data['chosen_widget_key']:

            chosen_widget_key = match_data['chosen_widget_key']
            rounded_hd = round(match_data['hausdorff_distance'])
            no_of_widgets = match_data['no_of_widgets']

            report = (
                f"Chose {chosen_widget_key}"
                f" (hausdorff of drawing = ~{rounded_hd})"
                f" among {no_of_widgets} widgets."
            )

            ### get position for widget

            union_of_strokes = match_data['union_of_strokes']
            xs, ys = zip(*union_of_strokes)

            left = min(xs)
            right = max(xs)

            width = right - left

            top = min(ys)
            bottom = max(ys)

            height = top - bottom

            x = left + width/2
            y = top + height/2

            # XXX the subtraction from y below is arbitrary: it simply
            # looks better positioned this way;
            #
            # investigate why is that when you have the time (for now
            # it is not an issue cause the user will be able to
            # reposition objects on canvas)
            y -= height

            ###

            if chosen_widget_key == 'label':

                # using get_label for the sake of conformity here,
                # since we could just use QGraphicsScene.addText()
                # instead
                get_widget = get_label

            elif chosen_widget_key == 'unchecked_check_box':
                get_widget = get_unchecked_check_box

            elif chosen_widget_key == 'checked_check_box':
                get_widget = get_checked_check_box

            widget_proxy = self.addWidget(get_widget())
            widget_proxy.setPos(x, y)

        else:
            report = match_data['report']

        ###
        self.show_message_on_status_bar(report, 2500)
