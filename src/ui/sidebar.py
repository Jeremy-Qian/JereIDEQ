from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(150)
        self.setMaximumWidth(500)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        label = QLabel("Needs Implementation")
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; border: none;")
        layout.addWidget(label)

        layout.addStretch()