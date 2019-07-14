import json
import os
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from globals import APP_PATH, getConfigs
from src.widgets.buttons import setPathButton


class styleGUI(QtWidgets.QWidget):
    """ Tab element, contains GUI style controls """
    def __init__(self):
        super(styleGUI, self).__init__()

        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)

        frame = QtWidgets.QWidget()
        fLayout = QtWidgets.QVBoxLayout(frame)
        frame.setLayout(fLayout)

        for name, f_path, p_path in (
                ("Breeze Light", ":/styles/stylesheets/light.qss", ":/preview/styles_preview/light.png"),
                ("Breeze Dark", ":/styles/stylesheets/dark.qss", ":/preview/styles_preview/dark.png"),
                ("Fusion", "Fusion", ":/preview/styles_preview/fusion.png"),
                ("Native style", "Native", ":/preview/styles_preview/os_style.png")):

            wrapper = partial(self.setData, f_path, p_path)
            wrapper_pix = partial(self.setPix, p_path)

            radio = QtWidgets.QRadioButton()
            radio.setText(name)
            radio.setBaseSize(QtCore.QSize(100, 100))
            radio.clicked.connect(wrapper)
            radio.clicked.connect(wrapper_pix)
            radio.clicked.connect(self.setCheck)

            fLayout.addWidget(radio)

        rect = QtWidgets.QApplication.desktop().availableGeometry()

        CURRENT_CONFIG = getConfigs()

        self.pixmap = QtGui.QPixmap(CURRENT_CONFIG["stylesheet"]["pixmap"])
        self.preview = QtWidgets.QLabel()
        self.preview.setScaledContents(True)
        self.preview.setFixedSize(int(rect.width() * 0.3), int(rect.height() * 0.3))
        self.preview.setPixmap(self.pixmap)

        layout.addWidget(frame)
        layout.addWidget(self.preview)

    def setCheck(self):
        CURRENT_CONFIG = getConfigs()

        CURRENT_CONFIG["additional"]["changed-settings"] = True

        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(CURRENT_CONFIG, f, indent=4)

    def setData(self, f_path, p_path):
        CURRENT_CONFIG = getConfigs()

        CURRENT_CONFIG["stylesheet"]["file"] = f_path
        CURRENT_CONFIG["stylesheet"]["pixmap"] = p_path

        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(CURRENT_CONFIG, f, indent=4)

        self.pixmap = QtGui.QPixmap(os.path.join(APP_PATH, p_path))
        self.preview.setPixmap(self.pixmap)

    def setPix(self, p_path):
        newPixmap = QtGui.QPixmap(p_path)
        self.preview.setPixmap(newPixmap)


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
        CURRENT_CONFIG = getConfigs()

        if state == QtCore.Qt.Checked:
            CURRENT_CONFIG["additional"]["message-box"] = False
        else:
            CURRENT_CONFIG["additional"]["message-box"] = True

        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(CURRENT_CONFIG, f, indent=4)


class pathLineEdit(QtWidgets.QLineEdit):
    """ Text line to set path to a given config"""
    def __init__(self, configName, parent=None):
        super(pathLineEdit, self).__init__(parent)

        self.cName = configName

        self.setToolTip("Click twice, write or push button to setup path")

        CURRENT_CONFIG = getConfigs()
        self.setText(CURRENT_CONFIG["common-path"][self.cName])

        self.textChanged[str].connect(self.writeToConfig)
        self.textChanged.connect(self.setCheck)


    def setCheck(self):
        CURRENT_CONFIG = getConfigs()

        CURRENT_CONFIG["additional"]["changed-settings"] = True

        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(CURRENT_CONFIG, f, indent=4)


    def mouseDoubleClickEvent(self, event:QtGui.QMouseEvent):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select directory", ".", options=QtWidgets.QFileDialog.DontUseNativeDialog
        )
        if fname != self.text():
            self.setText(fname)
            self.writeToConfig(fname)

    def writeToConfig(self, path):
        CURRENT_CONFIG = getConfigs()

        if path != "":
            CURRENT_CONFIG["common-path"][self.cName] = path
            CURRENT_CONFIG["additional"]["changed-settings"] = True
        else:
            CURRENT_CONFIG["common-path"][self.cName] = "."
        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(CURRENT_CONFIG, f, indent=4)


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
    """ Tab element, contains paths information """
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