import json
import os

from PySide2 import QtCore, QtWidgets
from globals import APP_PATH, getConfigs
from src.widgets.settings import styleGUI, warningDialog, baseConfig
from src.wizardUI.wizard import tutorWizard


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
        CURRENT_CONFIG = getConfigs()

        if CURRENT_CONFIG["additional"]["changed-settings"]:
            CURRENT_CONFIG["additional"]["changed-settings"] = False

            with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
                print(os.path.join(APP_PATH, "globalConfig.json"))
                json.dump(CURRENT_CONFIG, f, indent=4)

            if CURRENT_CONFIG["additional"]["message-box"]:
                dialog = warningDialog()
                dialog.exec_()

        self.close()


class welcomeShow(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(welcomeShow, self).__init__(parent)

        self.setWindowTitle("Message Box")
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setText("Welcome to Page Designer")
        self.setInformativeText("We recommend you to take a tutorial which covers "
                                "basics you need to know before you start. "
                                "You can always open it again in any time from the \"Help\" menu."
                                "Would you like to continue?")
        self.checkBox = QtWidgets.QCheckBox("Do not show it again", self)
        self.checkBox.stateChanged.connect(self.clickBox)
        self.setCheckBox(self.checkBox)

        self.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        self.buttonClicked.connect(self.sortBtn)

    def clickBox(self, state):
        CURRENT_CONFIG = getConfigs()

        if state == QtCore.Qt.Checked:
            CURRENT_CONFIG["additional"]["startup-message"] = False
            with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
                json.dump(CURRENT_CONFIG, f, indent=4)
        elif state == QtCore.Qt.Unchecked:
            CURRENT_CONFIG["additional"]["startup-message"] = True
            with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
                json.dump(CURRENT_CONFIG, f, indent=4)

    def sortBtn(self, i):
        if i is self.button(QtWidgets.QMessageBox.Ok):
            self.showTutor()

    def showTutor(self):
        dialog = tutorWizard()
        dialog.exec_()
        self.close()
