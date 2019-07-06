import os
import sys
import functools
import json

from PySide2 import QtWidgets, QtCore, QtGui, QtPrintSupport
from PySide2.QtCore import SIGNAL

from globals import APP_PATH, MAGICK_NUM, FILE_VERSION, PAGE_SIZE, POINT_SIZE, RAW
from src.widgets.dialogs import settingsGUI
from src.graphics import boxItem, pixmapItem
from src.textItem import textItem, textItemDialog

def getConfigs():
    with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
        data = json.load(settings)
    return data


def writeItemToBuffer(stream, items):
    for item in items:
        if isinstance(item, QtWidgets.QGraphicsTextItem):
            stream.writeQString("Text")
            stream.writeFloat(item.rotation())
            stream.writeFloat(item.scale())
            stream << item.pos() << item.matrix()
            stream.writeQString(item.toPlainText())
            stream << item.font()
        elif isinstance(item, QtWidgets.QGraphicsPixmapItem):
            stream.writeQString("Pixmap")
            stream.writeFloat(item.rotation())
            stream.writeFloat(item.scale())
            stream << item.pos() << item.matrix() << item.pixmap()
        elif isinstance(item, boxItem):
            stream.writeQString("Box")
            stream.writeFloat(item.rotation())
            stream.writeFloat(item.scale())
            stream << item.pos() << item.matrix() << item.rect
            stream.writeInt8(item.lineW)
            stream.writeInt16(item.join)
            stream.writeInt16(item.style)


def readItemsFromBuffer(stream, scene, parent, offset=0, flag=None, snap=None):
    if flag == None:
        type = ""
        position = QtCore.QPointF()
        matrix = QtGui.QMatrix()

        a_snap = snap


        for i in parent.copiedItems:
            type = stream.readQString()
            rotation = float(stream.readFloat())
            scale = float(stream.readFloat())
            stream >> position >> matrix

            if type == "Text":
                text = stream.readQString()
                font = QtGui.QFont()
                stream >> font
                textItem(text, position, rotation, scale, scene, font, matrix, snap=a_snap)
            elif type == "Box":
                rect = QtCore.QRectF()
                stream >> rect
                width = int(stream.readInt8())
                join = QtCore.Qt.PenJoinStyle(stream.readInt16())
                style = QtCore.Qt.PenStyle(stream.readInt16())
                box = boxItem(position, rotation, scale, width, join, style, rect, matrix, scene=scene, snap=a_snap)
                scene.clearSelection()
                scene.addItem(box)
            elif type == "Pixmap":
                image = QtGui.QPixmap()
                stream >> image
                pixmap = pixmapItem(position, rotation, scale, image, scene=scene, snap=a_snap)
                scene.addItem(pixmap)
            scene.clearSelection()
        if offset:
            position += QtCore.QPointF(offset, offset)

    elif flag == "open":
        type = ""
        position = QtCore.QPointF()
        matrix = QtGui.QMatrix()
        type = stream.readQString()
        rotation = float(stream.readFloat())
        scale = float(stream.readFloat())
        stream >> position >> matrix

        a_snap = snap
        print(scene)

        if offset:
            position += QtCore.QPointF(offset, offset)
        if type == "Text":
            text = stream.readQString()
            font = QtGui.QFont()
            stream >> font
            textItem(text, position, rotation, scale, scene, font, matrix, snap=a_snap)
        elif type == "Box":
            rect = QtCore.QRectF()
            stream >> rect
            width = int(stream.readInt8())
            join = QtCore.Qt.PenJoinStyle(stream.readInt16())
            style = QtCore.Qt.PenStyle(stream.readInt16())
            box = boxItem(position, rotation, scale, width, join, style, rect, matrix, scene=scene, snap=a_snap)
            scene.clearSelection()
            scene.addItem(box)
        elif type == "Pixmap":
            image = QtGui.QPixmap()
            stream >> image
            pixmap = pixmapItem(position, rotation, scale, image, scene=scene, snap=a_snap)
            scene.addItem(pixmap)
        scene.clearSelection()


