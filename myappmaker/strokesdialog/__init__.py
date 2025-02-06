
### standard library import
from functools import partial

### third-party imports

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

from PySide6.QtCore import Qt, QSize, QByteArray


### local import

from ..config import STROKES_DATA_DIR

from .getnotfoundsvg import get_not_found_icon_svg_text



### constant
STROKE_SIZE = QSize(300, 300)

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
            grid.addWidget(StrokesDisplay(widget_key), row, 1)
            grid.addWidget(button, row, 2)

        ###
        self.setLayout(self.grid)

    def reset_stroke(self, widget_key):
        print(widget_key)


### strokes display widget definition

NOT_FOUND_SVG_BYTE_ARRAY = (

    QByteArray(
        get_not_found_icon_svg_text(
            STROKE_SIZE.toTuple()
        )
    )

)


class StrokesDisplay(QWidget):

    def __init__(self, widget_key):

        super().__init__()

        self.strokes_dir = strokes_dir = (
            STROKES_DATA_DIR / f'{widget_key}_strokes_dir'
        )

        if strokes_dir.exists():

            npys = (
                sorted(
                    str(path)
                    for path in strokes_dir.glob('*.npy')
                )
            )

            if npys:
                self.init_strokes_display(npys)

            else:
                self.init_empty_display()

        else:
            self.init_empty_display()

    def init_empty_display(self):

        layout = QHBoxLayout()
        svg_widget = QSvgWidget()

        svg_widget.load((NOT_FOUND_SVG_BYTE_ARRAY))

        layout.addWidget(svg_widget)
        self.setLayout(layout)

    def init_strokes_display(self, stroke_array_paths):
        n = len(stroke_array_paths)
