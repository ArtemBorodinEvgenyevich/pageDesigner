import os

from PySide2 import QtWidgets, QtGui
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

