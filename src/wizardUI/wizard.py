from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
import sys, os


class tutorWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(tutorWizard, self).__init__(parent)

        self.setWindowTitle("Introduction tutorial")
        pages = self.findPages()
        self.initPages(pages)

    def findPages(self):
        ui_files = []
        cnt = 1
        current_dir = os.path.dirname(os.path.realpath(__file__))
        while len(ui_files) != 13:
            for file in os.listdir(current_dir):
                if file.startswith(f"{cnt}."):
                    ui_files.append(os.path.join(current_dir, file))
                    cnt += 1
        return ui_files

    def initPages(self, files):
        loader = QUiLoader()
        for i in files:
            file = QtCore.QFile(str(i))
            file.open(QtCore.QFile.ReadOnly)

            # As I have read from "https://stackoverflow.com/a/18654247/10171242"
            # Calling reset() before loading .ui file might cure the problem.
            # Anyway, it doesn't work in my case.
            file.reset()
            page = loader.load(file)

            file.close()

            self.addPage(page)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = tutorWizard()
    window.show()
    sys.exit(app.exec_())