def selectedItems(scene, parent):
    items = scene.selectedItems()
    if len(items) > 0:
        return items
    else:
        QtWidgets.QMessageBox.warning(parent, " Page Designer -- Warning", "No items selected!",
                                      QtWidgets.QMessageBox.Ok)
        return None


def save(scene, parent):
    if not parent.filename:
        path = getConfigs()["common-path"]["project"]
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent, "Page Designer -- Save As", path,
                                                         "Page Designer Files (*.pgd)",
                                                         options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if not fname:
            return
        if not fname.endswith(".pgd"):
            fname += ".pgd"
        parent.filename = fname
    fh = None
    try:
        fh = QtCore.QFile(parent.filename)
        if not fh.open(QtCore.QIODevice.WriteOnly):
            raise IOError(fh.errorString())
        scene.clearSelection()
        stream = QtCore.QDataStream(fh)
        stream.setVersion(QtCore.QDataStream.Qt_5_11)
        stream.writeInt32(MAGICK_NUM)
        stream.writeInt16(FILE_VERSION)
        items = scene.items()
        writeItemToBuffer(stream, items)
    except IOError as e:
        QtWidgets.QMessageBox.warning(parent, "Page Designer -- Save Error",
                                          f"Failed to save {parent.filename}: {e}")
    finally:
        if fh is not None:
            fh.close()

    global RAW
    RAW = False


