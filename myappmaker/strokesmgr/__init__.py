
### standard library import
from functools import partial


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QDialog,

    QGridLayout,
    QStackedLayout,

    QWidget,
    QComboBox,
    QLabel,
    QCheckBox,
    QPushButton,

    QSizePolicy,

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

        grid = self.grid = QGridLayout()

        ### define captions

        for row, label_text in enumerate(

            (
                "Pick widget:",
                "Widget:",
                "Strokes:",
            )

        ):

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            grid.addWidget(label, row, 0)

        ###

        button = QPushButton("Set/reset strokes")
        button.clicked.connect(self.reset_stroke)
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        grid.addWidget(button, 3, 1)

        ### populate:
        ###
        ### - combobox with widget keys
        ### - widget stack
        ### - strokes display stack

        widget_key_box = self.widget_key_box = QComboBox()
        widget_key_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        widget_stack = self.widget_stack = QStackedLayout()
        strokes_display_stack = self.strokes_display_stack = QStackedLayout()

        for widget_key, get_widget in (

            ('label', partial(QLabel, 'A label')),
            ('unchecked_check_box', get_unchecked_check_box),
            ('checked_check_box', get_checked_check_box),

        ):

            widget_key_box.addItem(widget_key)
            widget_stack.addWidget(get_widget())
            strokes_display_stack.addWidget(StrokesDisplay(widget_key))

        ###

        grid.addWidget(widget_key_box, 0, 1)

        widgets_holder = QWidget()
        widgets_holder.setLayout(widget_stack)
        grid.addWidget(widgets_holder, 1, 1)

        strokes_displays_holder = QWidget()
        strokes_displays_holder.setLayout(strokes_display_stack)
        grid.addWidget(strokes_displays_holder, 2, 1)

        ###
        self.setLayout(self.grid)

        ###

        widget_key_box.setCurrentText('label')
        widget_key_box.setEditable(False)
        widget_key_box.currentTextChanged.connect(self.update_stacks)
        self.update_stacks()

    def update_stacks(self):

        widget_key = self.widget_key_box.currentText()
        index = self.widget_key_box.currentIndex()

        self.widget_stack.setCurrentIndex(index)
        self.strokes_display_stack.setCurrentIndex(index)

    def reset_stroke(self):

        widget_key = self.widget_key_box.currentText()

        self.recording_dlg.prepare_session(
            self.strokes_display_stack.currentWidget()
        )

        self.recording_dlg.exec()
