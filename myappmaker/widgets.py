
### standard library imports

from functools import partial

from random import randint

from collections import deque


### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QLabel,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsRectItem,
    QGraphicsLineItem,
    QGraphicsSimpleTextItem,

    QSizePolicy,

)

from PySide6.QtCore import Qt, QPointF, QLineF, QRectF, QMarginsF

from PySide6.QtGui import QPainterPath, QPen, QBrush, QColorConstants, QFont



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

def get_line_edit():
    line_edit = QLineEdit('A line edit')
    line_edit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    return line_edit

def get_button():
    button = QPushButton('A button')
    button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    return button

### custom items representing widgets


class LabelItem(QGraphicsSimpleTextItem):
    
    fonts = {}

    def __init__(self, size=(30, 30)):

        super().__init__()
        self.pick_font(size)

        super().setText('A label')

    def pick_font(self, size):

        height = size[1]
        height *= .7
        height = round(height)

        if height not in self.fonts:

            f = QFont()
            f.setStyleHint(QFont.StyleHint.Cursive)
            f.setPointSize(height)
            self.fonts[height] = f

        super().setFont(self.fonts[height])

    @staticmethod
    def adjust_pos(x, y, width, height):
        return (x - (width * .5), y - (height * .7))


random_offset = (
    lambda delta: QPointF(*(randint(-delta, delta) for _ in range(2)))
)

class CheckBoxItem(QGraphicsItem):

    def __init__(self, checked=False, size=(0, 0)):

        super().__init__()

        self.paint = self.draw_checked if checked else self.draw_unchecked

        self.create_drawing_paths(size)

        box_pen = self.box_pen = QPen()
        box_pen.setStyle(Qt.SolidLine)
        box_pen.setColor(QColorConstants.Svg.black)
        box_pen.setWidth(4)

        tick_pen = self.tick_pen = QPen()
        tick_pen.setStyle(Qt.SolidLine)
        tick_pen.setColor(QColorConstants.Svg.blue)
        tick_pen.setWidth(10)

    def create_drawing_paths(self, size):
        
        width = height = size[0]

        box_area = QRectF(0, 0, width, height)

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

        width *= 1.2
        width = int(width)

        height *= 1.4
        height = int(height)

        tick_area = QRectF(0, 0, width, height)

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

    @staticmethod
    def adjust_pos(x, y, width, height):
        return (x - width/2, y - height/2)


UncheckedCheckBoxItem = partial(CheckBoxItem, False)
CheckedCheckBoxItem = partial(CheckBoxItem, True)


class LineEditItem(QGraphicsItemGroup):

    fonts = {}

    def __init__(self, size=(80, 30)):

        super().__init__()

        self.text_item = QGraphicsSimpleTextItem()
        self.pick_font(tuple(i - 5 for i in size))
        self.text_item.setText('A line edit')

        self.addToGroup(self.text_item)

        width, height = self.text_item.boundingRect().size().toTuple()

        ###

        outline_pen = QPen()
        outline_pen.setStyle(Qt.SolidLine)
        outline_pen.setColor(QColorConstants.Svg.black)
        outline_pen.setWidth(4)

        self.outline_rect = QGraphicsRectItem(0, 0, width+20, height+10)
        self.outline_rect.setPen(outline_pen)
        self.outline_rect.setBrush(Qt.NoBrush)

        self.addToGroup(self.outline_rect)

        self.text_item.setPos(10, 5)

    def pick_font(self, size):

        height = size[1]
        height *= .4
        height = round(height)

        if height not in self.fonts:

            f = QFont()
            f.setStyleHint(QFont.StyleHint.Cursive)
            f.setPointSize(height)
            self.fonts[height] = f

        self.text_item.setFont(self.fonts[height])

    @staticmethod
    def adjust_pos(x, y, width, height):
        return (x - (width * .5), y - (height * .7))


class ButtonItem(QGraphicsItemGroup):

    fonts = {}

    def __init__(self, size=(80, 30)):

        super().__init__()

        self.text_item = QGraphicsSimpleTextItem()
        self.pick_font(tuple(i - 5 for i in size))
        self.text_item.setText('A button')

        width, height = self.text_item.boundingRect().size().toTuple()

        ###

        background_brush = QBrush()
        background_brush.setStyle(Qt.SolidPattern)
        background_brush.setColor(QColorConstants.Svg.silver)

        self.outline_rect_item = QGraphicsRectItem(0, 0, width+20, height+10)
        self.outline_rect_item.setPen(Qt.NoPen)
        self.outline_rect_item.setBrush(background_brush)

        self.addToGroup(self.outline_rect_item)

        ###

        in_pen = QPen()
        in_pen.setStyle(Qt.SolidLine)
        in_pen.setColor(QColorConstants.Svg.lightgrey)
        in_pen.setWidth(4)

        out_pen = QPen()
        out_pen.setStyle(Qt.SolidLine)
        out_pen.setColor(QColorConstants.Svg.darkgrey)
        out_pen.setWidth(4)

        out_rect = self.outline_rect_item.rect()

        p1 = out_rect.bottomLeft()
        p3 = out_rect.topRight()

        for attr_name, pen in (
            ('bottomRight', out_pen),
            ('topLeft', in_pen),
        ):

            p2 = getattr(out_rect, attr_name)()

            for p in (p1, p3):

                lineitem = QGraphicsLineItem(QLineF(p, p2))
                lineitem.setPen(pen)
                self.addToGroup(lineitem)

        ###

        self.addToGroup(self.text_item)
        self.text_item.setPos(10, 5)

    def pick_font(self, size):

        height = size[1]
        height *= .4
        height = round(height)

        if height not in self.fonts:

            f = QFont()
            f.setStyleHint(QFont.StyleHint.Cursive)
            f.setPointSize(height)
            self.fonts[height] = f

        self.text_item.setFont(self.fonts[height])

    @staticmethod
    def adjust_pos(x, y, width, height):
        return (x - (width * .5), y - (height * .7))