def checkRawState(scene, parent):
    global RAW
    if RAW == True:
        message = message = QtWidgets.QMessageBox.question(parent, "Page Designer -- Unsaved Changes",
                                                           "Save unsaved changes?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if message == QtWidgets.QMessageBox.Yes:
            save(scene, parent)
    else:
        return


class actionCopy(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionCopy, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/copy.svg")))
        self.setShortcut("Ctrl+C")
        self.setToolTip("Copy selected objects")

        self.connect(SIGNAL("triggered()"), self.copy)

    def copy(self):
        items = selectedItems(self.p_scene, self.w_parent)
        if items is None:
            return
        self.w_parent.copiedItems.clear()
        self.w_parent.pasteOffset = 5
        stream = QtCore.QDataStream(self.w_parent.copiedItems, QtCore.QIODevice.WriteOnly)
        writeItemToBuffer(stream, items)


class actionPaste(QtWidgets.QAction):
    def __init__(self, scene, parent, snap=None):
        super(actionPaste, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent
        self.a_snap = snap

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/paste.svg")))
        self.setShortcut("Ctrl+V")
        self.setToolTip("Paste copied objects")

        self.connect(SIGNAL("triggered()"), self.paste)

    def paste(self):
        if self.w_parent.copiedItems.isEmpty():
            return
        stream = QtCore.QDataStream(self.w_parent.copiedItems, QtCore.QIODevice.ReadOnly)
        readItemsFromBuffer(stream, self.p_scene, self.w_parent, self.w_parent.pasteOffset, snap=self.a_snap)
        self.w_parent.pasteOffset += 5


class actionCut(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionCut, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/cut.svg")))
        self.setShortcut("Ctrl+X")
        self.setToolTip("Remove and copy selected objects")

        self.connect(SIGNAL("triggered()"), self.cut)

    def copy(self):
        items = selectedItems(self.p_scene, self.w_parent)
        if items is None:
            return
        self.w_parent.copiedItems.clear()
        self.w_parent.pasteOffset = 5
        stream = QtCore.QDataStream(self.w_parent.copiedItems, QtCore.QIODevice.WriteOnly)
        writeItemToBuffer(stream, items)

    def cut(self):
        items = selectedItems(self.p_scene, self.w_parent)
        if items is None:
            return
        self.copy()
        for i in items:
            self.p_scene.removeItem(i)
            del i


class actionDelete(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionDelete, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/delete.svg")))
        self.setShortcut("Ctrl+D")
        self.setToolTip("Delete selected objects")

        self.connect(SIGNAL("triggered()"), self.delete)

    def delete(self):
        items = selectedItems(self.p_scene, self.w_parent)
        if items and QtWidgets.QMessageBox.question(self.w_parent, "Page Designer - Delete",
                                                    f"Delete {len(items)} item{'s' if len(items) != 1 else '.'}?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            while items:
                item = items.pop()
                self.p_scene.removeItem(item)
                del item
            global RAW
            RAW = True


class actionSelectAll(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionSelectAll, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        # self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/addBox.svg")))
        self.setShortcut("Shift+A")
        self.setToolTip("Select all items")

        self.connect(SIGNAL("triggered()"), self.selectAll)

    def selectAll(self):
        items = self.p_scene.items()
        for i in items:
            i.setSelected(True)
            print("selected")


class actionCreateBox(QtWidgets.QAction):
    def __init__(self, scene, pos, parent, snap):
        super(actionCreateBox, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent
        self.a_pos = pos
        self.a_snap = snap

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/addBox.svg")))
        self.setShortcut("Ctrl+B")
        self.setToolTip("Create resizable frame")

        self.connect(SIGNAL("triggered()"), self.addBox)

    def addBox(self):
        box = boxItem(
            self.a_pos(), 0, 1, 2, QtCore.Qt.BevelJoin, QtCore.Qt.SolidLine,
            rect=None, matrix=QtGui.QMatrix(), scene=self.p_scene, snap=self.a_snap)
        self.p_scene.clearSelection()
        self.p_scene.addItem(box)
        global RAW
        RAW = True


class actionCreateText(QtWidgets.QAction):
    def __init__(self, scene, pos, parent, snap=None):
        super(actionCreateText, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent
        self.a_pos = pos
        self.a_snap = snap

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/addText.svg")))
        self.setShortcut("Ctrl+T")
        self.setToolTip("Create text item")

        self.connect(SIGNAL("triggered()"), self.addText)

    def addText(self):
        dialog = textItemDialog(position=self.a_pos(), scene=self.p_scene, parent=self.w_parent, snap=self.a_snap)
        dialog.exec_()


class actionCreatePixmapItem(QtWidgets.QAction):
    def __init__(self, scene, pos, parent, snap=None):
        super(actionCreatePixmapItem, self).__init__(parent)

        self.p_scene = scene
        print(self.p_scene)
        self.w_parent = parent
        self.a_pos = pos
        self.a_snap = snap

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/addPixmap.svg")))
        self.setShortcut("Ctrl+P")
        self.setToolTip("Create image item")

        self.connect(SIGNAL("triggered()"), self.addPixmap)

    def addPixmap(self):
        #path = QtCore.QFileInfo(self.w_parent.filename).path() if self.w_parent.filename else "."
        path = getConfigs()["common-path"]["pixmap"]
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self.w_parent, "Page Designer - Add Pixmap", path,
                                                         "Pixmap Files (*.bmp *.jpg *.jpeg *.png)",
                                                         options=QtWidgets.QFileDialog.DontUseNativeDialog)
        pixmap = pixmapItem(
            self.a_pos(), 0, 1, fname, QtGui.QMatrix(), self.p_scene, self.a_snap
        )
        self.p_scene.clearSelection()
        self.p_scene.addItem(pixmap)
        global RAW
        RAW = True


class actionOpenFile(QtWidgets.QAction):
    def __init__(self, scene, parent, snap):
        super(actionOpenFile, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent
        self.a_snap = snap

        self.setText("Open file")
        self.setShortcut("Ctrl+O")
        self.setToolTip("Open existing file")

        fOpen = functools.partial(self.openFile, self.a_snap)
        self.connect(SIGNAL("triggered()"), fOpen)

    def openFile(self, snap=None):
        checkRawState(self.p_scene, self.w_parent)

        if snap.isChecked():
            snap.click()

        #path = QtCore.QFileInfo(self.w_parent.filename).path() if self.w_parent.filename else "."
        path = getConfigs()["common-path"]["project"]
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self.w_parent, "Page Designer - Open", path,
                                                         "Page Designer Files (*.pgd)",
                                                         options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if not fname:
            return
        self.w_parent.filename = fname
        fh = None
        try:
            fh = QtCore.QFile(self.w_parent.filename)
            if not fh.open(QtCore.QIODevice.ReadOnly):
                raise IOError(fh.errorString())

            items = self.p_scene.items()
            while items:
                item = items.pop()
                #print(item)
                self.p_scene.removeItem(item)
                del item

            self.addBorders()

            stream = QtCore.QDataStream(fh)
            stream.setVersion(QtCore.QDataStream.Qt_5_12)
            magic = stream.readInt32()

            if magic != MAGICK_NUM:
                raise IOError("not a valid .pgd file")

            fileVersion = stream.readInt16()
            if fileVersion != FILE_VERSION:
                raise IOError("unrecognised .pgd file version")

            while not fh.atEnd():
                readItemsFromBuffer(stream, self.p_scene, self.w_parent, flag="open", snap=self.a_snap)

        except IOError as e:
            QtWidgets.QMessageBox.warning(self.w_parent, "Page Designer -- Open Error",
                                          f"Failed to open {self.w_parent.filename}: {e}")
        finally:
            if fh is not None:
                fh.close()
            #snap.click()

        global RAW
        RAW = False

    def addBorders(self):
        borders = []
        rect = QtCore.QRectF(0, 0, PAGE_SIZE[0], PAGE_SIZE[1]) # TODO different page sizes
        borders.append(self.p_scene.addRect(rect, QtGui.QPen(), QtGui.QBrush(QtCore.Qt.lightGray)))
        margin = 5.25 * POINT_SIZE
        borders.append(self.p_scene.addRect(rect.adjusted(margin, margin, -margin, -margin), QtGui.QPen(),
                                                 QtGui.QBrush(QtCore.Qt.white)))
        self.w_parent.borders = borders #


class actionSaveFile(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionSaveFile, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setText("Save file")
        self.setShortcut("Ctrl+S")
        self.setToolTip("Save current file")

        self.connect(SIGNAL("triggered()"), self.saveFile)

    def saveFile(self):
        save(self.p_scene, self.w_parent)


class actionPrintFile(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionPrintFile, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setText("Print file")
        self.setShortcut("Ctrl+Shift+P")
        self.setToolTip("Print current file / export to PDF format")

        self.connect(SIGNAL("triggered()"), self.printFile)

    def printFile(self):
        dialog = QtPrintSupport.QPrintDialog(self.w_parent.printer)
        if dialog.exec_():
            painter = QtGui.QPainter(self.w_parent.printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            self.p_scene.clearSelection()
            self.hideBorders()
            self.p_scene.render(painter)
            self.showBorders()

    def hideBorders(self):
        for i in range(len(self.w_parent.borders)):
            self.w_parent.borders[i].setVisible(False)

    def showBorders(self):
        for i in range(len(self.w_parent.borders)):
            self.w_parent.borders[i].setVisible(True)


class actionQuitApp(QtWidgets.QAction):
    def __init__(self, scene, parent):
        super(actionQuitApp, self).__init__(parent)

        self.p_scene = scene
        self.w_parent = parent

        self.setText("Quit")
        self.setShortcut("Ctrl+Q")
        self.setToolTip("Close application")

        self.connect(SIGNAL("triggered()"), self.quitApp)

    def quitApp(self):
        checkRawState(self.p_scene, self.w_parent)
        sys.exit(0)


class actionOpenSettings_GUI(QtWidgets.QAction):
    def __init__(self, parent):
        super(actionOpenSettings_GUI, self).__init__(parent)

        self.w_parent = parent

        self.setText("Open GUI Settings")
        self.setToolTip("Open settings to configure user interface appearance")

        self.connect(SIGNAL("triggered()"), self.openSetting_GUI)

    def openSetting_GUI(self):
        dialog = settingsGUI()
        dialog.exec_()
