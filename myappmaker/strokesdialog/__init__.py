
### standard library imports

from functools import partial

from shutil import rmtree


### third-party imports

## PySide6

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QCheckBox,
    QPushButton,
)

from PySide6.QtSvgWidgets import QSvgWidget

from PySide6.QtCore import Qt, QByteArray, QPointF

from PySide6.QtGui import QPainter, QPixmap, QPen

## numpy
from numpy import array as numpy_array


### local imports

from ..config import STROKES_DATA_DIR

from ..ourstdlibs.pyl import load_pyl, save_pyl

from .strokesrecordingdialog import StrokesRecordingDialog

from .getnotfoundsvg import get_not_found_icon_svg_text

from .constants import STROKE_SIZE, STROKE_DIMENSION, STROKE_HALF_DIMENSION




### unmarked checkbox

def get_check_box(checked=True):

    check_box = QCheckBox()
    check_box.setCheckState(
        getattr(
            Qt.CheckState,
            'Checked' if checked else 'Unchecked',
        )
    )
    check_box.setEnabled(False)

    return check_box

get_checked_check_box = partial(get_check_box, True)
get_unchecked_check_box = partial(get_check_box, False)

### stroke manager

class StrokesManager:

    def __init__(self):
        ...


### dialog definition

class StrokeSettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Stroke settings')

        self.recording_dlg = StrokesRecordingDialog(self)

        ###
        self.stroke_display_map = {}

        ###

        grid = self.grid = QGridLayout()

        ### define captions

        for col, label_text in enumerate(

            (
                "Widget name",
                "Strokes",
                "Set/reset",
            )

        ):

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            grid.addWidget(label, 0, col)

        ### define contents

        for row, (widget_key, get_widget) in enumerate(

            (
                ('label', partial(QLabel, 'A label')),
                ('unchecked_check_box', get_unchecked_check_box),
                ('checked_check_box', get_checked_check_box),
            ),

            start=1,

        ):

            button = QPushButton("Set/reset strokes")

            button.clicked.connect(
                partial(self.reset_stroke, widget_key)
            )

            grid.addWidget(get_widget(), row, 0)

            stroke_display = StrokesDisplay(widget_key)
            self.stroke_display_map[widget_key] = stroke_display
            grid.addWidget(stroke_display, row, 1)

            grid.addWidget(button, row, 2)

        ###
        self.setLayout(self.grid)

    def reset_stroke(self, widget_key):

        self.recording_dlg.prepare_session(
            self.stroke_display_map[widget_key]
        )

        self.recording_dlg.exec()


### strokes display widget definition

NOT_FOUND_SVG_BYTE_ARRAY = (

    QByteArray(
        get_not_found_icon_svg_text(STROKE_SIZE)
    )

)

STROKE_PEN = QPen()
STROKE_PEN.setWidth(2)
STROKE_PEN.setColor(Qt.red)

class StrokesDisplay(QWidget):

    def __init__(self, widget_key):

        super().__init__()

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

        layout = QHBoxLayout()
        svg_widget = QSvgWidget()

        svg_widget.load((NOT_FOUND_SVG_BYTE_ARRAY))
        svg_widget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)

        layout.addWidget(svg_widget)
        self.setLayout(layout)

    def init_strokes_display(self, stroke_paths):

        strokes = list(map(load_pyl, stroke_paths))
        self.stroke_arrays = list(map(numpy_array, strokes))

        self.label.setPixmap(self.get_new_pixmap(strokes))

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_and_save_strokes(self, strokes):

        strokes_dir = self.strokes_dir

        if strokes_dir.exists():
            rmtree(str(strokes_dir))

        strokes_dir.mkdir()

        for index, points in enumerate(strokes):

            save_pyl(
                points,
                (strokes_dir / f'stroke_{index:>02}.pyl'),
            )

        self.stroke_arrays = list(map(numpy_array, strokes))

        self.label.setPixmap(self.get_new_pixmap(strokes))

    def get_new_pixmap(self, strokes):

        n = len(strokes)
        width = n * STROKE_DIMENSION
        height = STROKE_DIMENSION

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setPen(STROKE_PEN)

        x_increment = -STROKE_HALF_DIMENSION
        y_increment = 150

        for points in strokes:

            x_increment += STROKE_DIMENSION

            painter.drawPolyline(

                [

                    QPointF(
                        a+x_increment,
                        b+y_increment,
                    )

                    for a, b in points

                ]

            )

        painter.end()

        return pixmap
