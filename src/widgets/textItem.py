from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import SIGNAL
from globals import POINT_SIZE
from src.widgets.textWidgets import codeEditor, textEditorWindow
from time import strftime



class textItem(QtWidgets.QGraphicsTextItem):
    """ Standard QGraphicsTextItem showing plain/html formated text """
    def __init__(self, text, position, rotation, scale, scene,
                 font=QtGui.QFont("Times", POINT_SIZE), matrix=QtGui.QMatrix(), snap=None, mode="plain"):
        super(textItem, self).__init__()

        self._canEdit = True

        self.p_scene = scene
        self.a_state = False
        self.mode = mode

        if snap.isChecked():
            self.a_state = True

        self.setRotation(rotation)
        self.setScale(scale)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsMovable)

        self.setFont(font)
        self.setPos(position)
        self.setMatrix(matrix)

        if mode == "plain":
            self.setPlainText(text)
        elif mode == "html":
            self.setHtml(text)


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
        if self.mode == "plain":
            dialog = codeSnippetItemDialog(self, self.parentWidget())
            dialog.exec_()
        elif self.mode == "html":
            dialog = textItemDialog(self, self.parentWidget())
            dialog.exec_()


class codeSnippetItemDialog(QtWidgets.QDialog):
    """ Dialog to input and code snippet and add into the QGraphicsScene """
    def __init__(self, item=None, position=None, scene=None, parent=None, snap=None):
        super(codeSnippetItemDialog, self).__init__(parent)

        self.item = item
        self.position = position
        self.scene = scene
        self.a_snap = snap

        self.textField = codeEditor(self)
        editorLabel = QtWidgets.QLabel("&Text:")
        editorLabel.setBuddy(self.textField)

        self.fontComboBox = QtWidgets.QFontComboBox()
        self.fontComboBox.setCurrentFont(QtGui.QFont("Times", POINT_SIZE))
        fontLabel = QtWidgets.QLabel("&Font:")
        fontLabel.setBuddy(self.fontComboBox)

        self.fontSpinBox = QtWidgets.QSpinBox()
        self.fontSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.fontSpinBox.setRange(6, 280)
        self.fontSpinBox.setValue(POINT_SIZE)
        fontSizeLabel = QtWidgets.QLabel("&Size:")
        fontSizeLabel.setBuddy(self.fontSpinBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                    QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.textField.setPlainText(self.item.toPlainText())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(editorLabel, alignment=QtCore.Qt.AlignLeft)

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addSpacing(40)
        layout1.addWidget(self.textField)
        layout.addLayout(layout1)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(fontLabel, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout2.addWidget(self.fontComboBox, alignment=QtCore.Qt.AlignRight, stretch=0)
        layout2.addSpacing(10)

        layout3 = QtWidgets.QHBoxLayout()
        layout3.addWidget(fontSizeLabel, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout3.addWidget(self.fontSpinBox, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout2.addLayout(layout3)
        layout.addLayout(layout2)

        layout.addWidget(self.buttonBox, alignment=QtCore.Qt.AlignRight)

        self.connect(self.fontComboBox,
                     SIGNAL("currentFontChanged(QtGui.QFont())"), self.updateUi)
        self.connect(self.fontSpinBox,
                     SIGNAL("valueChanged(int)"), self.updateUi)
        self.connect(self.textField, SIGNAL("textChanged()"),
                     self.updateUi)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)

        self.setWindowTitle("Page Designer - {} Text Item".format(
            "Add" if self.item is None else "Edit"))
        self.updateUi()

    def updateUi(self):
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.textField.document().setDefaultFont(font)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(self.textField.toPlainText()))

    def accept(self):
        if self.item is None:
            self.item = textItem("", self.position, 0, 1, self.scene, snap=self.a_snap, mode="plain")
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setPlainText(self.textField.toPlainText())

        br = self.item.boundingRect()
        self.item.setTransformOriginPoint(
            QtCore.QPointF(br.width() / 2, br.height() / 2)
        )

        self.item.update()
        global RAW
        RAW = True
        QtWidgets.QDialog.accept(self)


class textItemDialog(QtWidgets.QDialog):
    """ Dialog to input and add html formated text into the QGraphicsScene """
    def __init__(self, item=None, position=None, scene=None, parent=None, snap=None):
        super(textItemDialog, self).__init__(parent)

        self.item = item
        self.position = position
        self.scene = scene
        self.a_snap = snap

        self.resize(800, 400)
        self.setMinimumSize(780, 400)

        self.textField = textEditorWindow()
        editorLabel = QtWidgets.QLabel("&Text:")
        editorLabel.setBuddy(self.textField)

        self.fontComboBox = QtWidgets.QFontComboBox()
        self.fontComboBox.setCurrentFont(QtGui.QFont("Times", POINT_SIZE))
        fontLabel = QtWidgets.QLabel("&Font:")
        fontLabel.setBuddy(self.fontComboBox)

        self.fontSpinBox = QtWidgets.QSpinBox()
        self.fontSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.fontSpinBox.setRange(6, 280)
        self.fontSpinBox.setValue(POINT_SIZE)
        fontSizeLabel = QtWidgets.QLabel("&Size:")
        fontSizeLabel.setBuddy(self.fontSpinBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                    QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.textField.editor.setHtml(self.item.toHtml())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(editorLabel, alignment=QtCore.Qt.AlignLeft)

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addSpacing(40)
        layout1.addWidget(self.textField)
        layout.addLayout(layout1)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(fontLabel, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout2.addWidget(self.fontComboBox, alignment=QtCore.Qt.AlignRight, stretch=0)
        layout2.addSpacing(10)

        layout3 = QtWidgets.QHBoxLayout()
        layout3.addWidget(fontSizeLabel, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout3.addWidget(self.fontSpinBox, alignment=QtCore.Qt.AlignRight, stretch=1)
        layout2.addLayout(layout3)
        layout.addLayout(layout2)

        layout.addWidget(self.buttonBox, alignment=QtCore.Qt.AlignRight)

        self.connect(self.fontComboBox,
                     SIGNAL("currentFontChanged(QtGui.QFont())"), self.updateUi)
        self.connect(self.fontSpinBox,
                     SIGNAL("valueChanged(int)"), self.updateUi)
        self.connect(self.textField.editor, SIGNAL("textChanged()"),
                     self.updateUi)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)

        self.setWindowTitle("Page Designer - {} Text Item".format(
            "Add" if self.item is None else "Edit"))
        self.updateUi()

    def updateUi(self):
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.textField.editor.document().setDefaultFont(font)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(self.textField.editor.toPlainText()))

    def accept(self):
        if self.item is None:
            self.item = textItem("", self.position, 0, 1, self.scene, snap=self.a_snap, mode="html")
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setHtml(self.textField.editor.toHtml())

        br = self.item.boundingRect()
        self.item.setTransformOriginPoint(
            QtCore.QPointF(br.width() / 2, br.height() / 2)
        )

        self.item.update()
        global RAW
        RAW = True
        QtWidgets.QDialog.accept(self)