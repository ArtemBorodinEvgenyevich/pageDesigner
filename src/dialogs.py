import json
import os
from functools import partial

from PySide2 import QtCore, QtWidgets, QtGui


def getConfigs(path):
    with open(path + "/globalConfig.json", "r") as settings:
        data = json.load(settings)
    return data


parent_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
print(parent_path)

data = getConfigs(parent_path)  # TODO


class styleGUI(QtWidgets.QWidget):
    def __init__(self):
        super(styleGUI, self).__init__()

        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)

        frame = QtWidgets.QWidget()
        fLayout = QtWidgets.QVBoxLayout(frame)
        frame.setLayout(fLayout)

        for name, f_path, p_path in (
                ("Breeze Light", "/stylesheets/light.qss", "/stylesheets/styles_preview/light.png"),
                ("Breeze Dark", "/stylesheets/dark.qss", "/stylesheets/styles_preview/dark.png")):
            wrapper = partial(self.setData, f_path, p_path)
            radio = QtWidgets.QRadioButton()
            radio.setText(name)
            radio.setBaseSize(QtCore.QSize(100, 100))
            radio.clicked.connect(wrapper)
            fLayout.addWidget(radio)

        rect = QtWidgets.QApplication.desktop().availableGeometry()
        self.pixmap = QtGui.QPixmap(parent_path + data["stylesheet"]["pixmap"])
        self.preview = QtWidgets.QLabel()
        self.preview.setScaledContents(True)
        self.preview.setFixedSize(int(rect.width() * 0.3), int(rect.height() * 0.3))
        self.preview.setPixmap(self.pixmap)

        layout.addWidget(frame)
        layout.addWidget(self.preview)

    def setData(self, f_path, p_path):
        data["stylesheet"]["file"] = f_path
        data["stylesheet"]["pixmap"] = p_path

        with open(os.path.join(os.pardir, "globalConfig.json"), "w") as f:
            json.dump(data, f, indent=4)

        self.pixmap = QtGui.QPixmap(parent_path + p_path)
        self.preview.setPixmap(self.pixmap)
        global CONFIG_CHANGED
        CONFIG_CHANGED = True
        print("Done!")


class warningDialog(QtWidgets.QMessageBox):
    def __init__(self):
        super(warningDialog, self).__init__()

        self.setWindowTitle("Message Box")
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setText("Settings have been changed")
        self.setInformativeText("Restart the app to confirm the changes, please")
        self.checkBox = QtWidgets.QCheckBox("Do not show it again", self)
        self.checkBox.stateChanged.connect(self.clickBox)
        self.setCheckBox(self.checkBox)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.buttonClicked.connect(self.close)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            data["additional"]["message-box"] = False
            with open(os.path.join(parent_path, "globalConfig.json"), "w") as f:
                f = json.dump(data, f, indent=4)
        else:
            print("unchecked")


class baseConfig(QtWidgets.QWidget):
    def __init__(self):
        super(baseConfig, self).__init__()
        pass


class settingsGUI(QtWidgets.QDialog):
    def __init__(self):
        super(settingsGUI, self).__init__()

        rect = QtWidgets.QApplication.desktop().availableGeometry()
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
        if CONFIG_CHANGED is True and data["additional"]["message-box"] is True:
            dialog = warningDialog()
            dialog.exec_()
        self.close()
