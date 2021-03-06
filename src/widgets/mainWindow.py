import random

from src.actions.actions import *
from src.widgets.graphics import graphicsView, graphicsScene
from src.widgets.buttons import controlButton
from src.widgets.propertyBox import itemPropBox, gridPropBox, labelBox


QWIDGETSIZE_MAX = (1 << 24) - 1


class statusBar(QtWidgets.QStatusBar):      # FIXME: add signals to statusbar in each QAction subclass
    """ Indicates action status """
    def __init__(self, parent=None):
        super(statusBar, self).__init__(parent)
        self.setObjectName('statusBar')


class toolBox(QtWidgets.QToolBar):
    """ Contains QGraphicsScene editing functions """
    def __init__(self, scene, view, position, parent=None, snap=None):
        super(toolBox, self).__init__(parent)

        self.setObjectName('toolBox')
        self.setMinimumHeight(40)

        self.w_parent = parent  # pointer to the parent widget
        self.a_pos = position  # pointer to the QGraphicsView mouse position function
        self.p_scene = scene  # pointer to the QGraphicsScene object
        self.p_view = view  # pointer to the QGraphicsView object

        self.snap = snap
        self.textBtn = textTool(self.p_scene, self.a_pos, self.w_parent, self.snap)

        self.act_copy = actionCopy(self.p_scene, self.w_parent)
        self.act_paste = actionPaste(self.p_scene, self.w_parent, self.snap)
        self.act_cut = actionCut(self.p_scene, self.w_parent)
        self.act_delete = actionDelete(self.p_scene, self.w_parent)
        self.act_selectAll = actionSelectAll(self.p_scene, self.w_parent)

        self.act_createBox = actionCreateBox(self.p_scene, self.a_pos, self.w_parent, self.snap)
        self.act_createPixmap = actionCreatePixmapItem(self.p_scene, self.a_pos, self.w_parent, self.snap)

        # focus policy for macOS users      FIXME: test and remove if necessary
        MAC = "qt_mac_set_native_menubar" in dir()
        if not MAC:
            self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Add geometry functions
        self.addWidget(self.textBtn)
        self.addAction(self.act_createBox)
        self.addAction(self.act_createPixmap)
        self.addSeparator()

        # Add editing functions
        self.addAction(self.act_copy)
        self.addAction(self.act_paste)
        self.addAction(self.act_cut)
        self.addAction(self.act_delete)

        self.addSeparator()


class menuBar(QtWidgets.QMenuBar):
    """ Contains file manipulating functions """
    def __init__(self, scene, parent=None, snap=None):
        super(menuBar, self).__init__(parent)
        self.setObjectName("menuBar")

        self.p_scene = scene
        self.w_parent = parent
        self.a_snap = snap

        self.fileMenu = QtWidgets.QMenu("&File", self)

        self.act_openFile = actionOpenFile(self.p_scene, self.w_parent, self.a_snap)
        self.act_saveFile = actionSaveFile(self.p_scene, self.w_parent)
        self.act_printFile = actionPrintFile(self.p_scene, self.w_parent)
        self.act_quitApp = actionQuitApp(self.p_scene, self.w_parent)

        self.fileMenu.addAction(self.act_openFile)
        self.fileMenu.addAction(self.act_saveFile)
        self.fileMenu.addAction(self.act_printFile)
        self.fileMenu.addAction(self.act_quitApp)

        self.editMenu = QtWidgets.QMenu("&Edit", self)
        self.act_openSettings_GUI = actionOpenSettings_GUI(self.w_parent)
        self.editMenu.addAction(self.act_openSettings_GUI)

        self.helpMenu = QtWidgets.QMenu("&Help", self)
        self.act_openTutor = actionOpenTutor(self.w_parent)
        self.act_openLicense = actionOpenLicense(self.w_parent)
        self.helpMenu.addAction(self.act_openTutor)
        self.helpMenu.addAction(self.act_openLicense)

        self.addMenu(self.fileMenu)
        self.addMenu(self.editMenu)
        self.addMenu(self.helpMenu)


