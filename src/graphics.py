from PySide2 import QtGui, QtCore, QtWidgets
import functools
from .globals import *


class boxItem(QtWidgets.QGraphicsItem):
    def __init__(self, position, scene, style=QtCore.Qt.SolidLine,
                 rect=None, matrix=QtGui.QMatrix()):
        super(boxItem, self).__init__()
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsFocusable |
                      QtWidgets.QGraphicsItem.ItemSendsGeometryChanges |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        if rect is None:
            rect = QtCore.QRectF(-10 * POINT_SIZE, -POINT_SIZE,
                                 20 * POINT_SIZE, 2 * POINT_SIZE)
        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setMatrix(matrix)
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()
        global RAW
        RAW = True

    def parentWidget(self):
        return self.scene().views()[0]

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setColor(QtCore.Qt.black)
        pen.setWidth(1)
        if option.state & QtWidgets.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        painter.drawRect(self.rect)

    def itemChange(self, change, variant):
        if change != QtWidgets.QGraphicsItem.ItemSelectedChange:
            global RAW
            RAW = True
        return QtWidgets.QGraphicsItem.itemChange(self, change, variant)

    def contextMenuEvent(self, event):
        wrapped = []
        menu = QtWidgets.QMenu(self.parentWidget())
        for text, param in (("&Solid", QtCore.Qt.SolidLine),
                            ("&Dashed", QtCore.Qt.DashLine),
                            ("D&otted", QtCore.Qt.DotLine),
                            ("D&ashDotted", QtCore.Qt.DashDotLine),
                            ("DashDo&tDotten", QtCore.Qt.DashDotDotLine)):
            wrapper = functools.partial(self.setStyle, param)
            wrapped.append(wrapper)
            menu.addAction(text, wrapper)
        menu.exec_(event.screenPos())


    def setStyle(self, style):
        self.style = style
        self.update()
        global RAW
        RAW = True

    def keyPressEvent(self, event):
        factor = POINT_SIZE / 4
        changed = False
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            if event.key() == QtCore.Qt.Key_Left:
                self.rect.setRight(self.rect.right() - factor)
                changed = True
            elif event.key() == QtCore.Qt.Key_Right:
                self.rect.setRight(self.rect.right() + factor)
                changed = True
            elif event.key() == QtCore.Qt.Key_Up:
                self.rect.setBottom(self.rect.bottom() - factor)
                changed = True
            elif event.key() == QtCore.Qt.Key_Down:
                self.rect.setBottom(self.rect.bottom() + factor)
                changed = True
        if changed:
            self.update()
            global RAW
            RAW = True
        else:
            QtWidgets.QGraphicsItem.keyPressEvent(self, event)


    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            super(boxItem, self).mouseMoveEvent(event)
        elif event.buttons & QtCore.Qt.MiddleButton:
            itemPos = self.pos()
            rect = QtCore.QRectF(itemPos, event.pos()).normalized()
            self.rect.setRect(rect)


class pixmapItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self):
        pass


class graphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(graphicsView, self).__init__(parent)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)

    def wheelEvent(self, event):
        factor = 1.41 ** (-event.delta() / 240)
        self.scale(factor, factor)
