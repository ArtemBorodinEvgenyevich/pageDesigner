from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import SIGNAL

from globals import POINT_SIZE


class textItem(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, position, rotation, scale, scene,
                 font=QtGui.QFont("Times", POINT_SIZE), matrix=QtGui.QMatrix(), snap=None):
        super(textItem, self).__init__(text)

        self._canEdit = True

        self.p_scene = scene
        self.a_state = False
        print(snap)
        if snap.isChecked():
            self.a_state = True


        self.setRotation(rotation)
        self.setScale(scale)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsMovable)

        self.setFont(font)
        self.setPos(position)
        self.setMatrix(matrix)

        br = self.boundingRect()
        self.setTransformOriginPoint(
            QtCore.QPointF(br.width() / 2, br.height() / 2)
        )

        self.p_scene.clearSelection()
        self.p_scene.addItem(self)

        self.setSelected(True)
        global RAW
        RAW = True

        self.update()

        self.setGridIntersection(scene, snap)

    def parentWidget(self):
        return self.scene().views()[0]

    def itemChange(self, change, variant):
        if change != QtWidgets.QGraphicsItem.ItemSelectedChange:
            global RAW
            RAW = True
        return QtWidgets.QGraphicsTextItem.itemChange(self, change, variant)

    def setGridIntersection(self, scene, state):
        if state is True:
            grid_x = int(self.pos().x() / scene.gridDensity_X)
            grid_y = int(self.pos().y() / scene.gridDensity_Y)
            self.setPos(grid_x * scene.gridDensity_X, grid_y * scene.gridDensity_Y)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            if event.buttons() & QtCore.Qt.LeftButton:
                super(textItem, self).mouseMoveEvent(event)
            self.setGridIntersection(self.p_scene, self.a_state)

    def mouseDoubleClickEvent(self, event):
        dialog = textItemDialog(self, self.parentWidget())
        dialog.exec_()



class textItemDialog(QtWidgets.QDialog):
    def __init__(self, item=None, position=None, scene=None, parent=None, snap=None):
        super(textItemDialog, self).__init__(parent)

        self.item = item
        self.position = position
        self.scene = scene
        self.a_snap = snap
        print(self.a_snap)

        self.editor = QtWidgets.QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabChangesFocus(True)
        editorLable = QtWidgets.QLabel("&Text:")
        editorLable.setBuddy(self.editor)
        self.fontComboBox = QtWidgets.QFontComboBox()
        self.fontComboBox.setCurrentFont(QtGui.QFont("Times", POINT_SIZE))
        fontLable = QtWidgets.QLabel("&Font:")
        fontLable.setBuddy(self.fontComboBox)
        self.fontSpinBox = QtWidgets.QSpinBox()
        self.fontSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.fontSpinBox.setRange(6, 280)
        self.fontSpinBox.setValue(POINT_SIZE)
        fontSizeLable = QtWidgets.QLabel("&Size")
        fontSizeLable.setBuddy(self.fontSpinBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                    QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.editor.setPlainText(self.item.toPlainText())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())

        layout = QtWidgets.QGridLayout()
        layout.addWidget(editorLable, 0, 0)
        layout.addWidget(self.editor, 1, 0, 1, 6)
        layout.addWidget(fontLable, 2, 0)
        layout.addWidget(self.fontComboBox, 2, 1, 1, 2)
        layout.addWidget(fontSizeLable, 2, 3)
        layout.addWidget(self.fontSpinBox, 2, 4, 1, 2)
        layout.addWidget(self.buttonBox, 3, 0, 1, 6)
        self.setLayout(layout)

        self.connect(self.fontComboBox,
                     SIGNAL("currentFontChanged(QtGui.QFont())"), self.updateUi)
        self.connect(self.fontSpinBox,
                     SIGNAL("valueChanged(int)"), self.updateUi)
        self.connect(self.editor, SIGNAL("textChanged()"),
                     self.updateUi)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)

        self.setWindowTitle("Page Designer - {} Text Item".format(
            "Add" if self.item is None else "Edit"))
        self.updateUi()

    def updateUi(self):
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.editor.document().setDefaultFont(font)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(self.editor.toPlainText()))

    def accept(self):
        if self.item is None:
            self.item = textItem("", self.position, 0, 1, self.scene, snap=self.a_snap)
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setPlainText(self.editor.toPlainText())

        br = self.item.boundingRect()
        self.item.setTransformOriginPoint(
            QtCore.QPointF(br.width() / 2, br.height() / 2)
        )

        self.item.update()
        global RAW
        RAW = True
        QtWidgets.QDialog.accept(self)
