from PySide2 import QtWidgets, QtCore, QtGui

def hex2QColor(color):
    # TODO: use later somewhere else...
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return QtGui.QColor(r, g, b)


class itemPropBox(QtWidgets.QGroupBox):
    rotationChanged = QtCore.Signal(float)
    scaleChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super(itemPropBox, self).__init__(parent)

        self.setTitle("Properties")
        self.setFixedSize(200, 100)

        self.m_rotationSpinbox = QtWidgets.QDoubleSpinBox(
            minimum=-360, maximum=360
        )
        self.m_rotationSpinbox.valueChanged.connect(self.rotationChanged)

        self.m_scaleSpinBox = QtWidgets.QDoubleSpinBox(
            minimum=0, maximum=100, singleStep=0.1
        )
        self.m_scaleSpinBox.valueChanged.connect(self.scaleChanged)

        layout = QtWidgets.QFormLayout(self)
        layout.addRow("Rotation:", self.m_rotationSpinbox)
        layout.addRow("Scale:", self.m_scaleSpinBox)

    @property
    def rotation(self):
        return self.m_rotationSpinbox.value()

    @rotation.setter
    def rotation(self, value):
        self.m_rotationSpinbox.setValue(value)

    @property
    def scale(self):
        return self.m_scaleSpinBox.value()

    @scale.setter
    def scale(self, value):
        self.m_scaleSpinBox.setValue(value)
