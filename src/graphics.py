import functools
from globals import PAGE_SIZE
from PySide2 import QtGui, QtCore, QtWidgets


class graphicsView(QtWidgets.QGraphicsView):
    currentItemChanged = QtCore.Signal(QtWidgets.QGraphicsItem)

    def __init__(self, scene, snap, parent=None):
        super(graphicsView, self).__init__(parent)
        self.scene = scene
        self.snap = snap  # TODO

        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
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
        super(graphicsView, self).mousePressEvent(event)
        if event.button() & QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        it = self.itemAt(event.pos())
        if it is not None and hasattr(it, "_canEdit"):
            self.currentItem = it

    def mouseReleaseEvent(self, event):
        super(graphicsView, self).mouseReleaseEvent(event)
        if event.button() & QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    @property
    def currentItem(self):
        if not hasattr(self, "_currentItem"):
            self._currentItem = None
        return self._currentItem

    @currentItem.setter
    def currentItem(self, it):
        if self.currentItem != it:
            self._currentItem = it
            self.currentItemChanged.emit(it)


class graphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(graphicsScene, self).__init__()
        self.gridDensity_X = 50
        self.gridDensity_Y = 50

        self.lines = []

        self.setSceneRect(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)

        self.state = True

    def snap(self):
        if self.state is True:
            gr = self.sceneRect().toRect()
            start_x = gr.left() + self.gridDensity_X - (gr.left() % self.gridDensity_X)
            start_y = gr.top() + self.gridDensity_Y - (gr.top() % self.gridDensity_Y)

            for item in self.items():
                item.a_state = True

            for x in range(start_x, gr.right(), self.gridDensity_X):
                line = self.addLine(x, gr.top(), x, gr.bottom())
                line.setOpacity(0.3)
                line.setZValue(-1)
                self.lines.append(line)

            for y in range(start_y, gr.bottom(), self.gridDensity_Y):
                line = self.addLine(gr.left(), y, gr.right(), y)
                line.setOpacity(0.3)
                line.setZValue(-1)
                self.lines.append(line)

            for item in self.items():
                item.update()

            self.state = False
        else:
            for item in self.items():
                item.a_state = False
                item.update()

            for line in self.lines:
                self.removeItem(line)
            del self.lines[:]

            self.state = True

    def setGridOpacity(self, value):
        for line in self.lines:
            line.setOpacity(value)


class boxItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, position, rotation, scale, lineWidth, joinStyle,
                 lineStyle=QtCore.Qt.SolidLine, rect=None, matrix=QtGui.QMatrix(), scene=None, snap=None):
        super(boxItem, self).__init__()

        self._canEdit = True

        self.p_scene = scene
        self.a_state = False
        if snap.isChecked():
            self.a_state = True

        self.setRotation(rotation)
        self.setScale(scale)

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

        self.br = self.boundingRect()
        self.setTransformOriginPoint(
            QtCore.QPointF(self.br.width() / 2, self.br.height() / 2)
        )

        self.update()

        self.setSelected(True)
        self.setFocus()

    def itemChange(self, change, variant):
        if change != QtWidgets.QGraphicsRectItem.ItemSelectedChange:
            global RAW
            RAW = True
        return QtWidgets.QGraphicsRectItem.itemChange(self, change, variant)

    def setGridIntersection(self, scene, state):
        if state is True:
            grid_x = int(self.pos().x() / scene.gridDensity_X)
            grid_y = int(self.pos().y() / scene.gridDensity_Y)
            self.setPos(grid_x * scene.gridDensity_X, grid_y * scene.gridDensity_Y)

    def parentWidget(self):
        return self.scene().views()[0]

    def mouseMoveEvent(self, event):
        if self.isSelected():
            if event.buttons() & QtCore.Qt.LeftButton:
                super(boxItem, self).mouseMoveEvent(event)
            elif event.buttons() & QtCore.Qt.MiddleButton:
                self.rect = QtCore.QRectF(QtCore.QPoint(), event.pos()).normalized()
                self.prepareGeometryChange()
                self.setRect(self.rect)

            self.setGridIntersection(self.p_scene, self.a_state)

    def contextMenuEvent(self, event):
        if self.isSelected():
            super(boxItem, self).contextMenuEvent(event)

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
            pen.setColor(QtGui.QColor(51, 122, 255))
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
    def __init__(self, position, rotation, scale, pixmap, matrix=QtGui.QMatrix(), scene=None, snap=None):
        super(pixmapItem, self).__init__()

        self._canEdit = True

        self.p_scene = scene
        self.a_state = False
        if snap.isChecked():
            self.a_state = True

        self.setRotation(rotation)
        self.setScale(scale)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsFocusable |
                      QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setTransformationMode(QtCore.Qt.SmoothTransformation)

        self.setMatrix(matrix)
        self.setPos(position)
        self.setPixmap(pixmap)

        pixmap = self.pixmap()
        self.setTransformOriginPoint(
            QtCore.QPointF(pixmap.width() / 2, pixmap.height() / 2)
        )

        self.update()

        self.setSelected(True)
        self.setFocus()



    def setGridIntersection(self, scene, state):
        if state is True:
            grid_x = int(self.pos().x() / scene.gridDensity_X)
            grid_y = int(self.pos().y() / scene.gridDensity_Y)
            self.setPos(grid_x * scene.gridDensity_X, grid_y * scene.gridDensity_Y)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            if event.buttons() & QtCore.Qt.LeftButton:
                super(pixmapItem, self).mouseMoveEvent(event)
            self.setGridIntersection(self.p_scene, self.a_state)
