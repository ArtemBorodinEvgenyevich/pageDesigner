import random

from PySide2 import QtCore, QtWidgets, QtPrintSupport, QtGui

from globals import *
from .graphics import graphicsView as GrahpicsView
from .widgets.mainWindow import toolBox, menuBar, statusBar
from .actions.actions import actionSelectAll


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowTitle("Page Designer --Alpha--")
        self.setObjectName("mainWindow")

        self.filename = ""
        self.copiedItems = QtCore.QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QtCore.QPoint()
        self.addOffset = 5
        self.borders = []

        self.printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)

        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])  # TODO different sizes
        self.view = GrahpicsView(self.scene, self)

        self.setCentralWidget(self.view)

        # Init widgets
        self.toolBox = toolBox(self.scene, self.view, self.position, self)
        self.menuBar = menuBar(self.scene, self)
        self.statusBar = statusBar()

        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBox)
        self.setStatusBar(self.statusBar)

        # Init actions not listed in toolBox
        act_selectAll = actionSelectAll(self.scene, self)
        self.addAction(act_selectAll)

        # add page borders to the viewport
        self.addBorders()

    def position(self):
        point = self.mapFromGlobal(QtGui.QCursor.pos())
        if not self.view.geometry().contains(point):
            coord = random.randint(36, 144)
            point = QtCore.QPoint(coord, coord)
        else:
            if point == self.prevPoint:
                point += QtCore.QPoint(self.addOffset, self.addOffset)
                self.addOffset += 5
            else:
                self.addOffset = 5
                self.prevPoint = point
        return self.view.mapToScene(point)

    def addBorders(self):
        self.borders = []
        rect = QtCore.QRectF(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        self.borders.append(self.scene.addRect(rect, QtGui.QPen(), QtGui.QBrush(QtCore.Qt.lightGray)))
        margin = 5.25 * POINT_SIZE
        self.borders.append(self.scene.addRect(
            rect.adjusted(margin, margin, -margin, -margin), QtGui.QPen(),
            QtGui.QBrush(QtCore.Qt.white)))
