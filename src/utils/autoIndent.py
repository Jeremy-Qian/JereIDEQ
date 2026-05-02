from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from config.config_manager import config_manager


class AutoIndent:
    def __init__(self, editor):
        self.editor = editor
        # Load pairs from configuration
        self.PAIRS = config_manager.get_config_value('editor', 'auto_indent.pairs', {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'",
        })
        # Check if auto-indent is enabled in configuration
        self.auto_indent_enabled = config_manager.get_config_value('editor', 'auto_indent.enabled', True)

    def handle_key_press(self, event):
        """Handle auto-indent when Enter/Return is pressed."""
        if self.auto_indent_enabled and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            cursor = self.editor.textCursor()
            block = cursor.block()
            current_line_text = block.text()

            leading_whitespace = ''
            for char in current_line_text:
                if char in ' \t':
                    leading_whitespace += char
                else:
                    break

            cursor.insertText('\n' + leading_whitespace)
            self.editor.setTextCursor(cursor)
            return True
        return False
