from PySide6.QtWidgets import QFrame


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setStyleSheet("background-color: #f5f5f5;")