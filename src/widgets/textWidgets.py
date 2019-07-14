from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import SIGNAL
from globals import POINT_SIZE
from time import strftime
import re


class textEditorWindow(QtWidgets.QMainWindow):
    """ Window to input html formatted text """
    def __init__(self, parent=None):
        super(textEditorWindow, self).__init__(parent)

        self.editor = QtWidgets.QTextEdit()
        doc = QtGui.QTextDocument()
        doc.setTextWidth(1)
        self.editor.setDocument(doc)
        self.setCentralWidget(self.editor)

        self.toolBar = editorToolBar(self.editor)
        self.addToolBar(self.toolBar)


class editorToolBar(QtWidgets.QToolBar):
    """ Contains html text format functions """
    def __init__(self, parent=None):
        super(editorToolBar, self).__init__(parent)

        self.setMovable(False)

        act_insertBList = actionInsertBulletList(parent)
        act_insertDList = actionInsertDigitList(parent)
        act_insertDT = actionInsertDateTime(parent)
        act_insertTable = actionInsertTable(parent)
        act_findText = actionFind(parent)
        act_makeBold = actionMakeBold(parent)
        act_makeItalic = actionMakeItalic(parent)
        act_makeUnderline = actionMakeUnderline(parent)
        act_makeStrike = actionMakeStrike(parent)
        act_makeSuperscript = actionMakeSuperscript(parent)
        act_makeSubscript = actionMakeSubscript(parent)
        act_alignLeft = actionAlignLeft(parent)
        act_alignCenter = actionAlignCenter(parent)
        act_alignJustify = actionAlignJustify(parent)
        act_alignRight = actionAlignRight(parent)
        act_indentArea = actionIndentArea(parent)
        act_dedentArea = actionDedentArea(parent)

        self.addAction(act_insertBList)
        self.addAction(act_insertDList)
        self.addAction(act_insertDT)
        self.addAction(act_insertTable)
        self.addAction(act_findText)
        self.addAction(act_makeBold)
        self.addAction(act_makeItalic)
        self.addAction(act_makeUnderline)
        self.addAction(act_makeStrike)
        self.addAction(act_makeSuperscript)
        self.addAction(act_makeSubscript)
        self.addAction(act_alignLeft)
        self.addAction(act_alignCenter)
        self.addAction(act_alignJustify)
        self.addAction(act_alignRight)
        self.addAction(act_indentArea)
        self.addAction(act_dedentArea)


class codeEditor(QtWidgets.QPlainTextEdit):
    """ Window to input plain formatted text """
    def __init__(self, parent=None):
        super(codeEditor, self).__init__(parent)

        self.doc = QtGui.QTextDocument()
        self.docLayout = QtWidgets.QPlainTextDocumentLayout(self.doc)
        self.doc.setDocumentLayout(self.docLayout)
        self.setDocument(self.doc)

        self.lineNumberArea = lineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth()

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            lineColor = QtGui.QColor(61, 174, 230, 50)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), QtGui.QColor(116, 128, 139))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


class lineNumberArea(QtWidgets.QWidget):
    """ Code editor area to draw line numbers """
    def __init__(self, parent=None):
        super(lineNumberArea, self).__init__(parent)
        self.w_parent = parent

    def sizeHint(self):
        return QtCore.QSize(self.w_parent.lineNumberAreaWidth(), 0)

    def paintEvent(self, event:QtGui.QPaintEvent):
        self.w_parent.lineNumberAreaPaintEvent(event)


