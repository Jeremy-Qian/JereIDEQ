from PySide6.QtWidgets import QFrame
from const.theme import STATUS_BAR_BG, STATUS_BAR_HEIGHT


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(STATUS_BAR_HEIGHT)
        self.setStyleSheet(f"background-color: {STATUS_BAR_BG};")