from PySide2 import QtGui, QtCore, QtWidgets
import functools
from .globals import *


class Rectangle(QtWidgets.QGraphicsRectItem):
    def __init__(self, position, scene, lineWidth, joinStyle,
                 lineStyle=QtCore.Qt.SolidLine, rect=None, matrix=QtGui.QMatrix()):
        super(Rectangle, self).__init__()
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable
            | QtWidgets.QGraphicsItem.ItemIsMovable
            | QtWidgets.QGraphicsItem.ItemIsFocusable
            | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        if rect is None:
            rect = QtCore.QRectF(0, 0, 200, 200)

        self.rect = rect
        self.style = lineStyle
        self.lineW = lineWidth
        self.join = joinStyle

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
        def clearList(list):
            length = len(list)
            del list[0:length]

        if self.isSelected():
            super(Rectangle, self).contextMenuEvent(event)

            delta = 10
            r = self.boundingRect()
            r.adjust(-delta, -delta, delta, delta)
            if not r.contains(event.pos()):
                return

            self.setSelected(True)
            menu = QtWidgets.QMenu(self.parentWidget())

            styleMenu = menu.addMenu("Change line style")
            for text, param in (("Solid", QtCore.Qt.SolidLine),
                                ("Dashed", QtCore.Qt.DashLine),
                                ("Dotted", QtCore.Qt.DotLine),
                                ("DashDotted", QtCore.Qt.DashDotLine),
                                ("DashDotDotten", QtCore.Qt.DashDotDotLine)):
                wrapper = functools.partial(self.setStyle, param)
                styleMenu.addAction(text, wrapper)
            menu.addSeparator()

            penMenu = menu.addMenu("Change line width")
            for text, param in (("1px", 1),
                                ("2px", 2),
                                ("3px", 3),
                                ("4px", 4),
                                ("5px", 5),):
                wrapper = functools.partial(self.setWidth, param)
                penMenu.addAction(text, wrapper)
            menu.addSeparator()

            joinMenu = menu.addMenu("Change line join style")
            for text, param in (("Bevel join", QtCore.Qt.BevelJoin),
                                ("Round join", QtCore.Qt.RoundJoin),
                                ("Miter join", QtCore.Qt.MiterJoin)):
                wrapper = functools.partial(self.setJoin, param)
                joinMenu.addAction(text, wrapper)

            menu.exec_(event.screenPos())


    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setColor(QtCore.Qt.black)
        pen.setWidth(self.lineW)
        pen.setJoinStyle(self.join)
        if self.join == QtCore.Qt.MiterJoin:
            limit = pen.width() / 2
            pen.setMiterLimit(limit)

        painter.setPen(pen)
        painter.setBrush(self.brush())

        if option.state & QtWidgets.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.blue)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)

        painter.drawRect(self.boundingRect())


    def setStyle(self, style):
        self.style = style
        self.update()
        global RAW
        RAW = True

    def setWidth(self, width):
        self.lineW = width
        self.update()
        global RAW
        RAW = True

    def setJoin(self, style):

        self.join = style
        self.update()
        global RAW
        RAW = True




class pixmapItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self):
        pass


class graphicsView(QtWidgets.QGraphicsView):

    def __init__(self, scene, parent=None):
        super(graphicsView, self).__init__(parent)
        self.scene = scene

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.setScene(self.scene)


    def wheelEvent(self, event):
        factor = 1.41 ** (-event.delta() / 240)
        self.scale(factor, factor)
        global RAW
        RAW = True


    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            super(graphicsView, self).mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if event.button() & QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        else:
            super(graphicsView, self).mouseReleaseEvent(event)





