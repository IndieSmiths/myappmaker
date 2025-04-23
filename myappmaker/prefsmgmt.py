"""Facility for managing preferences."""


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QDialog,
    QGridLayout,
    QLabel,
    QCheckBox,

)

from PySide6.QtCore import Qt



### dialog definition

class PreferencesDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Preferences')

        ###

        grid = self.grid = QGridLayout()

        ### define captions

        topright_alignment = (
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTop
        )

        for row, label_text in enumerate(

            (
                "Prompt user for widget after drawing",
            )

        ):
            grid.addWidget(QLabel(label_text), row, 0, topright_alignment)


        ###
        grid.addWidget(QCheckBox(), 0, 1, Qt.AlignmentFlag.AlignLeft)

        ###
        self.setLayout(self.grid)
