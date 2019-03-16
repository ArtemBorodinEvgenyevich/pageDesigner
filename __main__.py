from PySide2 import QtWidgets
import sys
from src.pageDesigner import mainForm

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = mainForm()
    rect = QtWidgets.QApplication.desktop().availableGeometry()
    form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
    form.show()
    app.exec_()