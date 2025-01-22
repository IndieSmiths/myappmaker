"""Facility with canvas to add and organize widgets."""

### third-party imports

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem

from PySide6.QtGui import QBrush, QPen, QPixmap, QPainter

from PySide6.QtCore import Qt



### constant
SIZE = (1280, 720)



### class definition

class CanvasScene(QGraphicsScene):

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
        pen.setWidth(3)

        ###
        self.last_point = None

    def mouseMoveEvent(self, event):

        ### leave right away if left button is NOT pressed

        if not (event.buttons() & Qt.LeftButton):
            return

        ### grab/reference points locally

        point = event.scenePos()
        last_point = self.last_point

        ### if there's no last point, store current point as last
        ### one and leave right away

        if last_point is None:

            self.last_point = point
            return

        ### if the points are too close, leave as well
        if (last_point - point).manhattanLength() <= 3:
            return


        ### otherwise, draw a line on our board and update its
        ### QGraphics proxy

        painter = QPainter(self.board)

        painter.setPen(self.board_pen)
        painter.drawLine(self.last_point, point)

        painter.end()

        self.last_point = point

        self.board_proxy.setPixmap(self.board)

    def mouseReleaseEvent(self, event):
        self.last_point = None
