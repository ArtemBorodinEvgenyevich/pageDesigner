import json
import os
from functools import partial

from PySide2 import QtWidgets, QtCore, QtGui

from globals import APP_PATH, CONFIG_CHANGED
from src.widgets.Buttons import setPathButton


def getConfigs():
    with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
        data = json.load(settings)
    return data

data = getConfigs()

class styleGUI(QtWidgets.QWidget):
    def __init__(self):
        super(styleGUI, self).__init__()

        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)

        frame = QtWidgets.QWidget()
        fLayout = QtWidgets.QVBoxLayout(frame)
        frame.setLayout(fLayout)

        for name, f_path, p_path in (
                ("Breeze Light", "stylesheets/light.qss", "stylesheets/styles_preview/light.png"),
                ("Breeze Dark", "stylesheets/dark.qss", "stylesheets/styles_preview/dark.png")):
            wrapper = partial(self.setData, f_path, p_path)
            radio = QtWidgets.QRadioButton()
            radio.setText(name)
            radio.setBaseSize(QtCore.QSize(100, 100))
            radio.clicked.connect(wrapper)
            fLayout.addWidget(radio)

        rect = QtWidgets.QApplication.desktop().availableGeometry()
        self.pixmap = QtGui.QPixmap(os.path.join(APP_PATH, data["stylesheet"]["pixmap"]))
        self.preview = QtWidgets.QLabel()
        self.preview.setScaledContents(True)
        self.preview.setFixedSize(int(rect.width() * 0.3), int(rect.height() * 0.3))
        self.preview.setPixmap(self.pixmap)

        layout.addWidget(frame)
        layout.addWidget(self.preview)

    def setData(self, f_path, p_path):
        data["stylesheet"]["file"] = f_path
        data["stylesheet"]["pixmap"] = p_path

        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(data, f, indent=4)

        self.pixmap = QtGui.QPixmap(os.path.join(APP_PATH, p_path))
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
            with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
                json.dump(data, f, indent=4)
        else:
            print("unchecked")


class pathLineEdit(QtWidgets.QLineEdit):
    def __init__(self, configName, parent=None):
        super(pathLineEdit, self).__init__(parent)

        self.cName = configName

        self.setToolTip(f"Click twice, write or push button to setup path")
        self.setText(data["common-path"][self.cName])

        self.textChanged[str].connect(self.writeToConfig)


    def mouseDoubleClickEvent(self, event:QtGui.QMouseEvent):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select directory", ".", options=QtWidgets.QFileDialog.DontUseNativeDialog
        )
        if fname != self.text():
            self.setText(fname)
            self.writeToConfig(fname)

    def writeToConfig(self, path):
        if path != "":
            data["common-path"][self.cName] = path
        else:
            data["common-path"][self.cName] = "."
        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(data, f, indent=4)


class groupWidget(QtWidgets.QWidget):
    """Local widget to group line edit and assign button in one layout"""
    def __init__(self, widget1, widget2, text="row1", parent=None):
        super(groupWidget, self).__init__(parent)

        self.label = QtWidgets.QLabel(text)

        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.label)
        layout.addSpacing(20)
        layout.addWidget(widget1)
        layout.addWidget(widget2)


class baseConfig(QtWidgets.QWidget):
    def __init__(self):
        super(baseConfig, self).__init__()

        layout = QtWidgets.QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        self.pixmapP_edit = pathLineEdit("pixmap")
        self.pixmapP_btn = setPathButton(self.pixmapP_edit)
        row1 = groupWidget(self.pixmapP_edit, self.pixmapP_btn, "Select pixmap folder path:", self)
        layout.addRow(row1)

        self.projectP_edit = pathLineEdit("project")
        self.projectP_btn = setPathButton(self.projectP_edit)
        row2 = groupWidget(self.projectP_edit, self.projectP_btn, "Select project folder path:", self)
        layout.addRow(row2)