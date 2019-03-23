from PySide2 import QtGui, QtCore, QtWidgets
import functools
from .globals import *


class Rectangle(QtWidgets.QGraphicsRectItem):
    def __init__(self, position, scene, style=QtCore.Qt.SolidLine,
                 rect=None, matrix=QtGui.QMatrix()):
        super(Rectangle, self).__init__()
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable
            | QtWidgets.QGraphicsItem.ItemIsMovable
            | QtWidgets.QGraphicsItem.ItemIsFocusable
            | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        if rect is None:
            rect = QtCore.QRectF(0, 0, 200, 200)

        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setMatrix(matrix)
        self.setRect(self.rect)

        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()
        global RAW
        RAW = True

    def itemChange(self, change, variant):
        if change != QtWidgets.QGraphicsRectItem.ItemSelectedChange:
            global RAW
            RAW = True
        return QtWidgets.QGraphicsRectItem.itemChange(self, change, variant)

    def parentWidget(self):
        return self.scene().views()[0]

    def mouseMoveEvent(self, event):
        if self.isSelected():
            if event.buttons() & QtCore.Qt.LeftButton:
                super(Rectangle, self).mouseMoveEvent(event)
            elif event.buttons() & QtCore.Qt.MiddleButton:
                self.rect = QtCore.QRectF(QtCore.QPoint(), event.pos()).normalized()
                self.prepareGeometryChange()
                self.setRect(self.rect)


    def contextMenuEvent(self, event):
        if self.isSelected():
            super(Rectangle, self).contextMenuEvent(event)
            delta = 10
            r = self.boundingRect()
            r.adjust(-delta, -delta, delta, delta)
            if not r.contains(event.pos()):
                return
            self.setSelected(True)
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


    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setColor(QtCore.Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(self.brush())
        if option.state & QtWidgets.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.blue)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.boundingRect())
        #print(self.rect())


    def setStyle(self, style):
        pen = self.pen()
        pen.setStyle(style)
        self.setPen(pen)
        self.style = style
        self.update()
        global RAW
        RAW = True



class pixmapItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self):
        pass


class graphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(graphicsView, self).__init__(parent)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)

    def wheelEvent(self, event):
        factor = 1.41 ** (-event.delta() / 240)
        self.scale(factor, factor)
        global RAW
        RAW = True


'''
    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setColor(QtCore.Qt.black)
        pen.setWidth(1)
        if option.state & QtWidgets.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        painter.drawRect(self.rect)
'''
