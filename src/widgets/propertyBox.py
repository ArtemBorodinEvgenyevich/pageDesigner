from PySide2 import QtWidgets, QtCore, QtGui

def hex2QColor(color):
    # TODO: use later somewhere else...
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return QtGui.QColor(r, g, b)

class labelBox(QtWidgets.QGroupBox):
    def __init__(self, text, parent=None):
        super(labelBox, self).__init__(parent)

        self.setFixedSize(200, 50)
        self.label = QtWidgets.QLabel(text)

        label_layout = QtWidgets.QHBoxLayout(self)
        label_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(label_layout)

        label_layout.addWidget(self.label)


class itemPropBox(QtWidgets.QGroupBox):
    rotationChanged = QtCore.Signal(float)
    scaleChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super(itemPropBox, self).__init__(parent)

        self.setTitle("Item properties")
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


class gridPropBox(QtWidgets.QGroupBox):
    densityX_Changed = QtCore.Signal(int)
    densityY_Changed = QtCore.Signal(int)
    opacityChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super(gridPropBox, self).__init__(parent)

        self.setTitle("Grid properties")
        self.setFixedSize(200, 120)

        self.m_gridDensityX_SpinBox = QtWidgets.QSpinBox(
            minimum=1, maximum=500, singleStep=1
        )
        self.m_gridDensityX_SpinBox.valueChanged.connect(self.densityX_Changed)

        self.m_gridDensityY_SpinBox = QtWidgets.QSpinBox(
            minimum=1, maximum=500, singleStep=1
        )
        self.m_gridDensityY_SpinBox.valueChanged.connect(self.densityY_Changed)

        self.m_gridOpacity_SpinBox = QtWidgets.QDoubleSpinBox(
            minimum=0, maximum=1, singleStep=0.05
        )
        self.m_gridOpacity_SpinBox.valueChanged.connect(self.opacityChanged)

        layout = QtWidgets.QFormLayout(self)
        layout.addRow("Density X:", self.m_gridDensityX_SpinBox)
        layout.addRow("Density Y:", self.m_gridDensityY_SpinBox)
        layout.addRow("Opacity:", self.m_gridOpacity_SpinBox)

    @property
    def gridDensity_X(self):
        return self.m_gridDensityX_SpinBox.value()

    @gridDensity_X.setter
    def gridDensity_X(self, value):
        return self.m_gridDensityX_SpinBox.setValue(value)

    @property
    def gridDensity_Y(self):
        return self.m_gridDensityY_SpinBox.value()

    @gridDensity_Y.setter
    def gridDensity_Y(self, value):
        return self.m_gridDensityY_SpinBox.setValue(value)

    @property
    def opacity(self):
        return self.m_gridOpacity_SpinBox.value()

    @opacity.setter
    def opacity(self, value):
        return self.m_gridOpacity_SpinBox.setValue(value)
