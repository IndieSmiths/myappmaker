
### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QDialog,

    QGridLayout,
    QStackedLayout,

    QWidget,
    QComboBox,
    QLabel,

    QSizePolicy,

)

from PySide6.QtCore import Qt


### local imports

from ..widgets import (
    get_checked_check_box,
    get_unchecked_check_box,
    get_label,
)

from .recordingpanel import StrokesRecordingPanel

from .display import StrokesDisplay



### dialog definition

class StrokeSettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Stroke settings')

        ###

        grid = self.grid = QGridLayout()

        ### define captions

        topright_alignment = (
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTop
        )

        for row, label_text in enumerate(

            (
                "Pick widget:",
                "Widget:",
                "Strokes:",
                "(Re)set strokes:",
            )

        ):
            grid.addWidget(QLabel(label_text), row, 0, topright_alignment)

        ###

        self.recording_panel = StrokesRecordingPanel(self)
        grid.addWidget(self.recording_panel, 3, 1)

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

        topleft_alignment = (
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        grid.addWidget(widgets_holder, 1, 1, topleft_alignment)

        strokes_displays_holder = QWidget()
        strokes_displays_holder.setLayout(strokes_display_stack)
        grid.addWidget(strokes_displays_holder, 2, 1, topleft_alignment)

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
