"""Facility with canvas to add and organize widgets."""

### third-party imports

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem

from PySide6.QtGui import QBrush, QPen, QPainter, QPainterPath

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

        ### 

        pen = QPen(Qt.red)
        pen.setWidth(3)

        path = self.path = QPainterPath()
        self.path_proxy = self.addPath(path, pen)

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

            self.path.moveTo(point.x(), point.y())
            self.last_point = point
            return

        ### if the points are too close, leave as well
        if (last_point - point).manhattanLength() <= 3:
            return


        ### otherwise, draw a line on our board and update its
        ### QGraphics proxy

        self.path.lineTo(point.x(), point.y())
        self.path_proxy.setPath(self.path)

        self.last_point = point


    def mouseReleaseEvent(self, event):
        self.last_point = None
