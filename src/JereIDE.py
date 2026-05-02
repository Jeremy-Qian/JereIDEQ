# Entry Point
import sys
import os

# Add src directory to path
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

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
