"""Facility with canvas to add and organize widgets."""

### standard library import

from collections import deque

from functools import partial


### third-party imports

## PySide

from PySide6.QtWidgets import QGraphicsScene, QMenu

from PySide6.QtGui import QBrush, QPen, QPainterPath, QCursor

from PySide6.QtCore import Qt, QPoint, QTimer


### local imports

from .strokesmgmt.utils import get_stroke_matches_data

from .widgets import (
    LabelItem,
    UncheckedCheckBoxItem,
    CheckedCheckBoxItem,
)



### constants/module level objs

SIZE = (1280, 720)

STROKES = deque()
STROKE_PATH_PROXIES = []



### class definition

class CanvasScene(QGraphicsScene):

    def __init__(self, main_window, show_message_on_status_bar):

        super().__init__(0, 0, *SIZE)

        self.cursor = QCursor()

        self.menu_offset = QPoint(-18, -12)
        self.cursor_offset = QPoint(30, 0)

        self.main_window = main_window

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

        ### only proceed if STROKES have at least 2 points

        if any(len(stroke) < 2 for stroke in STROKES):

            STROKES.clear()
            return

        ### check list of strokes for matches

        match_data = get_stroke_matches_data(STROKES)

        STROKES.clear()

        ###

        menu_items = match_data['menu_items']
        chosen_widget_key = match_data['chosen_widget_key']

        if not menu_items and not chosen_widget_key:

            self.show_message_on_status_bar(match_data['report'], 2500)
            return

        elif menu_items:
            
            menu = QMenu(self.main_window)

            action_to_key = {}

            for index, (_, widget_key) in enumerate(menu_items):

                ac = menu.addAction(f"{widget_key}")

                if index == 0:
                    first_action = ac

                action_to_key[ac] = widget_key

            ### get position for menu

            cursor_pos = self.cursor.pos()

            menu_pos = cursor_pos + self.menu_offset
            new_cursor_pos = cursor_pos + self.cursor_offset

            QTimer.singleShot(1, partial(self.cursor.setPos, new_cursor_pos))

            ###
            chosen_action = menu.exec(menu_pos, first_action)

            if chosen_action is None:

                report = "No widget was chosen"
                self.show_message_on_status_bar(report, 2500)
                return

            else:
                chosen_widget_key = action_to_key[chosen_action]

        elif chosen_widget_key:

            rounded_hd = round(match_data['sym_hausdorff_dist'])
            no_of_widgets = match_data['no_of_widgets']

            report = (
                f"Chose {chosen_widget_key}"
                f" (hausdorff of drawing = ~{rounded_hd})"
                f" among {no_of_widgets} widgets."
            )

            self.show_message_on_status_bar(report, 2500)

        ### get position for widget

        union_of_strokes = match_data['union_of_strokes']
        xs, ys = zip(*union_of_strokes)

        left = min(xs)
        right = max(xs)

        width = right - left

        top = min(ys)
        bottom = max(ys)

        height = bottom - top

        x = left + width/2
        y = top + height/2

        if chosen_widget_key == 'label':
            item_class = LabelItem

        elif chosen_widget_key == 'unchecked_check_box':
            item_class = UncheckedCheckBoxItem 

        elif chosen_widget_key == 'checked_check_box':
            item_class = CheckedCheckBoxItem

        item = item_class()
        self.addItem(item)
        item.setPos(x, y)
