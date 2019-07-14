from PySide2 import QtCore, QtWidgets, QtGui
from src.widgets.dialogs import welcomeShow
from globals import APP_PATH
import fnmatch
import json
import os
import sys

# Import compiled .qrc files
# Separated to reduce size limits
from stylesheets import breeze_resources
from stylesheets import textdialogico
from stylesheets import preview
from stylesheets import toolbarico
from stylesheets import wizardpixmaps
from stylesheets import stylesheets
from stylesheets import licenseIco

def getConfigs():
    with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
        data = json.load(settings)
    return data


CONFIG_EXIST = False
CURRENT_CONFIG = ""

if __name__ == '__main__':

    for file in os.listdir(APP_PATH):
        if fnmatch.fnmatch(file, "globalConfig.json"):
            print("Config exist")
            CONFIG_EXIST = True
            with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as f:
                data = json.load(f)
                CURRENT_CONFIG = data

    if not CONFIG_EXIST:
        print("No config")
        data = {
            "stylesheet": {
                "file": "Fusion",
                "pixmap": ":/preview/styles_preview/fusion.png"
            },
            "undo-redo": {
                "list-len": 10
            },
            "common-path": {
                "pixmap": ".",
                "project": "."
            },
            "additional": {
                "message-box": True,
                "changed-settings": False,
                "startup-message": True
            }
        }
        CURRENT_CONFIG = data
        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as f:
            json.dump(data, f, indent=4)


    from src.pageDesigner import mainWindow


    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/logos/icon.png"))

    if CURRENT_CONFIG["stylesheet"]["file"] == 'Fusion':
        app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    elif CURRENT_CONFIG["stylesheet"]["file"] == 'Native':
        pass
    else:
        file = QtCore.QFile(CURRENT_CONFIG["stylesheet"]["file"])
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        app.setStyleSheet(stream.readAll())


    form = mainWindow()
    rect = QtWidgets.QApplication.desktop().availableGeometry()
    form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
    form.show()

    if CURRENT_CONFIG["additional"]["startup-message"]:
        widget = welcomeShow()
        widget.exec_()

    sys.exit(app.exec_())
