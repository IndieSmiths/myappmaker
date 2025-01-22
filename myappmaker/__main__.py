"""Facility for launching the application - myappmaker.

Myappmaker: visual desktop app builder with features for both non-technical
and technical users, including block coding and many more.
"""

### standard library import
import sys


### third-party imports
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView


### local import
from .canvasscene import CanvasScene



class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('MyAppMaker')
        scene = self.scene = CanvasScene()
        view = self.view = QGraphicsView(scene)
        self.setCentralWidget(view)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
