import json
import os

from PySide2 import QtCore, QtWidgets
from globals import APP_PATH, CONFIG_CHANGED
from src.widgets.settings import styleGUI, warningDialog, baseConfig


def getConfigs():
    with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
        data = json.load(settings)
    return data

data = getConfigs()


class settingsGUI(QtWidgets.QDialog):
    def __init__(self):
        super(settingsGUI, self).__init__()

        rect = QtWidgets.QApplication.desktop().availableGeometry()
        self.setWindowTitle("App configuration")
        self.resize(int(rect.width() * 0.6), int(rect.height() * 0.5))


        layout = QtWidgets.QVBoxLayout(self)
        mainWidget = QtWidgets.QTabWidget()
        layout.addWidget(mainWidget)

        styleTab = styleGUI()
        appConfigTab = baseConfig()

        mainWidget.addTab(appConfigTab, "Set Base Configuration")
        mainWidget.addTab(styleTab, "Set Style")

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok,
                                                    QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttonBox)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.closeWindow)

    def closeWindow(self):
        global CONFIG_CHANGED
        if CONFIG_CHANGED is True and data["additional"]["message-box"] is True:
            dialog = warningDialog()
            dialog.exec_()
        self.close()

