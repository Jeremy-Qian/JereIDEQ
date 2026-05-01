from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from const.theme import EDITOR_BG
import os


class WelcomeFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {EDITOR_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.addStretch()

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "src", "icons", "logo.svg")

        self._logo = QLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(logo_path)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.end()

        self._logo.setPixmap(pixmap)
        self._logo.setAlignment(Qt.AlignCenter)

        self._label = QLabel("needs implementation")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("color: #888; font-size: 18px;")

        layout.addWidget(self._logo)
        layout.addWidget(self._label)
        layout.addStretch()
