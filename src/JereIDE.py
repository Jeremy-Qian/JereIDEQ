# Entry Point
import sys
from PySide6.QtWidgets import QApplication
from ui.mainWindow import MainWindow
from const.paths import STYLESHEET_PATH


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(STYLESHEET_PATH, "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
