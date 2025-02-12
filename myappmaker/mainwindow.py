"""Facility for main window."""



### third-party imports

from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QGraphicsView,
)

from PySide6.QtGui import QAction

from PySide6.QtCore import Qt


### local imports

from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME

from .canvasscene import CanvasScene

from .strokesmgr import StrokeSettingsDialog




class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(APP_TITLE)

        scene = self.scene = CanvasScene()
        view = self.view = QGraphicsView(scene)

        self.setCentralWidget(view)

        ###

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction("Stroke settings", self)
        button_action.triggered.connect(self.showStrokeSettingsDialog)
        toolbar.addAction(button_action)

        ###
        self.stroke_settings_dlg = StrokeSettingsDialog(self)

    def showStrokeSettingsDialog(self, s):
        self.stroke_settings_dlg.exec()

