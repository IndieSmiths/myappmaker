"""Facility for main window."""

### third-party imports

from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar,
    QGraphicsView,
)

from PySide6.QtGui import QAction, QKeySequence, QShortcut

from PySide6.QtCore import Qt


### local imports

from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME

from .canvasscene import CanvasScene

from .strokesmgmt.recordingdialog import StrokeRecordingDialog

from .prefsmgmt import PreferencesDialog



class MainWindow(QMainWindow):

    def __init__(self, app):

        super().__init__()

        self.setWindowTitle(APP_TITLE)

        ###

        qs = self.quit_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        qs.activated.connect(app.quit, Qt.QueuedConnection)

        ###
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        ###

        ###

        scene = self.scene = CanvasScene(self, status_bar.showMessage)
        view = self.view = QGraphicsView(scene)

        self.setCentralWidget(view)

        ###
        self.stroke_recording_dlg = StrokeRecordingDialog(self)
        self.preferences_dlg = PreferencesDialog(self)

        ###

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        for text, operation in (
            ("Preferences", self.preferences_dlg.exec),
            ("(Re)define strokes", self.stroke_recording_dlg.exec),
            ("Clear canvas", self.scene.clear),
        ):

            btn = QAction(text, self)
            btn.triggered.connect(operation)
            toolbar.addAction(btn)
