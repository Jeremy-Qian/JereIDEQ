from PySide6.QtWidgets import QWidget
from const.theme import STATUS_BAR_BG, STATUS_BAR_HEIGHT


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(STATUS_BAR_HEIGHT)
        self.setStyleSheet(f"background-color: {STATUS_BAR_BG}; border: 1px solid #ccc;")