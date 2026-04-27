import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                             QTextEdit, QWidget, QVBoxLayout, QPushButton)

class TabbedEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Tabbed Editor")
        self.setGeometry(100, 100, 800, 600)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Add initial tab
        self.add_new_tab()

        # Add a button to add new tabs
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.add_tab_button)

    def add_new_tab(self):
        editor = QTextEdit()
        tab_name = f"Tab {self.tabs.count() + 1}"
        self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentWidget(editor)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabbedEditor()
    window.show()
    sys.exit(app.exec())
