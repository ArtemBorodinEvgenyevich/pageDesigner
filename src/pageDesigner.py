from PySide2 import QtCore, QtWidgets, QtPrintSupport, QtGui
from PySide2.QtCore import SIGNAL
from .globals import *
from .graphics import graphicsView as GrahpicsView
from .graphics import boxItem as BoxItem
from .textItem import textItemDialog as TextItemDlg
from .textItem import textItem as TextItem
import functools
import random
import sys

MAC = "qt_mac_set_native_menubar" in dir()

class mainForm(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(mainForm, self).__init__(parent)


        self.filename = ""
        self.copiedItems = QtCore.QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QtCore.QPoint()
        self.addOffset = 5
        self.borders = []


        self.printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)


        self.view = GrahpicsView()
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        self.addBorders()
        self.view.setScene(self.scene)


        self.wrapped = []
        buttonLayout = QtWidgets.QVBoxLayout()
        for text, slot in (("Add &Text", self.addText),
                           ("Add &Box", self.addBox),
                           ("Add Pi&xmap", self.addPixmap),
                           ("&Align", None),
                           ("&Copy", self.copy),
                           ("C&ut", self.cut),
                           ("&Paste", self.paste),
                           ("&Delete...", self.delete),
                           ("&Rotate", self.rotate),
                           ("Pri&nt...", self.printFile),
                           ("&Open...", self.open),
                           ("&Save", self.save),
                           ("&Quit", self.accept)):
            button = QtWidgets.QPushButton(text)
            if not MAC:
                button.setFocusPolicy(QtCore.Qt.NoFocus)
            if slot is not None:
                self.connect(button, SIGNAL("clicked()"), slot)
            if text == "&Align":
                menu = QtWidgets.QMenu(self)
                for text, arg in (("Align &Left", QtCore.Qt.AlignLeft),
                                  ("Align &Right", QtCore.Qt.AlignRight),
                                  ("Align &Top", QtCore.Qt.AlignTop),
                                  ("Align &Bottom", QtCore.Qt.AlignBottom)):
                    wrapper = functools.partial(self.setAlignment, arg)
                    self.wrapped.append(wrapper)
                    menu.addAction(text, wrapper)
                button.setMenu(menu)
            if text == "Pri&nt...":
                buttonLayout.addStretch(5)
            if text == "&Quit":
                buttonLayout.addStretch(1)
            buttonLayout.addWidget(button)
        buttonLayout.addStretch()


        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.view, 1)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)


        fm = QtGui.QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle(f"Page Designer {PROGRAM_VERSION}")


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


    def reject(self):
        self.accept()


    def accept(self):
        self.offerSave()
        QtWidgets.QDialog.accept(self)


    def offerSave(self):
        if RAW and QtWidgets.QMessageBox.question(self,
                                                  "Page Designer -- Unsaved Changes",
                                                  "Save unsaved changes?",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            self.save()


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


    def addBox(self):
        BoxItem(self.position(), self.scene)


    def addPixmap(self):
        path = QtCore.QFileInfo(self.filename).path() if self.filename else "."
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Page Designer - Add Pixmap", path,
                                                      "Pixmap Files (*.bmp *.jpg *.jpeg *.png)")
        if not fname:
            return
        pixmap = QtGui.QPixmap(fname)
        self.createPixmapItem(pixmap, self.position())


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


    def selectedItem(self):
        items = self.scene.selectedItems()
        if len(items) == 1:
            return items[0]
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


    def paste(self):
        if self.copiedItems.isEmpty():
            return
        stream = QtCore.QDataStream(self.copiedItems, QtCore.QIODevice.ReadOnly)
        self.readItemsFromStream(stream, self.pasteOffset)
        self.pasteOffset += 5


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
        elif alignment == QtCore.Qt.AlignRight:
            xAlignment = min(rightXs)
            for i, item in enumerate(items):
                item.moveBy(xAlignment - rightXs[i], 0)
        elif alignment == QtCore.Qt.AlignTop:
            yAlignment = min(topYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - topYs[i])
        elif alignment == QtCore.Qt.AlignBottom:
            yAlignment = min(bottomYs)
            for i, item in enumerate(items):
                item.moveBy(0, yAlignment - bottomYs[i])
        global RAW
        RAW = True


    def rotate(self):
        for item in self.scene.selectedItems():
            coord = item.pos()
            print(coord)
            item.rotate(15)
        self.scene.update()


    def delete(self):
        items = self.scene.selectedItems()
        if len(items) and QtWidgets.QMessageBox.question(self, "Page Designer - Delete",
                                                         f"Delete {len(items)} item{'s' if len(items) != 1 else '.'}?",
                                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
            global RAW
            RAW = True


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


    def open(self):
        self.offerSave()
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
            style = QtCore.Qt.PenStyle(stream.readInt16())
            BoxItem(position, self.scene, style, rect, matrix)
        elif type == "Pixmap":
            pixmap = QtGui.QPixmap()
            stream >> pixmap
            self.createPixmapItem(pixmap, position, matrix)



