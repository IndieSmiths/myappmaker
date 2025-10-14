"""Facility for dialog to record drawings (strokes)."""

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
    get_line_edit,
    get_button,
)

from .recordingpanel import StrokesRecordingPanel

from .displaypanel import StrokesDisplayPanel



### dialog definition

class StrokeRecordingDialog(QDialog):
    """Dialog with widgets to assist in recording drawings (strokes)."""

    def __init__(self, parent=None):
        """Initialize superclass and build contents."""

        ### initialize superclass
        super().__init__(parent)

        ### set title for dialog's window
        self.setWindowTitle('Stroke settings')

        ### create a grid layout to use like a table
        grid = self.grid = QGridLayout()

        ### define labels representing captions for our grid-table
        ### and add them

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

        ### instantiate and add a recording panel for recording drawings
        ### (strokes) performed by the user

        self.recording_panel = StrokesRecordingPanel(self)
        grid.addWidget(self.recording_panel, 3, 1)

        ### create and populate a combobox and related stacks holding
        ### info/widgets related to specific widgets

        ## combobox

        widget_key_box = self.widget_key_box = QComboBox()
        widget_key_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        ## stacks

        widget_stack = self.widget_stack = QStackedLayout()
        strokes_display_stack = self.strokes_display_stack = QStackedLayout()

        ## populate

        for widget_key, get_widget in (

            ('label', get_label),
            ('unchecked_check_box', get_unchecked_check_box),
            ('checked_check_box', get_checked_check_box),
            ('line_edit', get_line_edit),
            ('button', get_button),

        ):

            widget_key_box.addItem(widget_key)
            widget_stack.addWidget(get_widget())
            strokes_display_stack.addWidget(StrokesDisplayPanel(widget_key))

        ### add the combobox and stacks to the grid

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

        ### set grid as the layout for this dialog
        self.setLayout(self.grid)

        ### perform extra setups on the combobox and stacks

        widget_key_box.setCurrentText('label')
        widget_key_box.setEditable(False)
        widget_key_box.currentTextChanged.connect(self.prepare_for_edition)

        self.prepare_for_edition()

    def prepare_for_edition(self):
        """Perform setups so relevant info and behaviour is ready."""

        ### grab index of current value set on combobox
        index = self.widget_key_box.currentIndex()

        ### use it to update displayed widget on stacks

        self.widget_stack.setCurrentIndex(index)
        self.strokes_display_stack.setCurrentIndex(index)

        ### pass a reference of the display panel to the recording panel

        self.recording_panel.reference_display_panel(
            self.strokes_display_stack.currentWidget()
        )
