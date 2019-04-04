import os
import sys

from PySide2 import QtWidgets

from src.pageDesigner import mainWindow

path = os.path.dirname(os.path.abspath(__file__))
print(path)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    style = QtWidgets.QStyleFactory.create('Fusion')
    app.setStyle(style)

    form = mainWindow(path)
    rect = QtWidgets.QApplication.desktop().availableGeometry()
    form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
    form.show()
    sys.exit(app.exec_())
