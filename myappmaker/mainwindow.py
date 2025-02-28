"""Facility for main window."""

### third-party imports

from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar,
    QGraphicsView,
)

from PySide6.QtGui import QAction

from PySide6.QtCore import Qt


### local imports

from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME

from .canvasscene import CanvasScene

from .strokesmgmt.settingsdialog import StrokeSettingsDialog



class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(APP_TITLE)

        ###
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        ###

        scene = self.scene = CanvasScene(status_bar.showMessage)
        view = self.view = QGraphicsView(scene)

        self.setCentralWidget(view)

        ###
        self.stroke_settings_dlg = StrokeSettingsDialog(self)

        ###

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        for text, operation in (
            ("Stroke settings", self.stroke_settings_dlg.exec),
            ("Clear canvas", self.scene.clear),
        ):

            btn = QAction(text, self)
            btn.triggered.connect(operation)
            toolbar.addAction(btn)
