from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Signal, Qt
from const.theme import EDITOR_BG, STATUS_BAR_BG


class BottomPanel(QWidget):
    """Collapsible bottom panel (dock) that can be toggled via the status bar button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)
        self.setStyleSheet(
            f"QWidget {{ background-color: {EDITOR_BG}; border-top: 1px solid #ccc; }}"
        )
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder = QLabel("needs implementation")
        placeholder.setStyleSheet("color: #888; font-size: 14px; font-style: italic;")
        layout.addWidget(placeholder)

    def toggle(self):
        """Toggle the visibility of the bottom panel."""
        self.setVisible(not self.isVisible())
