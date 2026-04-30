from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from const.theme import EDITOR_BG


class WelcomeFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {EDITOR_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._label = QLabel("needs implementation")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("color: #888; font-size: 18px;")

        layout.addWidget(self._label)