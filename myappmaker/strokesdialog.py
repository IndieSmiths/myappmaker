
### third-party imports

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QWidget,
    QLabel,
    QCheckBox,
)

from PySide6.QtGui import QPixmap

from PySide6.QtCore import Qt, QSize


### local import
from .config import STROKES_DATA_DIR



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

        cbox = QCheckBox()
        cbox.setCheckState(Qt.CheckState.Unchecked)

        grid.addWidget(cbox, 1, 0)
        grid.addWidget(StrokesDisplay(unmarked_checkbutton_strokes_dir), 1, 1)

        ### marked checkbutton

        marked_checkbutton_strokes_dir = (
            STROKES_DATA_DIR / 'marked_checkbutton_strokes_dir'
        )

        cbox = QCheckBox()
        cbox.setCheckState(Qt.CheckState.Checked)

        grid.addWidget(cbox, 2, 0)
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

        self.label = QLabel(self)
        pmap = QPixmap(STROKE_SIZE)
        self.label.setPixmap(pmap)

    def init_strokes_display(self, stroke_array_paths):
        n = len(stroke_array_paths)
