import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox
from ui.codeEditor import QCodeEditor
from ui.statusBar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JereIDE")
        self.resize(800, 600)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = QCodeEditor()
        layout.addWidget(self.editor)

        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

        self.setCentralWidget(container)

        self.setup_menu()
        self.current_file = None

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        new_action = file_menu.addAction("&New")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)

        open_action = file_menu.addAction("&Open")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = file_menu.addAction("&Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.triggered.connect(self.save_as_file)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

    def new_file(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("JereIDE")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = file_path
                self.setWindowTitle(f"JereIDE - {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)")
        if file_path:
            self.current_file = file_path
            self.save_file()
            self.setWindowTitle(f"JereIDE - {os.path.basename(file_path)}")
