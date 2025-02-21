
### standard library import
from functools import partial


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QLabel,
    QCheckBox,

    QSizePolicy,

)

from PySide6.QtCore import Qt




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