class dateTime(QtWidgets.QDialog):
    """ Dialog to insert current date and time """
    def __init__(self, parent=None):
        super(dateTime, self).__init__(parent)

        self.w_parent = parent
        self.formats = ["%A, %d. %B %Y %H:%M",
                        "%A, %d. %B %Y",
                        "%d. %B %Y %H:%M",
                        "%d.%m.%Y %H:%M",
                        "%d. %B %Y",
                        "%d %m %Y",
                        "%d.%m.%Y",
                        "%x",
                        "%X",
                        "%H:%M"]

        self.box = QtWidgets.QComboBox(self)

        for i in self.formats:
            self.box.addItem(strftime(i))

        insert = QtWidgets.QPushButton("Insert", self)
        insert.clicked.connect(self.insert)

        cancel = QtWidgets.QPushButton("Cancel", self)
        cancel.clicked.connect(self.close)

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.box, 0, 0, 1, 2)
        layout.addWidget(insert, 1, 0)
        layout.addWidget(cancel, 1, 1)

        self.setGeometry(300, 300, 400, 80)
        self.setWindowTitle("Date and time")

    def insert(self):
        cursor = self.w_parent.textCursor()
        date_time = strftime(self.formats[self.box.currentIndex()])
        cursor.insertText(date_time)
        self.close()


class textTable(QtWidgets.QDialog):
    """ Dialog to insert table """
    def __init__(self, parent=None):
        super(textTable, self).__init__(parent)

        self.w_parent = parent

        rowLabel = QtWidgets.QLabel("Rows: ", self)
        self.rows = QtWidgets.QSpinBox(self)

        columnLabel = QtWidgets.QLabel("Columns: ", self)
        self.columns = QtWidgets.QSpinBox(self)

        spaceLabel = QtWidgets.QLabel("Cell spacing", self)
        self.space = QtWidgets.QSpinBox(self)

        padLabel = QtWidgets.QLabel("Cell padding", self)
        self.pad = QtWidgets.QSpinBox(self)
        self.pad.setValue(10)

        insertButton = QtWidgets.QPushButton("Insert", self)
        insertButton.clicked.connect(self.insert)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(rowLabel, 0, 0)
        layout.addWidget(self.rows, 0, 1)

        layout.addWidget(columnLabel, 1, 0)
        layout.addWidget(self.columns, 1, 1)

        layout.addWidget(padLabel, 2, 0)
        layout.addWidget(self.pad, 2, 1)

        layout.addWidget(spaceLabel, 3, 0)
        layout.addWidget(self.space, 3, 1)

        layout.addWidget(insertButton, 4, 0, 1, 2)

        self.setWindowTitle("Insert Table")
        self.setGeometry(300, 300, 200, 100)
        self.setLayout(layout)

    def insert(self):
        cursor = self.w_parent.textCursor()

        rows = self.rows.value()
        columns = self.columns.value()

        if not rows or not columns:
            popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                          "Parameter error",
                                          "Row and column numbers may not be zero.",
                                          QtWidgets.QMessageBox.Ok,
                                          self)
            popup.show()
        else:
            padding = self.pad.value()
            space = self.space.value()

            fmt = QtGui.QTextTableFormat()
            fmt.setCellPadding(padding)
            fmt.setCellSpacing(space)

            cursor.insertTable(rows, columns, fmt)

            self.close()


