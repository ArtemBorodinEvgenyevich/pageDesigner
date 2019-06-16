from src.actions.actions import *


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

        self.act_copy = actionCopy(self.p_scene, self.w_parent)
        self.act_paste = actionPaste(self.p_scene, self.w_parent)
        self.act_cut = actionCut(self.p_scene, self.w_parent)
        self.act_delete = actionDelete(self.p_scene, self.w_parent)
        self.act_selectAll = actionSelectAll(self.p_scene, self.w_parent)

        self.act_createText = actionCreateText(self.p_scene, self.a_pos, self.w_parent)
        self.act_createBox = actionCreateBox(self.p_scene, self.a_pos, self.w_parent)
        self.act_createPixmap = actionCreatePixmapItem(self.p_scene, self.a_pos, self.w_parent)

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

        snap = QtWidgets.QAction(self.w_parent)
        # snap.connect(SIGNAL("triggered()"), self.setSnap) TODO
        snap.setToolTip("Snap items to grid")
        snap.setIcon(QtGui.QIcon(os.path.join(APP_PATH, "stylesheets/toolbar/snap.svg")))
        self.addAction(snap)
        self.addSeparator()


class menuBar(QtWidgets.QMenuBar):
    def __init__(self, scene, parent=None):
        super(menuBar, self).__init__(parent)
        self.setObjectName("menuBar")

        self.p_scene = scene
        self.w_parent = parent

        self.fileMenu = QtWidgets.QMenu("&File", self)

        self.act_openFile = actionOpenFile(self.p_scene, self.w_parent)
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
