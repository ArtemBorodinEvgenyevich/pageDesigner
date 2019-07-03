from PySide2 import QtWidgets, QtPrintSupport

from .actions.actions import actionSelectAll
from .widgets.mainWindow import toolBox, menuBar, statusBar, centralWidget


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowTitle("Page Designer --Alpha--")
        self.setObjectName("mainWindow")


        self.printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)

        self.centralWidget = centralWidget(self.printer, self)

        self.setCentralWidget(self.centralWidget)


        # Init widgets
        self.toolBox = toolBox(self.centralWidget.scene, self.centralWidget.view, self.centralWidget.position, self.centralWidget)
        self.menuBar = menuBar(self.centralWidget.scene, self.centralWidget)
        self.statusBar = statusBar()

        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBox)
        self.setStatusBar(self.statusBar)

        # Init actions not listed in toolBox
        act_selectAll = actionSelectAll(self.centralWidget.scene, self.centralWidget)
        #act_closeOpenPBox = actionOpenClosePropertyBox(self.propBox, self)

        self.addAction(act_selectAll)
        # add page borders to the viewport
        self.centralWidget.addBorders()

