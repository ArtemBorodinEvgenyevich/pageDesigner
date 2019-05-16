import functools
import random
import sys

from PySide2 import QtCore, QtWidgets, QtPrintSupport, QtGui
from PySide2.QtCore import SIGNAL

from globals import *
from .dialogs import settingsGUI as GUIsettings
from .graphics import Rectangle as BoxItem
from .graphics import graphicsView as GrahpicsView
from .textItem import textItem as TextItem
from .textItem import textItemDialog as TextItemDlg

MAC = "qt_mac_set_native_menubar" in dir()


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self, path):
        super(mainWindow, self).__init__()

        self.absolutePath = path

        self.filename = ""
        self.copiedItems = QtCore.QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QtCore.QPoint()
        self.addOffset = 5
        self.borders = []

        self.printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)

        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        self.addBorders()
        self.view = GrahpicsView(self.scene, self)

        self.setCentralWidget(self.view)
        # self.setWindowTitle(f"Page Designer {PROGRAM_VERSION}")
        self.setWindowTitle("Page Designer --Alpha--")

        self.setNavBar()
        self.setToolBox()
        self.setNotificationBar()
        self.setObjectName("mainWindow")

        # with open(self.ui_style_path, "r") as sf:
        #    self.setStyleSheet(sf.read())
        #    self.update()
        # self.setStyle(QtWidgets.QStyleFactory.create("windows"))

    def setNavBar(self):
        self.navBar = QtWidgets.QMenuBar(self)
        self.navBar.setObjectName("navBar")
        self.navBar.setFixedHeight(20)

        fileMenu = QtWidgets.QMenu("&File", self.navBar)
        for text, slot, shortcut, tooltip in (("Open...", self.open, "Ctrl+O", "Open existing file"),
                                              ("Save", self.save, "Ctrl+S", "Save current file"),
                                              ("Print...", self.printFile, "Ctrl+P",
                                               "Send file to device / PDF export"),
                                              ("Quit", self.quitApp, "Ctrl+Q", "Quit application")):
            action = QtWidgets.QAction(text, self)
            action.connect(SIGNAL("triggered()"), slot)
            action.setShortcut(shortcut)
            action.setToolTip(tooltip)
            fileMenu.addAction(action)
            fileMenu.addSeparator()

        viewMenu = QtWidgets.QMenu("&Edit", self.navBar)
        for text, slot, tooltip in (("Application Settings", self.openGUI_Settings, "Edit application appearence"),
                                    ("Same", self.openGUI_Settings, "Doing same")):
            action = QtWidgets.QAction(text, self)
            action.connect(SIGNAL("triggered()"), slot)
            action.setToolTip(tooltip)
            viewMenu.addAction(action)

        self.navBar.addMenu(fileMenu)
        self.navBar.addMenu(viewMenu)
        self.setMenuBar(self.navBar)

    def setToolBox(self):
        toolBox = QtWidgets.QToolBar()
        toolBox.setObjectName("toolBox")
        # toolBox.setMovable(False)
        toolBox.setMinimumHeight(40)

        if not MAC:
            toolBox.setFocusPolicy(QtCore.Qt.NoFocus)

        # Add geometry functions
        for text, slot, shortcut, \
            icon in (
                ("Add Text", self.addText, "Ctrl+T",
                 QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/addText.svg")),
                ("Add Box", self.addBox, "Ctrl+B", QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/addBox.svg")),
                (
                        "Add Pixmap", self.addPixmap, "Ctrl+I",
                        QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/addPixmap.svg"))):
            action = QtWidgets.QAction(self)
            action.connect(SIGNAL("triggered()"), slot)
            action.setShortcut(shortcut)
            action.setToolTip(text)
            action.setIcon(icon)
            toolBox.addAction(action)
        toolBox.addSeparator()

        # Add editing functions
        for text, slot, shortcut, \
            icon in (("Copy", self.copy, "Ctrl+C", QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/copy.svg")),
                     ("Cut", self.cut, "Ctrl+X", QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/cut.svg")),
                     ("Paste", self.paste, "Ctrl+V", QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/paste.svg")),
                     ("Delete", self.delete, "Ctrl+D",
                      QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/delete.svg"))):
            if slot is not None:
                action = QtWidgets.QAction(self)
                action.connect(SIGNAL("triggered()"), slot)
                action.setShortcut(shortcut)
                action.setToolTip(text)
                action.setIcon(icon)
                toolBox.addAction(action)
        toolBox.addSeparator()

        shiftButton = QtWidgets.QPushButton(toolBox)
        shiftButton.setIcon(QtGui.QIcon(self.absolutePath + "/stylesheets/toolbar/shift.svg"))
        menu = QtWidgets.QMenu(shiftButton)
        for text, arg in (("Shift Left", QtCore.Qt.AlignLeft),
                          ("Shift Right", QtCore.Qt.AlignRight),
                          ("Shift Top", QtCore.Qt.AlignTop),
                          ("Shift Bottom", QtCore.Qt.AlignBottom)):
            wrapper = functools.partial(self.setAlignment, arg)
            menu.addAction(text, wrapper)
        shiftButton.setMenu(menu)
        shiftButton.connect(SIGNAL("triggered()"), QtWidgets.QToolButton.showMenu)
        shiftButton.setToolTip("Shift selected elements randomly")
        shiftButton.setObjectName("toolBarButton")
        toolBox.addWidget(shiftButton)

        self.addToolBar(toolBox)

    def openGUI_Settings(self):
        dialog = GUIsettings()
        dialog.exec_()
        if dialog.Accepted:
            self.notifyBar.showMessage("-- Your settings have been updated!", 4000)



    def setNotificationBar(self):
        self.notifyBar = QtWidgets.QStatusBar()
        # self.notifyBar.showMessage("Test", 5000)
        self.notifyBar.setObjectName('notifyBar')
        self.setStatusBar(self.notifyBar)



    def addBorders(self):
        self.borders = []
        rect = QtCore.QRectF(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        self.borders.append(self.scene.addRect(rect, QtGui.QPen(), QtGui.QBrush(QtCore.Qt.lightGray)))
        margin = 5.25 * POINT_SIZE
        self.borders.append(self.scene.addRect(
            rect.adjusted(margin, margin, -margin, -margin), QtGui.QPen(),
            QtGui.QBrush(QtCore.Qt.white)))


    def removeBorders(self):
        while self.borders:
            item = self.borders.pop()
            self.scene.removeItem(item)
            del item



    def hideBorders(self):
        for i in range(len(self.borders)):
            self.borders[i].setVisible(False)


    def showBorders(self):
        for i in range(len(self.borders)):
            self.borders[i].setVisible(True)

    def quitApp(self):
        self.checkIfSaved()
        sys.exit(0)

    def checkIfSaved(self):
        if RAW == True:
            message = QtWidgets.QMessageBox.question(self, "Page Designer -- Unsaved Changes",
                                                     "Save unsaved changes?",
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if message == QtWidgets.QMessageBox.Yes:
                self.save()
        else:
            return

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


    def addText(self):
        dialog = TextItemDlg(position=self.position(),
                             scene=self.scene, parent=self)
        dialog.exec_()
        if dialog.Accepted:
            self.notifyBar.showMessage("-- Your text has been added!", 4000)


    def addBox(self):
        #midX = PAGE_SIZE[0] + PAGE_SIZE[0] / 2
        #midY = PAGE_SIZE[1] + PAGE_SIZE[1] / 2
        BoxItem(self.position(), self.scene, 2, QtCore.Qt.BevelJoin, QtCore.Qt.SolidLine)
        self.notifyBar.showMessage("-- Your box element has been added!", 4000)
        global RAW
        RAW = True

    def addPixmap(self):
        path = QtCore.QFileInfo(self.filename).path() if self.filename else "."
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Page Designer - Add Pixmap", path,
                                                      "Pixmap Files (*.bmp *.jpg *.jpeg *.png)")
        if not fname:
            return
        pixmap = QtGui.QPixmap(fname)
        self.createPixmapItem(pixmap, self.position())
        self.notifyBar.showMessage("-- Your pixmap has been added!", 4000)


    def createPixmapItem(self, pixmap, position, matrix=QtGui.QMatrix()):
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        item.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable)
        item.setPos(position)
        item.setMatrix(matrix)
        self.scene.clearSelection()
        self.scene.addItem(item)
        item.setSelected(True)
        global RAW
        RAW = True


    def copy(self):
        item = self.selectedItem()
        if item is None:
            return
        self.copiedItems.clear()
        self.pasteOffset = 5
        stream = QtCore.QDataStream(self.copiedItems, QtCore.QIODevice.WriteOnly)
        self.writeItemToStream(stream, item)
        self.notifyBar.showMessage("-- Your item has been copied!", 4000)


    def selectedItem(self):
        items = self.scene.selectedItems()
        if len(items) == 1:
            return items[0]
        elif len(items) > 1:
            self.notifyBar.showMessage("-- Only one item allowed to copy / cut!", 4000)
            return None
        self.notifyBar.showMessage("-- No item to copy!", 4000)
        return None


    def cut(self):
        item = self.selectedItem()
        if item is None:
            QtWidgets.QMessageBox.warning(self, " Page Designer -- Cutting items",
                                          "No items to cut!", QtWidgets.QMessageBox.Ok)
            return
        self.copy()
        self.scene.removeItem(item)
        del item
        self.notifyBar.showMessage("-- Your item has been cut!", 4000)


    def paste(self):
        if self.copiedItems.isEmpty():
            return
        stream = QtCore.QDataStream(self.copiedItems, QtCore.QIODevice.ReadOnly)
        self.readItemsFromStream(stream, self.pasteOffset)
        self.pasteOffset += 5
        self.notifyBar.showMessage("-- Your item has been added!", 4000)


    def setAlignment(self, alignment):
        items = self.scene.selectedItems()
        if len(items) <= 1:
            return
        leftXs = rightXs = topYs = bottomYs = []
        for item in items:
            rect = item.sceneBoundingRect()
            leftXs.append(rect.x())
            rightXs.append(rect.x() + rect.width())
            topYs.append(rect.y())
            bottomYs.append(rect.y() + rect.height())
        # Perform alignment
        if alignment == QtCore.Qt.AlignLeft:
            xAlignment = min(leftXs)
            for i, item in enumerate(items):
                item.moveBy(xAlignment - leftXs[i], 0)
            self.notifyBar.showMessage("-- Moved to left.", 4000)
        elif alignment == QtCore.Qt.AlignRight:
            xAlignment = min(rightXs)
            for i, item in enumerate(items):
                item.moveBy(xAlignment - rightXs[i], 0)
            self.notifyBar.showMessage("-- Moved to right.", 4000)
        elif alignment == QtCore.Qt.AlignTop:
            yAlignment = min(topYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - topYs[i])
            self.notifyBar.showMessage("-- Moved to top.", 4000)
        elif alignment == QtCore.Qt.AlignBottom:
            yAlignment = min(bottomYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - bottomYs[i])
            self.notifyBar.showMessage("-- Moved to bottom.", 4000)
        global RAW
        RAW = True


    def delete(self):
        items = self.scene.selectedItems()
        if len(items) and QtWidgets.QMessageBox.question(self, "Page Designer - Delete",
                                                         f"Delete {len(items)} item{'s' if len(items) != 1 else '.'}?",
                                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
            self.notifyBar.showMessage("-- Your item(s) has been deleted!", 4000)
            global RAW
            RAW = True
        else:
            self.notifyBar.showMessage("-- No items to delete!", 4000)



    def printFile(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            self.scene.clearSelection()
            self.hideBorders()
            self.scene.render(painter)
            self.showBorders()
        self.notifyBar.showMessage("-- Your page has been successfully printed!", 4000)


    def open(self):
        self.checkIfSaved()

        path = QtCore.QFileInfo(self.filename).path() if self.filename else "."
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Page Designer - Open", path,
                                                      "Page Designer Files (*.pgd)")
        if not fname:
            return
        self.filename = fname
        fh = None
        try:
            fh = QtCore.QFile(self.filename)
            if not fh.open(QtCore.QIODevice.ReadOnly):
                raise IOError(fh.errorString())
            items = self.scene.items()
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
            self.addBorders()
            stream = QtCore.QDataStream(fh)
            stream.setVersion(QtCore.QDataStream.Qt_5_11)
            magic = stream.readInt32()
            if magic != MAGICK_NUM:
                raise IOError("not a valid .pgd file")
            fileVersion = stream.readInt16()
            if fileVersion != FILE_VERSION:
                raise IOError("unrecognised .pgd file version")
            while not fh.atEnd():
                self.readItemsFromStream(stream)
        except IOError as e:
            QtWidgets.QMessageBox.warning(self, "Page Designer -- Open Error",
                                          f"Failed to open {self.filename}: {e}")
        finally:
            if fh is not None:
                fh.close()
        self.notifyBar.showMessage("-- File has been successfully opened!", 4000)
        global RAW
        RAW = False

    def save(self):
        if not self.filename:
            path = "."
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Page Designer -- Save As", path,
                                                          "Page Designer Files (*.pgd)")
            print(fname)
            if not fname:
                return
            if not fname.endswith(".pgd"):
                fname += ".pgd"
            self.filename = fname
        fh = None
        try:
            fh = QtCore.QFile(self.filename)
            if not fh.open(QtCore.QIODevice.WriteOnly):
                raise IOError(fh.errorString())
            self.scene.clearSelection()
            stream = QtCore.QDataStream(fh)
            stream.setVersion(QtCore.QDataStream.Qt_5_11)
            stream.writeInt32(MAGICK_NUM)
            stream.writeInt16(FILE_VERSION)
            for item in self.scene.items():
                self.writeItemToStream(stream, item)
        except IOError as e:
            QtWidgets.QMessageBox.warning(self, "Page Designer -- Save Error",
                                          f"Failed to save {self.filename}: {e}")
        finally:
            if fh is not None:
                fh.close()
        self.notifyBar.showMessage("-- File has been successfully saved!", 4000)
        global RAW
        RAW = False


    def writeItemToStream(self, stream, item):
        if isinstance(item, QtWidgets.QGraphicsTextItem):
            stream.writeQString("Text")
            stream << item.pos() << item.matrix()
            stream.writeQString(item.toPlainText())
            stream << item.font()
        elif isinstance(item, QtWidgets.QGraphicsPixmapItem):
            stream.writeQString("Pixmap")
            stream << item.pos() << item.matrix() << item.pixmap()
        elif isinstance(item, BoxItem):
            stream.writeQString("Box")
            stream << item.pos() << item.matrix() << item.rect
            stream.writeInt8(item.lineW)
            stream.writeInt16(item.join)
            stream.writeInt16(item.style)


    def readItemsFromStream(self, stream, offset=0):
        type = ""
        position = QtCore.QPointF()
        matrix = QtGui.QMatrix()
        type = stream.readQString()
        stream >> position >> matrix

        if offset:
            position += QtCore.QPointF(offset, offset)
        if type == "Text":
            text = stream.readQString()
            font = QtGui.QFont()
            stream >> font
            TextItem(text, position, self.scene, font, matrix)
        elif type == "Box":
            rect = QtCore.QRectF()
            stream >> rect
            width = int(stream.readInt8())
            join = QtCore.Qt.PenJoinStyle(stream.readInt16())
            style = QtCore.Qt.PenStyle(stream.readInt16())
            BoxItem(position, self.scene, width, join, style, rect, matrix)
        elif type == "Pixmap":
            pixmap = QtGui.QPixmap()
            stream >> pixmap
            self.createPixmapItem(pixmap, position, matrix)
        self.scene.clearSelection()