class textFind(QtWidgets.QDialog):
    """ Dialog to find and replace in text """
    def __init__(self, parent=None):
        super(textFind, self).__init__(parent)

        self.w_parent = parent

        self.lastStart = 0

        findButton = QtWidgets.QPushButton("Find", self)
        findButton.clicked.connect(self.find)

        replaceButton = QtWidgets.QPushButton("Replace", self)
        replaceButton.clicked.connect(self.replace)

        allButton = QtWidgets.QPushButton("Replace all", self)
        allButton.clicked.connect(self.replaceAll)

        self.normalRadio = QtWidgets.QRadioButton("Normal", self)

        regexRadio = QtWidgets.QRadioButton("RegEx", self)

        self.findField = QtWidgets.QTextEdit(self)
        self.findField.resize(250, 50)

        self.replaceField = QtWidgets.QTextEdit(self)
        self.replaceField.resize(250, 50)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.findField, 1, 0, 1, 4)
        layout.addWidget(self.normalRadio, 2, 2)
        layout.addWidget(regexRadio, 2, 3)
        layout.addWidget(findButton, 2, 0, 1, 2)

        layout.addWidget(self.replaceField, 3, 0, 1, 4)
        layout.addWidget(replaceButton, 4, 0, 1, 2)
        layout.addWidget(allButton, 4, 2, 1, 2)

        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle("Find and Replace")
        self.setLayout(layout)

        self.normalRadio.setChecked(True)

    def find(self):
        text = self.w_parent.toPlainText()
        query = self.findField.toPlainText()

        if self.normalRadio.isChecked():

            self.lastStart = text.find(query, self.lastStart + 1)

            if self.lastStart >= 0:
                end = self.lastStart + len(query)
                self.moveCursor(self.lastStart, end)
            else:
                self.lastStart = 0
                self.w_parent.moveCursor(QtGui.QTextCursor.End)
        else:
            pattern = re.compile(query)
            match = pattern.search(text, self.lastStart + 1)

            if match:
                self.lastStart = match.start()
                self.moveCursor(self.lastStart, match.end())
            else:
                self.lastStart = 0
                self.w_parent.text.moveCursor(QtGui.QTextCursor.End)

    def replace(self):
        cursor = self.w_parent.textCursor()

        # Security
        if cursor.hasSelection():
            # We insert the new text, which will override the selected
            # text
            cursor.insertText(self.replaceField.toPlainText())

            # And set the new cursor
            self.w_parent.setTextCursor(cursor)

    def replaceAll(self):
        self.lastStart = 0
        self.find()

        # Replace and find until self.lastStart is 0 again
        while self.lastStart:
            self.replace()
            self.find()

    def moveCursor(self, start, end):

        # We retrieve the QTextCursor object from the parent's QTextEdit
        cursor = self.w_parent.textCursor()

        # Then we set the position to the beginning of the last match
        cursor.setPosition(start)

        # Next we move the Cursor by over the match and pass the KeepAnchor parameter
        # which will make the cursor select the the match's text
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)

        # And finally we set this new cursor as the parent's
        self.w_parent.setTextCursor(cursor)


