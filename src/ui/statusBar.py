
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from const.theme import STATUS_BAR_BG, STATUS_BAR_HEIGHT


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(STATUS_BAR_HEIGHT)
        self.setStyleSheet(f"background-color: {STATUS_BAR_BG}; border-top: 1px solid #ccc;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        self._position_button = QPushButton("1:1")
        self._position_button.setFixedHeight(STATUS_BAR_HEIGHT - 4)
        self._position_button.setStyleSheet(
            "QPushButton { background-color: transparent; border: none; "
            "color: #666; font-size: 12px; padding: 0 5px; text-align: left; }"
            "QPushButton:disabled { color: #666; }"
        )

        layout.addWidget(self._position_button)
        layout.addStretch()

    def update_position(self, line: int, column: int):
        self._position_button.setText(f"{line}:{column}")
