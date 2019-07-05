import random

from src.actions.actions import *
from src.graphics import graphicsView, graphicsScene
from src.widgets.Buttons import controlButton
from src.widgets.propertyBox import itemPropBox
from src.widgets.Buttons import snapButton

QWIDGETSIZE_MAX = (1 << 24) - 1

class statusBar(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super(statusBar, self).__init__(parent)
        self.setObjectName('statusBar')


class toolBox(QtWidgets.QToolBar):
    def __init__(self, scene, view, position, parent=None):
        super(toolBox, self).__init__(parent)

        self.setObjectName('toolBox')
        self.setMinimumHeight(40)

        self.w_parent = parent  # pointer to the parent widget
        self.a_pos = position  # pointer to the QGraphicsView mouse position function
        self.p_scene = scene  # pointer to the QGraphicsScene object
        self.p_view = view  # pointer to the QGraphicsView object

        self.snap = snapButton(self.p_scene, self)

        self.act_copy = actionCopy(self.p_scene, self.w_parent)
        self.act_paste = actionPaste(self.p_scene, self.w_parent, self.snap)
        self.act_cut = actionCut(self.p_scene, self.w_parent)
        self.act_delete = actionDelete(self.p_scene, self.w_parent)
        self.act_selectAll = actionSelectAll(self.p_scene, self.w_parent)

        self.act_createText = actionCreateText(self.p_scene, self.a_pos, self.w_parent, self.snap)
        self.act_createBox = actionCreateBox(self.p_scene, self.a_pos, self.w_parent, self.snap)
        self.act_createPixmap = actionCreatePixmapItem(self.p_scene, self.a_pos, self.w_parent, self.snap)

        MAC = "qt_mac_set_native_menubar" in dir()
        if not MAC:
            self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.addAction(self.act_createText)
        self.addAction(self.act_createBox)
        self.addAction(self.act_createPixmap)

        # Add editing functions
        self.addAction(self.act_copy)
        self.addAction(self.act_paste)
        self.addAction(self.act_cut)
        self.addAction(self.act_delete)

        self.addSeparator()

        self.addWidget(self.snap)


class menuBar(QtWidgets.QMenuBar):
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

        self.addMenu(self.fileMenu)
        self.addMenu(self.editMenu)


class centralWidget(QtWidgets.QWidget):

    def __init__(self, printerSupport, parent=None):
        super(centralWidget, self).__init__(parent)

        self.printer = printerSupport

        self.filename = ""
        self.copiedItems = QtCore.QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QtCore.QPoint()
        self.addOffset = 5
        self.borders = []

        self.scene =  graphicsScene()
        #TODO different sizes

        self.view = graphicsView(self.scene, self)

        self.propPanel = controllWidget(self.view)

        self.controlButton = controlButton(self)

        layoutBtn = QtWidgets.QVBoxLayout()
        layoutBtn.addWidget(self.controlButton)


        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.view, 10)
        layout.addSpacing(5)
        layout.addLayout(layoutBtn)
        layout.setSpacing(0)
        layout.addWidget(self.propPanel)


        self.m_deltaX = 0
        self.m_animation = QtCore.QPropertyAnimation(
            self.propPanel, b"maximumWidth", parent=self, duration=200
        )

    def position(self):
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
        if self.controlButton.isChecked():
            self.propPanel.setMaximumWidth(self.propPanel.width())
            start = int(self.propPanel.maximumWidth())
            self.m_deltaX = start
            end = 0
            self.m_animation.setStartValue(start)
            self.m_animation.setEndValue(end)
            self.controlButton.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/buttons/openPanel.svg")))
        else:
            start = int(self.propPanel.maximumWidth())
            end = self.m_deltaX
            self.m_animation.setStartValue(start)
            self.m_animation.setEndValue(end)
            self.controlButton.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/buttons/collapsePanel.svg")))

        self.m_animation.start()

    def resizeEvent(self, event: "QResizeEvent"):
        if not self.controlButton.isChecked():
            self.propPanel.setMaximumWidth(QWIDGETSIZE_MAX)

class controllWidget(QtWidgets.QWidget):
    def __init__(self, view, parent=None):
        super(controllWidget, self).__init__(parent)

        self.view = view
        self.view.currentItemChanged.connect(self.onCurrentItemChanged)

        self.propBox = itemPropBox()
        self.propBox.rotationChanged.connect(self.onRotationChanged)
        self.propBox.scaleChanged.connect(self.onScaleChanged)
        self.propBox.hide()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self.propBox)

    @QtCore.Slot(QtWidgets.QGraphicsItem)
    def onCurrentItemChanged(self, item):
        self.propBox.setVisible(item is not None)
        if item is not None:
            self.propBox.rotation = item.rotation()
            self.propBox.scale = item.scale()

    @QtCore.Slot(float)
    def onRotationChanged(self, rotation):
        it = self.view.currentItem
        it.setRotation(rotation)

    @QtCore.Slot(float)
    def onScaleChanged(self, scale):
        it = self.view.currentItem
        it.setScale(scale)
