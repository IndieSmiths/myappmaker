

### third-party imports

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QCheckBox,
)

from PySide6.QtSvgWidgets import QSvgWidget

from PySide6.QtCore import Qt, QSize, QByteArray


### local import

from ..config import STROKES_DATA_DIR

from .getnotfoundsvg import get_not_found_icon_svg_text



### constant
STROKE_SIZE = QSize(300, 300)


### dialog definition

class StrokeSettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        grid = self.grid = QGridLayout()

        ### label

        label_strokes_dir = STROKES_DATA_DIR / 'label_strokes_dir'

        grid.addWidget(QLabel('Label'), 0, 0)
        grid.addWidget(StrokesDisplay(label_strokes_dir), 0, 1)

        ### unmarked checkbutton

        unmarked_checkbutton_strokes_dir = (
            STROKES_DATA_DIR / 'unmarked_checkbutton_strokes_dir'
        )

        unchecked_checkbox = QCheckBox()
        unchecked_checkbox.setCheckState(Qt.CheckState.Unchecked)

        grid.addWidget(unchecked_checkbox, 1, 0)
        grid.addWidget(StrokesDisplay(unmarked_checkbutton_strokes_dir), 1, 1)

        ### marked checkbutton

        marked_checkbutton_strokes_dir = (
            STROKES_DATA_DIR / 'marked_checkbutton_strokes_dir'
        )

        checked_checkbox = QCheckBox()
        checked_checkbox.setCheckState(Qt.CheckState.Checked)

        grid.addWidget(checked_checkbox, 2, 0)
        grid.addWidget(StrokesDisplay(marked_checkbutton_strokes_dir), 2, 1)

        ###
        self.setLayout(self.grid)


### strokes display widget definition


class StrokesDisplay(QWidget):

    def __init__(self, strokes_dir):

        super().__init__()

        self.strokes_dir = strokes_dir

        if strokes_dir.exists():

            npys = sorted(str(path) for path in strokes_dir.glob('*.npy'))

            if npys:
                self.init_strokes_display(npys)

            else:
                self.init_empty_display()

        else:
            self.init_empty_display()

    def init_empty_display(self):

        layout = QHBoxLayout()
        svg_widget = QSvgWidget()

        svg_widget.load(

            QByteArray(

                get_not_found_icon_svg_text(
                    STROKE_SIZE.toTuple()
                )

            )

        )

        layout.addWidget(svg_widget)
        self.setLayout(layout)

    def init_strokes_display(self, stroke_array_paths):
        n = len(stroke_array_paths)
