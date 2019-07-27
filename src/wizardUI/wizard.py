from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
import os, sys


if getattr(sys, "frozen", False):
    currentDir = os.path.join(sys._MEIPASS, "wizardUI")
else:
    currentDir = os.path.dirname(os.path.realpath(__file__))

class tutorWizard(QtWidgets.QWizard):
    """ Contains introduction tutorial """
    def __init__(self, parent=None):
        super(tutorWizard, self).__init__(parent)


        self.setWindowTitle("Introduction tutorial")
        pages = self.findPages()
        self.initPages(pages)

    def findPages(self):
        ui_files = []
        cnt = 1
        while len(ui_files) != 15:
            for file in os.listdir(currentDir):
                if file.startswith("{}.".format(cnt)):
                    ui_files.append(os.path.join(currentDir, file))
                    cnt += 1
        return ui_files

    def initPages(self, files):
        loader = QUiLoader()
        for i in files:
            file = QtCore.QFile(str(i))
            if file.open(QtCore.QFile.ReadOnly):
                page = loader.load(file)
                self.addPage(page)
