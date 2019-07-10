import os

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import SIGNAL

from globals import APP_PATH


class controlButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(controlButton, self).__init__(parent)

        self.setFixedSize(25, 500)
        self.setCheckable(True)
        self.connect(SIGNAL("clicked()"), parent.slideWidget)
        self.setShortcut("Q")

        self.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/buttons/collapsePanel.svg")))
        self.setStyleSheet("background-color: transparent;"
                           "border: none;")

class snapButton(QtWidgets.QToolButton):
    currentStateChanged = QtCore.Signal(bool)
    def __init__(self, scene, gridBox=None, parent=None):
        super(snapButton, self).__init__(parent)

        self.setCheckable(True)
        self.setShortcut("Ctrl+U")
        self.setToolTip("Enable grid snapping")
        self.setIcon(QtGui.QIcon("stylesheets/toolbar/snap.svg"))

        self.p_scene = scene

        self.childWidget = gridBox

        self.clicked.connect(self.p_scene.snap)
        self.clicked.connect(self.setState)

    def setState(self):
        if self.isChecked():
            self.childWidget.setVisible(True)
            self.childWidget.gridDensity_X = self.p_scene.gridDensity_X
            self.childWidget.gridDensity_Y = self.p_scene.gridDensity_Y
            self.childWidget.opacity = self.p_scene.lines[0].opacity()
        else:
            self.childWidget.setVisible(False)


class setPathButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(setPathButton, self).__init__(parent)

        self.a_parent = parent

        self.setText("...")
        self.setToolTip("Click to choose folder")
        self.setFixedWidth(30)

        self.clicked.connect(self.writeToConfig)

    def writeToConfig(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select directory", ".", options=QtWidgets.QFileDialog.DontUseNativeDialog
        )
        if fname != "":
            self.a_parent.setText(fname)
        else:
            self.a_parent.setText(".")