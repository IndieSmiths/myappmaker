"""Facility with canvas wherein to lay out widgets to design apps."""

### standard library import

from collections import deque

from functools import partial


### third-party imports

## PySide

from PySide6.QtWidgets import QGraphicsScene, QMenu

from PySide6.QtGui import QBrush, QPen, QPainterPath

from PySide6.QtCore import Qt, QPoint, QTimer


### local imports

from .config import REFS

from .strokesmgmt.utils import get_stroke_matches_data

from .widgets import (
    LabelItem,
    UncheckedCheckBoxItem,
    CheckedCheckBoxItem,
    LineEditItem,
    ButtonItem,
)



### constants/module level objs

SIZE = (1280, 720)

STROKES = deque()
STROKE_PATH_PROXIES = []



### class definition

class CanvasScene(QGraphicsScene):
    """Specialized QGraphicsScene wherein to lay out widgets to design apps."""

    def __init__(self, main_window, show_message_on_status_bar):
        """Setup scene.

        Parameters
        ==========
        main_window
            Reference to main window.
        show_message_on_status_bar
            Callable used to show message on the status bar.
        """
        ### initialize super class with a given size for maximum
        ### performance
        super().__init__(0, 0, *SIZE)

        ### store given references

        self.main_window = main_window
        self.show_message_on_status_bar = show_message_on_status_bar

        ### store 2D offsets for later use

        self.menu_offset = QPoint(-18, -12)
        self.cursor_offset = QPoint(30, 0)

        ### instantiate and store pen used for drawing

        self.strokes_pen = QPen(Qt.red)
        self.strokes_pen.setWidth(3)

        ### set background to white
        self.setBackgroundBrush(Qt.white)

        ### set placeholder/flag attributes

        self.last_point = None
        self.watch_out_for_shift_release = False

    def mouseMoveEvent(self, event):
        """Respond to mouse movement if meaningful to widget's purpose.

        The movement is meaningful only if both mouse left button and shift
        key are pressed, in which case we make a series of setups to either
        start or keep recording a drawing (if we already started it
        previously).
        """

        ### leave right away if either...
        ###
        ### - mouse left button is NOT pressed
        ### - shift key is NOT pressed

        if (
            not (event.buttons() & Qt.LeftButton)
            or not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            return

        ### turn on the flag that indicates we must watch out for the release
        ### of the shift key
        self.watch_out_for_shift_release = True

        ### grab/reference points locally

        point = event.scenePos()
        last_point = self.last_point

        ### if there's no last point, it means the user just began drawing a
        ### stroke, so create and store path

        if last_point is None:

            ### create a path and its QGraphics proxy to represent the stroke

            path = self.path = QPainterPath()
            self.path_proxy = self.addPath(path, self.strokes_pen)

            ### move path to current point and store such point as last one

            path.moveTo(point)
            self.last_point = point

            ### store 2-tuple of coordinates in new list within STROKES
            STROKES.append([point.toTuple()])

            ### store path proxy
            STROKE_PATH_PROXIES.append(self.path_proxy)

            ### then leave
            return

        ### if the points are too close, leave as well

        if (last_point - point).manhattanLength() <= 3:
            return


        ### otherwise, draw a line on our path and update its QGraphics proxy

        self.path.lineTo(point)
        self.path_proxy.setPath(self.path)

        ### append 2-tuple of coordinates in last stroke in the list
        STROKES[-1].append(point.toTuple())

        ### reference current point as last one
        self.last_point = point

    def mouseReleaseEvent(self, event):
        """Set last_point to None."""
        self.last_point = None

    def keyReleaseEvent(self, event):
        """Process strokes if shift key is released while watching out for it.

        We watch out for shift key's release when we are drawing.
        """

        if (
            event.key() == Qt.Key.Key_Shift
            and self.watch_out_for_shift_release
        ):

            self.watch_out_for_shift_release = False
            self.process_strokes()

    def process_strokes(self):
        """Process drawing (its strokes) to turn it into a widget."""

        ### remove path proxies (proxies added when drawing)

        for item in STROKE_PATH_PROXIES:
            self.removeItem(item)

        STROKE_PATH_PROXIES.clear()

        del self.path, self.path_proxy

        ### only proceed if all strokes have at least 2 points

        if any(len(stroke) < 2 for stroke in STROKES):

            ## otherwise we clear the strokes and leave the method
            ## earlier

            STROKES.clear()
            return

        ### check list of strokes for matches
        match_data = get_stroke_matches_data(STROKES)

        ### clear strokes
        STROKES.clear()

        ### act according to whether menu items and/or a chosen
        ### widget was given

        menu_items = match_data['menu_items']
        chosen_widget_key = match_data['chosen_widget_key']

        ## if neither was given, simply display the report on the status
        ## bar and leave method

        if not menu_items and not chosen_widget_key:

            self.show_message_on_status_bar(match_data['report'], 2500)
            return

        ## if menu items were given, it means we must present such menu
        ## for the user to pick one of the items; we then process the
        ## choice

        elif menu_items:
            
            ## create and populate the mneu

            menu = QMenu(self.main_window)

            action_to_key = {}

            for index, (_, widget_key) in enumerate(menu_items):

                ac = menu.addAction(f"{widget_key}")

                if index == 0:
                    first_action = ac

                action_to_key[ac] = widget_key

            ## set timer to position cursor in a very short instant
            ## (so it appears right on top of the first menu's item

            cursor_pos = REFS.cursor.pos()

            menu_pos = cursor_pos + self.menu_offset
            new_cursor_pos = cursor_pos + self.cursor_offset

            QTimer.singleShot(1, partial(REFS.cursor.setPos, new_cursor_pos))

            ## display menu, executing its loop and process user's choice
            chosen_action = menu.exec(menu_pos, first_action)

            ## if user didn't pick any choice, display report on status bar
            ## and leave method

            if chosen_action is None:

                report = "No widget was chosen"
                self.show_message_on_status_bar(report, 2500)
                return

            ## otherwise reference widget's key according to choice

            else:
                chosen_widget_key = action_to_key[chosen_action]

        ## if menu items weren't given but a widget was already chosen
        ## based on the processed strokes, we just need to report stats
        ## from the processed strokes on the status bar

        elif chosen_widget_key:

            rounded_hd = round(match_data['sym_hausdorff_dist'])
            no_of_widgets = match_data['no_of_widgets']

            report = (
                f"Chose {chosen_widget_key}"
                f" (hausdorff of drawing = ~{rounded_hd})"
                f" among {no_of_widgets} widgets."
            )

            self.show_message_on_status_bar(report, 2500)

        ### reaching this point in the method means we already have
        ### a widget to create, either chosen by the user in the
        ### menu or automatically based on the strokes
        ###
        ### now we just need to create such widget

        ## calculate position for widget

        left, top, right, bottom = match_data['union_bounding_box']

        width = right - left
        height = bottom - top

        x = left + width/2
        y = top + height/2

        ## calculate size for widget
        size = (width, height)

        ## reference the widget class to use

        if chosen_widget_key == 'label':
            item_class = LabelItem

        elif chosen_widget_key == 'unchecked_check_box':
            item_class = UncheckedCheckBoxItem 

        elif chosen_widget_key == 'checked_check_box':
            item_class = CheckedCheckBoxItem

        elif chosen_widget_key == 'line_edit':
            item_class = LineEditItem

        elif chosen_widget_key == 'button':
            item_class = ButtonItem


        ## finally instantiate, add and position widget

        item = item_class(size)

        self.addItem(item)

        x, y = item.get_adjusted_pos(x, y, width, height)
        item.setPos(x, y)
