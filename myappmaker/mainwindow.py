"""Facility for main window."""

### third-party imports

from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar,
    QGraphicsView,
)

from PySide6.QtGui import QAction, QKeySequence, QShortcut, QPainter

from PySide6.QtCore import Qt


### local imports

from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME

from .canvasscene import CanvasScene

from .strokesmgmt.recordingdialog import StrokeRecordingDialog

from .prefsmgmt import PreferencesDialog



class MainWindow(QMainWindow):
    """Main window for the application."""

    def __init__(self, app):
        """Setup window and its widgets."""

        ### initialize superclass
        super().__init__()

        ### set window's title
        self.setWindowTitle(APP_TITLE)

        ### create keyboard shortcut to exit app (escape key); this is used to
        ### speed up iterations during development and debugging; it will likely
        ### be removed/turned off in stable releases, as it can cause the user
        ### to accidentaly close the app

        qs = self.quit_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        qs.activated.connect(app.quit, Qt.QueuedConnection)

        ### instantiate status bar

        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        ### instantite and setup QGraphicsScene subclass and corresponding
        ### QGraphicsView

        scene = self.scene = CanvasScene(self, status_bar.showMessage)
        view = self.view = QGraphicsView(scene)

        view.setRenderHint(QPainter.Antialiasing)
        view.setOptimizationFlag(
            QGraphicsView.OptimizationFlag.DontSavePainterState
        )

        self.setCentralWidget(view)

        ### instantiate and store dialogs

        self.stroke_recording_dlg = StrokeRecordingDialog(self)
        self.preferences_dlg = PreferencesDialog(self)

        ### instantiate and setup toolbar

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
