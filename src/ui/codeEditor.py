from PySide6.QtWidgets import QPlainTextEdit, QTextEdit
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QPainter, QTextFormat, QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QBrush
from ui.lineNumber import LineNumberArea
from const.theme import EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE, LINE_NUMBER_BG, LINE_NUMBER_TEXT, CURRENT_LINE_BG
from const.theme import SYNTAX_KEYWORD, SYNTAX_STRING, SYNTAX_NUMBER, SYNTAX_COMMENT
from const.theme import SYNTAX_BUILTIN, SYNTAX_DECORATOR, SYNTAX_CLASS_DEF, SYNTAX_FUNCTION_DEF


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    PYTHON_KEYWORDS = [
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    ]

    PYTHON_BUILTINS = [
        'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr', 'dict',
        'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
        'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id',
        'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals',
        'map', 'max', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow',
        'print', 'property', 'range', 'repr', 'reversed', 'round', 'set',
        'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
        'type', 'vars', 'zip', '__import__'
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._highlighting_rules = []
        self._build_highlighting_rules()

    def _create_format(self, color, bold=False, italic=False):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _build_highlighting_rules(self):
        # Keywords (e.g., def, class, if, while, etc.)
        keyword_fmt = self._create_format(SYNTAX_KEYWORD, bold=True)
        for word in self.PYTHON_KEYWORDS:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self._highlighting_rules.append((pattern, keyword_fmt))

        # Built-in functions
        builtin_fmt = self._create_format(SYNTAX_BUILTIN)
        for word in self.PYTHON_BUILTINS:
            pattern = QRegularExpression(r'\b' + word + r'(?=\s*\()')
            self._highlighting_rules.append((pattern, builtin_fmt))

        # Decorators
        decorator_fmt = self._create_format(SYNTAX_DECORATOR)
        pattern = QRegularExpression(r'@\w+')
        self._highlighting_rules.append((pattern, decorator_fmt))

        # Class definitions
        class_fmt = self._create_format(SYNTAX_CLASS_DEF, bold=True)
        pattern = QRegularExpression(r'\bclass\s+\w+')
        self._highlighting_rules.append((pattern, class_fmt))

        # Function definitions
        func_fmt = self._create_format(SYNTAX_FUNCTION_DEF)
        pattern = QRegularExpression(r'\bdef\s+\w+')
        self._highlighting_rules.append((pattern, func_fmt))

        # Single-line comments
        comment_fmt = self._create_format(SYNTAX_COMMENT, italic=True)
        pattern = QRegularExpression(r'#.*')
        self._highlighting_rules.append((pattern, comment_fmt))

        # Triple-quoted strings (docstrings)
        triple_quote_fmt = self._create_format(SYNTAX_STRING)
        pattern = QRegularExpression(r'""".*?"""', QRegularExpression.MultilineCapture)
        self._highlighting_rules.append((pattern, triple_quote_fmt))
        pattern = QRegularExpression(r"'''.*?'''", QRegularExpression.MultilineCapture)
        self._highlighting_rules.append((pattern, triple_quote_fmt))

        # Double-quoted strings
        string_fmt = self._create_format(SYNTAX_STRING)
        pattern = QRegularExpression(r'"(?:[^"\\]|\\.)*"')
        self._highlighting_rules.append((pattern, string_fmt))

        # Single-quoted strings
        pattern = QRegularExpression(r"'(?:[^'\\]|\\.)*'")
        self._highlighting_rules.append((pattern, string_fmt))

        # Triple-double-quoted strings (raw)
        pattern = QRegularExpression(r'""".*?"""')
        self._highlighting_rules.append((pattern, triple_quote_fmt))

        # Triple-single-quoted strings (raw)
        pattern = QRegularExpression(r"'''.*?'''")
        self._highlighting_rules.append((pattern, triple_quote_fmt))

        # Numbers (integers and floats)
        number_fmt = self._create_format(SYNTAX_NUMBER)
        pattern = QRegularExpression(r'\b[0-9]+\.?[0-9]*\b')
        self._highlighting_rules.append((pattern, number_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class QCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        # Apply Python syntax highlighting
        self.syntax_highlighter = PythonSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

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