class actionInsertDateTime(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionInsertDateTime, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/calendar.svg"))

        self.setToolTip("Insert current date and time")
        self.connect(SIGNAL("triggered()"), self.insert)

    def insert(self):
        dialog = dateTime(self.w_parent)
        dialog.exec_()


class actionInsertBulletList(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionInsertBulletList, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/bullet-list.svg"))

        self.setToolTip("Insert bullet list")
        self.connect(SIGNAL("triggered()"), self.bulletList)

    def bulletList(self):
        cursor = self.w_parent.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDisc)


class actionInsertDigitList(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionInsertDigitList, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/list-button.svg"))

        self.setToolTip("Insert digital list")
        self.connect(SIGNAL("triggered()"), self.decimalList)

    def decimalList(self):
        cursor = self.w_parent.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)


class actionInsertTable(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionInsertTable, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/spreadsheet.svg"))

        self.setToolTip("Insert table")
        self.connect(SIGNAL("triggered()"), self.insertTable)

    def insertTable(self):
        dialog = textTable(self.w_parent)
        dialog.exec_()


class actionFind(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionFind, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/find.svg"))

        self.setToolTip("Input pattern to find in text")
        self.connect(SIGNAL("triggered()"), self.insertTable)

    def insertTable(self):
        dialog = textFind(self.w_parent)
        dialog.show()


class actionMakeBold(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeBold, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/bold.svg"))

        self.setToolTip("Set bold font")
        self.connect(SIGNAL("triggered()"), self.makeBold)

    def makeBold(self):
        if self.w_parent.fontWeight() == QtGui.QFont.Bold:
            self.w_parent.setFontWeight(QtGui.QFont.Normal)
        else:
            self.w_parent.setFontWeight(QtGui.QFont.Bold)


class actionMakeItalic(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeItalic, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/italic.svg"))

        self.setToolTip("Set italic font")
        self.connect(SIGNAL("triggered()"), self.makeItalic)

    def makeItalic(self):
        state = self.w_parent.fontItalic()
        self.w_parent.setFontItalic(not state)


class actionMakeUnderline(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeUnderline, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/underline.svg"))

        self.setToolTip("Set underlined font")
        self.connect(SIGNAL("triggered()"), self.makeUnderline)

    def makeUnderline(self):
        state = self.w_parent.fontUnderline()
        self.w_parent.setFontUnderline(not state)


class actionMakeStrike(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeStrike, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/strikethrough.svg"))

        self.setToolTip("Set strikethrough font")
        self.connect(SIGNAL("triggered()"), self.makeStrike)

    def makeStrike(self):
        fmt = self.w_parent.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.w_parent.setCurrentCharFormat(fmt)


class actionMakeSuperscript(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeSuperscript, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/superscript.svg"))

        self.setToolTip("Set superscript")
        self.connect(SIGNAL("triggered()"), self.superScript)

    def superScript(self):
        fmt = self.w_parent.currentCharFormat()
        align = fmt.verticalAlignment()

        if align == QtGui.QTextCharFormat.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        self.w_parent.setCurrentCharFormat(fmt)


class actionMakeSubscript(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionMakeSubscript, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/subscript.svg"))

        self.setToolTip("Set subscript")
        self.connect(SIGNAL("triggered()"), self.subScript)

    def subScript(self):
        fmt = self.w_parent.currentCharFormat()
        align = fmt.verticalAlignment()

        if align == QtGui.QTextCharFormat.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        self.w_parent.setCurrentCharFormat(fmt)


class actionAlignLeft(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionAlignLeft, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/left-alignment.svg"))

        self.setToolTip("Align text on the left")
        self.connect(SIGNAL("triggered()"), self.alignLeft)

    def alignLeft(self):
        self.w_parent.setAlignment(QtCore.Qt.AlignLeft)


class actionAlignRight(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionAlignRight, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/right-alignment.svg"))

        self.setToolTip("Align text on the right")
        self.connect(SIGNAL("triggered()"), self.alignRight)

    def alignRight(self):
        self.w_parent.setAlignment(QtCore.Qt.AlignRight)


class actionAlignCenter(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionAlignCenter, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/center-alignment.svg"))

        self.setToolTip("Center text")
        self.connect(SIGNAL("triggered()"), self.alignCenter)

    def alignCenter(self):
        self.w_parent.setAlignment(QtCore.Qt.AlignCenter)


class actionAlignJustify(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionAlignJustify, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/justify.svg"))

        self.setToolTip("Justify text")
        self.connect(SIGNAL("triggered()"), self.alignJustify)

    def alignJustify(self):
        self.w_parent.setAlignment(QtCore.Qt.AlignJustify)


class actionIndentArea(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionIndentArea, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/indent.svg"))

        self.setToolTip("Indent area")
        self.connect(SIGNAL("triggered()"), self.indent)

    def indent(self):
        cursor = self.w_parent.textCursor()

        if cursor.hasSelection():
            temp = cursor.blockNumber()

            # Move to the selection's end
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp

            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down

            # Iterate over lines (diff absolute value)
            for n in range(abs(diff) + 1):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)

                # Insert tabbing
                cursor.insertText("\t")

                # And move back up
                cursor.movePosition(direction)

        # If there is no selection, just insert a tab
        else:
            cursor.insertText("\t")


class actionDedentArea(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(actionDedentArea, self).__init__(parent)

        self.w_parent = parent

        self.setIcon(QtGui.QIcon(":/icons/dialogToolbar/dedent.svg"))

        self.setToolTip("Dedent area")
        self.connect(SIGNAL("triggered()"), self.dedent)

    def handleDedent(self, cursor):
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)

        # Grab the current line
        line = cursor.block().text()

        # If the line starts with a tab character, delete it
        if line.startswith("\t"):

            # Delete next character
            cursor.deleteChar()

        # Otherwise, delete all spaces until a non-space character is met
        else:
            for char in line[:8]:

                if char != " ":
                    break

                cursor.deleteChar()

    def dedent(self):
        cursor = self.w_parent.textCursor()

        if cursor.hasSelection():

            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's last line
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp

            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down

            # Iterate over lines
            for n in range(abs(diff) + 1):
                self.handleDedent(cursor)

                # Move up
                cursor.movePosition(direction)
        else:
            self.handleDedent(cursor)
