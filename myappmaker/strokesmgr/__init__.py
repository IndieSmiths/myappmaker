
### standard library import
from functools import partial


### third-party imports

## PySide6

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QCheckBox,
    QPushButton,
)

from PySide6.QtCore import Qt


### local imports

from .strokesrecordingdialog import StrokesRecordingDialog

from .strokesdisplay import StrokesDisplay



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
                "Widget",
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
