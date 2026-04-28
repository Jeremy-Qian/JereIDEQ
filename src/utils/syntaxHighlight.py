from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat
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
        keyword_fmt = self._create_format(SYNTAX_KEYWORD, bold=True)
        for word in self.PYTHON_KEYWORDS:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self._highlighting_rules.append((pattern, keyword_fmt))

        builtin_fmt = self._create_format(SYNTAX_BUILTIN)
        for word in self.PYTHON_BUILTINS:
            pattern = QRegularExpression(r'\b' + word + r'(?=\s*\()')
            self._highlighting_rules.append((pattern, builtin_fmt))

        decorator_fmt = self._create_format(SYNTAX_DECORATOR)
        pattern = QRegularExpression(r'@\w+')
        self._highlighting_rules.append((pattern, decorator_fmt))

        class_fmt = self._create_format(SYNTAX_CLASS_DEF, bold=True)
        pattern = QRegularExpression(r'\bclass\s+\w+')
        self._highlighting_rules.append((pattern, class_fmt))

        func_fmt = self._create_format(SYNTAX_FUNCTION_DEF)
        pattern = QRegularExpression(r'\bdef\s+\w+')
        self._highlighting_rules.append((pattern, func_fmt))

        comment_fmt = self._create_format(SYNTAX_COMMENT, italic=True)
        pattern = QRegularExpression(r'#.*')
        self._highlighting_rules.append((pattern, comment_fmt))

        triple_quote_fmt = self._create_format(SYNTAX_STRING)
        pattern = QRegularExpression(r'""".*"""')
        self._highlighting_rules.append((pattern, triple_quote_fmt))
        pattern = QRegularExpression(r"'''.*'''")
        self._highlighting_rules.append((pattern, triple_quote_fmt))

        string_fmt = self._create_format(SYNTAX_STRING)
        pattern = QRegularExpression(r'"(?:[^"\\]|\\.)*"')
        self._highlighting_rules.append((pattern, string_fmt))

        pattern = QRegularExpression(r"'(?:[^'\\]|\\.)*'")
        self._highlighting_rules.append((pattern, string_fmt))

        number_fmt = self._create_format(SYNTAX_NUMBER)
        pattern = QRegularExpression(r'\b[0-9]+\.?[0-9]*\b')
        self._highlighting_rules.append((pattern, number_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
