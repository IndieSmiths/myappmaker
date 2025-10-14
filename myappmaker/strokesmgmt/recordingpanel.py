"""Facility with canvas (scene) to record strokes."""

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
    QMessageBox,
)

from PySide6.QtGui import QPen, QPainterPath

from PySide6.QtCore import Qt, QLine


### local imports

from .utils import get_stroke_matches_data

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
    """Scene used to record strokes drawn by user."""

    def __init__(self, recording_panel):
        """Initialize superclass and setup contents."""

        ### initialize superclass, defining a fixed size
        ### it (which helps with performance)
        super().__init__(0, 0, *STROKE_SIZE)

        ### store given reference to recording panel
        self.recording_panel = recording_panel

        ### fill scene with white
        self.setBackgroundBrush(Qt.white)

        ### define and add perpendicular dashed lines that
        ### cross at the middle of the scene, just so they
        ### can be used as drawing guides;
        ###
        ### we don't store references to those lines because
        ### we won't need to manipulate them anymore

        ## pen for dashed lines

        dash_pen = QPen()
        dash_pen.setWidth(2)
        dash_pen.setStyle(Qt.DashLine)
        dash_pen.setColor(LIGHT_GREY_QCOLOR)

        ## horizontal line

        horizontal_line = (

            QLine(
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
                STROKE_HALF_DIMENSION,
            )

        )

        self.addLine(horizontal_line, dash_pen)

        ## vertical line

        vertical_line = (

            QLine(
                STROKE_HALF_DIMENSION,
                0,
                STROKE_HALF_DIMENSION,
                STROKE_DIMENSION,
            )

        )

        self.addLine(vertical_line, dash_pen)

        ### define and store pen for strokes

        self.strokes_pen = QPen(Qt.red)
        self.strokes_pen.setWidth(3)

        ### create placeholder and flag attributes to assist in this
        ### widget's recording operations

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

        self.path.lineTo(point.x(), point.y())
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
        """Process drawing (its strokes) to associate it with widgets."""

        ### remove path proxies (proxies added when drawing)

        for item in STROKE_PATH_PROXIES:
            self.removeItem(item)

        STROKE_PATH_PROXIES.clear()

        del self.path, self.path_proxy

        ### offset strokes so they are centered on the origin (0, 0)

        offset_strokes = []

        while STROKES:

            points = STROKES.popleft()

            offset_points = [
                (a - STROKE_HALF_DIMENSION, b - STROKE_HALF_DIMENSION)
                for a, b in points
            ]

            offset_strokes.append(offset_points)

        ### abort saving strokes if it is already similar enough with an existing
        ### drawing

        ## using the strokes, try getting best match among existing drawing

        chosen_widget_key = (
            get_stroke_matches_data(
                offset_strokes,
                always_filter=True,
            )['chosen_widget_key']
        )

        ## if there's a matching widget and it isn't the current one,
        ## explain to the user that we can't use the drawing because another
        ## widget is already using it

        if (
            chosen_widget_key
            and chosen_widget_key != self.display_panel.widget_key
        ):

            QMessageBox.information(
                self.recording_panel,
                "Drawing already exists!",
                (
                    "The provided drawing can't be used for this widget."
                    f"It is already in use for the {chosen_widget_key} widget."
                ),
            )

        ### otherwise, the new drawing can be set without problems;
        ###
        ### note that this new strokes may still have matched the pre-existing
        ### strokes for this widget we are associating with the new strokes;
        ### there is no problem, as this case serves as a way for the user
        ### to update the drawing; of course, the user might stil be doing that
        ### inadvertently, but in the end it is harmless because the strokes
        ### will simply be replace by a set of strokes that also matches the
        ### original strokes used; in other words, it is practically the same
        ### drawing anyway

        else:
            self.display_panel.update_and_save_strokes(offset_strokes)



class StrokesRecordingPanel(QWidget):
    """Panel to hold the view and associated scene for recording strokes."""

    def __init__(self, parent=None):
        """Initialize superclass and setup contents."""

        ### initialize superclass
        super().__init__()

        ### instantiate and store custom scene and standard view,
        ### associating them

        scene = self.scene = StrokesRecordingScene(self)
        self.view = QGraphicsView(scene)

        ### create and setup layout for this widget, adding the
        ### view to it

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

    def reference_display_panel(self, display_panel):
        """Store a reference to the display panel in the scene."""
        self.scene.display_panel = display_panel
