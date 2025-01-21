"""Facility for launching the application - myappmaker.

Myappmaker: visual desktop app builder with features for both non-technical
and technical users, including block coding and many more.
"""

### standard library import
import sys


### third-party imports

from PySide6.QtWidgets import (

    QGraphicsScene,
    QGraphicsView,
    QGraphicsRectItem,

    QApplication,
    QMainWindow,
)

from PySide6.QtGui import QBrush, QPen, QPixmap, QPainter

from PySide6.QtCore import Qt



SIZE = (1280, 720)


class Scene(QGraphicsScene):

    def __init__(self):

        super().__init__(0, 0, *SIZE)

        ### rect

        rect = QGraphicsRectItem(200, 200, 100, 100)

        brush = QBrush(Qt.blue)
        rect.setBrush(brush)

        pen = QPen(Qt.green)
        pen.setWidth(10)
        rect.setPen(pen)

        self.addItem(rect)

        ### transparent drawing board (pixmap)

        board = self.board = QPixmap(*SIZE)
        board.fill(Qt.transparent)

        self.board_proxy = self.addPixmap(board)

        ## its pen

        pen = self.board_pen = QPen(Qt.red)
        pen.setWidth(6)

        ###
        self.last_point = None

    def mouseMoveEvent(self, event):

        ### exit right away if left button is NOT pressed

        if not (event.buttons() & Qt.LeftButton):
            return

        point = event.scenePos()

        if self.last_point is None:

            self.last_point = point
            return

        painter = QPainter(self.board)

        painter.setPen(self.board_pen)
        painter.drawLine(self.last_point, point)

        painter.end()

        self.last_point = point

        self.board_proxy.setPixmap(self.board)

    def mouseReleaseEvent(self, event):
        self.last_point = None


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('MyAppMaker')
        scene = self.scene = Scene()
        view = self.view = QGraphicsView(scene)
        self.setCentralWidget(view)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
