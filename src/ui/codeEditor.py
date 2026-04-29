from PySide6.QtWidgets import QPlainTextEdit, QTextEdit
from PySide6.QtCore import Qt, QRect, QRegularExpression
from PySide6.QtGui import QPainter, QTextFormat, QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QBrush, QKeyEvent, QTextCursor
from ui.lineNumber import LineNumberArea
from utils.syntaxHighlight import PythonSyntaxHighlighter
from const.theme import EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE, LINE_NUMBER_BG, LINE_NUMBER_TEXT, CURRENT_LINE_BG
from const.theme import SYNTAX_KEYWORD, SYNTAX_STRING, SYNTAX_NUMBER, SYNTAX_COMMENT
from const.theme import SYNTAX_BUILTIN, SYNTAX_DECORATOR, SYNTAX_CLASS_DEF, SYNTAX_FUNCTION_DEF, PAIR_HIGHLIGHT


class QCodeEditor(QPlainTextEdit):
    PAIRS = {
        '(': ')',
        '[': ']',
        '{': '}',
        '"': '"',
        "'": "'",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.auto_indent_enabled = True
        self.line_numbers_enabled = True
        self.auto_pairing_enabled = True
        self._highlighted_pair = None

        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setStyleSheet("QPlainTextEdit { border: none; background-color: white; }")

        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

        # Apply Python syntax highlighting
        self.syntax_highlighter = PythonSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self._on_cursor_moved)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def keyPressEvent(self, event):
        key = event.text()
        if self.auto_pairing_enabled and key in self.PAIRS:
            cursor = self.textCursor()
            cursor.insertText(key + self.PAIRS[key])
            cursor.movePosition(QTextCursor.PreviousCharacter, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
            self._highlight_pair_at_cursor()
        elif self.auto_indent_enabled and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            cursor = self.textCursor()
            block = cursor.block()
            current_line_text = block.text()

            leading_whitespace = ''
            for char in current_line_text:
                if char in ' \t':
                    leading_whitespace += char
                else:
                    break

            cursor.insertText('\n' + leading_whitespace)
            self.setTextCursor(cursor)
        else:
            super().keyPressEvent(event)

    def _highlight_pair_at_cursor(self):
        self._highlighted_pair = None
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()
        
        if pos < len(text):
            char = text[pos]
            if char in self.PAIRS.values():
                self._find_and_highlight_pair(pos, char)
            elif char in self.PAIRS:
                self._find_opening_pair(pos, char)
        self.highlight_current_line()

    def _find_opening_pair(self, pos, opening_char):
        closing_char = self.PAIRS[opening_char]
        text = self.toPlainText()
        close_pos = text.find(closing_char, pos + 1)
        
        while close_pos >= 0:
            if self._is_unnested(text, pos, close_pos, closing_char, opening_char):
                break
            close_pos = text.find(closing_char, close_pos + 1)
        
        if close_pos >= 0:
            self._highlighted_pair = (pos, close_pos)

    def _find_and_highlight_pair(self, pos, closing_char):
        opening_char = None
        for o, c in self.PAIRS.items():
            if c == closing_char:
                opening_char = o
                break
        
        if not opening_char:
            return
        
        text = self.toPlainText()
        open_pos = text.rfind(opening_char, 0, pos)
        
        while open_pos >= 0:
            if self._is_unnested(text, open_pos, pos, closing_char, opening_char):
                break
            open_pos = text.rfind(opening_char, 0, open_pos)
        
        if open_pos >= 0:
            self._highlighted_pair = (open_pos, pos)

    def _is_unnested(self, text, open_pos, close_pos, closing_char, opening_char):
        stack = []
        for i in range(open_pos + 1, close_pos):
            ch = text[i]
            if ch in self.PAIRS:
                stack.append(ch)
            elif ch in self.PAIRS.values():
                if stack and ((ch == ')' and stack[-1] == '(') or 
                          (ch == ']' and stack[-1] == '[') or 
                          (ch == '}' and stack[-1] == '{') or 
                          (ch == '"' and stack[-1] == '"') or 
                          (ch == "'" and stack[-1] == "'")):
                    stack.pop()
        return opening_char not in stack

    def set_line_numbers_enabled(self, enabled: bool):
        self.line_numbers_enabled = enabled
        self.line_number_area.setVisible(enabled)
        self.update_line_number_area_width(0)

    def _on_cursor_moved(self):
        if not self.auto_pairing_enabled:
            self._highlighted_pair = None
            return
        self._highlight_pair_at_cursor()

    def line_number_area_width(self):
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        if self.line_numbers_enabled:
            self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        else:
            self.setViewportMargins(0, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(CURRENT_LINE_BG))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

            if self._highlighted_pair:
                open_pos, close_pos = self._highlighted_pair
                for p in [open_pos, close_pos]:
                    cursor = QTextCursor(self.document())
                    cursor.setPosition(p)
                    cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)
                    selection = QTextEdit.ExtraSelection()
                    selection.format.setBackground(QColor(PAIR_HIGHLIGHT))
                    selection.cursor = cursor
                    extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(LINE_NUMBER_BG))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(LINE_NUMBER_TEXT))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                              Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
