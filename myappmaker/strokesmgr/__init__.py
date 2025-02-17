
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

from .strokesrecordingpanel import StrokesRecordingPanel

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

def get_label():

    label = QLabel('A label')
    label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    return label

### dialog definition

class StrokeSettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Stroke settings')

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
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            grid.addWidget(label, row, 0)

        ###

        self.recording_panel = StrokesRecordingPanel(self)

        button = QPushButton("Show/hide editor")
        button.clicked.connect(self.toggle_recording_panel)
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        grid.addWidget(button, 3, 0)
        grid.addWidget(self.recording_panel, 3, 1)
        self.recording_panel.hide()

        ###

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

            ('label', get_label),
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

        self.recording_panel.prepare(
            self.strokes_display_stack.currentWidget()
        )

    def toggle_recording_panel(self):

        rpanel = self.recording_panel

        is_visible = rpanel.isVisible()

        if is_visible:
            rpanel.hide()

        else:

            rpanel.prepare(self.strokes_display_stack.currentWidget())
            rpanel.show()
