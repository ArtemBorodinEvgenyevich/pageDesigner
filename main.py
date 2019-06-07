import fnmatch
import json
import os
import sys

from PySide2 import QtCore
from PySide2 import QtWidgets


from globals import CONFIG_EXIST, APP_PATH
from stylesheets import breeze_resources

print(os.getcwd())


if __name__ == '__main__':

    for file in os.listdir(os.pardir):
        if fnmatch.fnmatch(file, "globalConfig.json"):
            print("Config exist")
            CONFIG_EXIST = True
            with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
                data = json.load(settings)
            global CURRENT_CONFIG
            CURRENT_CONFIG = data

    if not CONFIG_EXIST:
        print("No config")
        data = {
            "stylesheet": {
                "file": "stylesheets/light.qss",
                "pixmap": "stylesheets/styles_preview/light.png"
            },
            "undo-redo": {
                "list-len": 10
            },
            "additional": {
                "message-box": True
            }
        }
        with open(os.path.join(APP_PATH, "globalConfig.json"), "w") as settings:
            json.dump(data, settings, indent=4)

    from src.pageDesigner import mainWindow

    #print(data["stylesheets"])

    app = QtWidgets.QApplication(sys.argv)

    # style = QtWidgets.QStyleFactory.create('Fusion')
    # app.setStyle(style)

    file = QtCore.QFile(os.path.join(APP_PATH, data["stylesheet"]["file"]))
    file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    stream = QtCore.QTextStream(file)
    app.setStyleSheet(stream.readAll())

    form = mainWindow()
    rect = QtWidgets.QApplication.desktop().availableGeometry()
    form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
    form.show()
    sys.exit(app.exec_())