
### standard library imports

from functools import partial

from random import randint

from collections import deque


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QLabel,
    QCheckBox,
    QGraphicsItem,
    QGraphicsSimpleTextItem,

    QSizePolicy,

)

from PySide6.QtCore import Qt, QPointF, QLineF, QRectF, QMarginsF

from PySide6.QtGui import QPainterPath, QPen, QColorConstants



### regular widgets

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


### custom items representing widgets


class LabelItem(QGraphicsSimpleTextItem):

    def __init__(self):

        super().__init__()
        super().setText('A label')


random_offset = (
    lambda delta: QPointF(*(randint(-delta, delta) for _ in range(2)))
)

class CheckBoxItem(QGraphicsItem):

    def __init__(self, checked=False):

        super().__init__()

        self.paint = self.draw_checked if checked else self.draw_unchecked

        self.create_drawing_paths()

        box_pen = self.box_pen = QPen()
        box_pen.setStyle(Qt.SolidLine)
        box_pen.setColor(QColorConstants.Svg.black)
        box_pen.setWidth(4)

        tick_pen = self.tick_pen = QPen()
        tick_pen.setStyle(Qt.SolidLine)
        tick_pen.setColor(QColorConstants.Svg.blue)
        tick_pen.setWidth(10)

    def create_drawing_paths(self):

        box_area = QRectF(0, 0, 50, 50)

        control_margin = 6
        control_area = (
            box_area.marginsAdded(QMarginsF(*((control_margin,) * 4)))
        )

        ### max change
        mc = 4

        box_path = self.box_path = QPainterPath()

        point_names = deque(('topLeft', 'topRight', 'bottomRight', 'bottomLeft'))

        for _ in range(4):

            point_name_a = point_names[0]
            point_names.rotate(-1)
            point_name_b = point_names[0]

            point_a = getattr(box_area, point_name_a)()
            point_b = getattr(box_area, point_name_b)()

            control_point = QLineF(
                getattr(control_area, point_name_a)(),
                getattr(control_area, point_name_b)(),
            ).pointAt(.5)

            box_path.moveTo(point_a + random_offset(mc))
            box_path.quadTo(control_point, point_b + random_offset(mc))

        box_path_br = box_path.boundingRect()

        ###

        mid_point = box_path_br.center() + random_offset(4)

        tick_area = QRectF(0, 0, 60, 80)
        tick_area.moveCenter(box_area.center())

        tick_path = self.tick_path = QPainterPath()

        start_point = (

            QLineF(
                mid_point,
                tick_area.topLeft(),
            ).pointAt(.5)

            + random_offset(4)

        )

        end_point = tick_area.topRight() + random_offset(4)

        tick_path.moveTo(start_point)
        tick_path.lineTo(mid_point)
        tick_path.lineTo(end_point)
        tick_path.translate(0, 5)

        tick_path_br = tick_path.boundingRect()

        bounding_rect = self.bounding_rect = (
            box_path_br
            .united(tick_path_br)
            .marginsAdded(
              QMarginsF(*((5,)*4))
            )
        )

        offset = bounding_rect.topLeft() - QPointF(0, 0)

        bounding_rect.translate(-offset)
        box_path.translate(-offset)
        tick_path.translate(-offset)

    def boundingRect(self):
        return self.bounding_rect

    def draw_unchecked(self, painter, option, widget):

        painter.setPen(self.box_pen)
        painter.drawPath(self.box_path)

    def draw_checked(self, painter, option, widget):

        painter.setPen(self.box_pen)
        painter.drawPath(self.box_path)
        painter.setPen(self.tick_pen)
        painter.drawPath(self.tick_path)


UncheckedCheckBoxItem = partial(CheckBoxItem, False)
CheckedCheckBoxItem = partial(CheckBoxItem, True)