class centralWidget(QtWidgets.QWidget):
    """ Contains QGaphicsScene subclass with property frame """
    def __init__(self, printerSupport, parent=None):
        super(centralWidget, self).__init__(parent)

        self.printer = printerSupport

        self.filename = ""
        self.copiedItems = QtCore.QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QtCore.QPoint()
        self.addOffset = 5
        self.borders = []

        self.scene = graphicsScene()        # TODO: make different sizes

        self.view = graphicsView(self.scene, self)

        self.propPanel = controllWidget(self.view, self.scene)

        self.controlButton = controlButton(self)

        layoutBtn = QtWidgets.QVBoxLayout()
        layoutBtn.addWidget(self.controlButton)


        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.view, 10)
        layout.addSpacing(5)
        layout.addLayout(layoutBtn)
        layout.setSpacing(0)
        layout.addWidget(self.propPanel)

        # define parameters for property frame animation
        self.m_deltaX = 0
        self.m_animation = QtCore.QPropertyAnimation(
            self.propPanel, b"maximumWidth", parent=self, duration=200
        )

    def position(self):
        """ Get mouse position """

        point = self.mapFromGlobal(QtGui.QCursor.pos())
        if not self.view.geometry().contains(point):
            coord = random.randint(36, 144)
            point = QtCore.QPoint(coord, coord)
        else:
            if point == self.prevPoint:
                point += QtCore.QPoint(self.addOffset, self.addOffset)
                self.addOffset += 5
            else:
                self.addOffset = 5
                self.prevPoint = point
        return self.view.mapToScene(point)

    def addBorders(self):
        self.borders = []
        rect = QtCore.QRectF(0, 0, PAGE_SIZE[0], PAGE_SIZE[1])
        border1 = self.scene.addRect(
            rect, QtGui.QPen(), QtGui.QBrush(QtCore.Qt.lightGray)
        )
        border1.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        border1.setZValue(-3)

        margin = 5.25 * POINT_SIZE

        border2 = self.scene.addRect(
            rect.adjusted(margin, margin, -margin, -margin), QtGui.QPen(), QtGui.QBrush(QtCore.Qt.white)
        )
        border2.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        border2.setZValue(-2)

        self.borders.append(border1)
        self.borders.append(border2)

    def slideWidget(self):
        """ Animates property frame"""

        if self.controlButton.isChecked():
            self.propPanel.setMaximumWidth(self.propPanel.width())
            start = int(self.propPanel.maximumWidth())
            self.m_deltaX = start
            end = 0
            self.m_animation.setStartValue(start)
            self.m_animation.setEndValue(end)
            self.controlButton.setIcon(QtGui.QIcon(":/icons/buttons/openPanel.svg"))
        else:
            start = int(self.propPanel.maximumWidth())
            end = self.m_deltaX
            self.m_animation.setStartValue(start)
            self.m_animation.setEndValue(end)
            self.controlButton.setIcon(QtGui.QIcon(":/icons/buttons/collapsePanel.svg"))

        self.m_animation.start()

    def resizeEvent(self, event: "QResizeEvent"):
        if not self.controlButton.isChecked():
            self.propPanel.setMaximumWidth(QWIDGETSIZE_MAX)


class controllWidget(QtWidgets.QFrame):
    """ Contains QGraphicsItem editable properties """
    def __init__(self, view, scene, parent=None):
        super(controllWidget, self).__init__(parent)

        self.view = view
        self.view.currentItemChanged.connect(self.onCurrentItemChanged)
        self.scene = scene

        # Setting unique name to setup css frame not inherited by widgets' children
        self.setObjectName("controlFrame")
        self.setStyleSheet("#controlFrame {border:1px solid grey;}")

        self.label = labelBox("Property box")

        self.propBox = itemPropBox()
        self.propBox.rotationChanged.connect(self.onRotationChanged)
        self.propBox.scaleChanged.connect(self.onScaleChanged)
        self.propBox.hide()

        self.gridPropBox = gridPropBox()
        self.gridPropBox.densityX_Changed.connect(self.onDensityX_Changed)
        self.gridPropBox.densityY_Changed.connect(self.onDensityY_Changed)
        self.gridPropBox.opacityChanged.connect(self.onOpacity_Changed)
        self.gridPropBox.hide()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        layout.addWidget(self.label)
        layout.addWidget(self.propBox)
        layout.addWidget(self.gridPropBox)

    @QtCore.Slot(QtWidgets.QGraphicsItem)
    def onCurrentItemChanged(self, item):
        self.propBox.setVisible(item is not None)
        if item is not None:
            self.propBox.rotation = item.rotation()
            self.propBox.scale = item.scale()

    @QtCore.Slot(bool)
    def onCurrentStateChanged(self, state):
        self.gridPropBox.setVisible(state)
        if state:
            self.gridPropBox.gridDensity_X = self.scene.gridDensity_X
            self.gridPropBox.gridDensity_Y = self.scene.gridDensity_Y
            self.gridPropBox.opacity = self.scene.lines[0].opacity()

    @QtCore.Slot(float)
    def onRotationChanged(self, rotation):
        it = self.view.currentItem
        it.setRotation(rotation)

    @QtCore.Slot(float)
    def onScaleChanged(self, scale):
        it = self.view.currentItem
        it.setScale(scale)

    @QtCore.Slot(int)
    def onDensityX_Changed(self, value):
        self.scene.gridDensity_X = value
        self.scene.snap()
        self.scene.snap()

    @QtCore.Slot(int)
    def onDensityY_Changed(self, value):
        self.scene.gridDensity_Y = value
        self.scene.snap()
        self.scene.snap()

    @QtCore.Slot(float)
    def onOpacity_Changed(self, value):
        lines = self.scene.lines
        for i in lines:
            i.setOpacity(value)


class textTool(QtWidgets.QToolButton):      # FIXME: solve cyclic imports and move to buttons.py
    """ Contains dialogs to add different types of QGraphicsTextItems """
    def __init__(self, scene, pos, parent, snap):
        super(textTool, self).__init__(parent)

        self.setIcon(QtGui.QIcon(":/icons/toolbar/addText.svg"))
        self.setShortcut("Ctrl+T")
        self.setToolTip("Create text item")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.act_createCode = actionCreateCodeSnippet(scene, pos, parent, snap)
        self.act_createText = actionCreateText(scene, pos, parent, snap)

        menu = QtWidgets.QMenu(self)
        menu.addAction(self.act_createText)
        menu.addAction(self.act_createCode)
        self.setMenu(menu)
