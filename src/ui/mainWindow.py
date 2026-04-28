import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox
from ui.codeEditor import QCodeEditor
from ui.statusBar import StatusBar
from ui.tabs import JereIDEBook


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JereIDE - untitled")
        self.setWindowFilePath("")
        self.resize(800, 600)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.notebook = JereIDEBook(None)
        layout.addWidget(self.notebook)

        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

        self.setCentralWidget(container)

        self.setup_menu()

        self.notebook.page_changed.connect(self.on_tab_changed)
        self.notebook.page_close_requested.connect(self.on_tab_close_requested)

        self._tabs_data = []

        self._create_new_tab()

    def _create_new_tab(self, title: str = "untitled", file_path: str | None = None):
        editor = QCodeEditor()
        self.notebook.AddPage(editor, title)
        tab_index = self.notebook.GetPageCount() - 1
        self._tabs_data.append({
            "editor": editor,
            "file_path": file_path,
            "is_untitled": file_path is None,
            "original_content": ""
        })
        editor.textChanged.connect(lambda: self.on_text_changed(editor))

    def _get_current_tab_data(self):
        idx = self.notebook.GetSelection()
        if 0 <= idx < len(self._tabs_data):
            return idx, self._tabs_data[idx]
        return -1, None

    def _get_tab_index_by_editor(self, editor):
        for i, data in enumerate(self._tabs_data):
            if data["editor"] == editor:
                return i
        return -1

    def on_tab_changed(self, index: int):
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            file_path = data["file_path"]
            is_untitled = data["is_untitled"]
            file_name = os.path.basename(file_path) if file_path else "untitled"
            is_modified = data["editor"].toPlainText() != data["original_content"]
            title = f"JereIDE - {file_name}{' *' if is_modified else ''}"
            self.setWindowTitle(title)
            self.setWindowFilePath(file_path if file_path else "")
            self.setWindowModified(is_modified)

    def on_tab_close_requested(self, index: int):
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            is_modified = data["editor"].toPlainText() != data["original_content"]
            if is_modified:
                file_name = os.path.basename(data["file_path"]) if data["file_path"] else "untitled"
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"Save changes to {file_name}?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Save:
                    self._save_current_tab(index)
                    self._close_tab(index)
                elif reply == QMessageBox.StandardButton.Discard:
                    self._close_tab(index)
            else:
                self._close_tab(index)

    def _close_tab(self, index: int):
        self.notebook.CloseTab(index)
        if 0 <= index < len(self._tabs_data):
            self._tabs_data.pop(index)
        for i in range(len(self._tabs_data)):
            self.notebook.SetPageText(i, self._get_tab_title(i))
        if self.notebook.GetPageCount() == 0:
            self._create_new_tab()

    def _get_tab_title(self, index: int):
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            file_path = data["file_path"]
            return os.path.basename(file_path) if file_path else "untitled"
        return "untitled"

    def _save_current_tab(self, index: int):
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            if data["file_path"]:
                try:
                    with open(data["file_path"], 'w', encoding='utf-8') as f:
                        f.write(data["editor"].toPlainText())
                    data["original_content"] = data["editor"].toPlainText()
                    file_name = os.path.basename(data["file_path"])
                    self.notebook.SetPageText(index, file_name)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file: {e}")
            else:
                self._save_as_current_tab(index)

    def _save_as_current_tab(self, index: int):
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File As", "",
                "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
            )
            if file_path:
                data["file_path"] = file_path
                data["is_untitled"] = False
                self._save_current_tab(index)
                self.notebook.SetPageText(index, os.path.basename(file_path))

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
        self._create_new_tab()
        idx = self.notebook.GetSelection()
        self.on_tab_changed(idx)

    def on_text_changed(self, editor):
        index = self._get_tab_index_by_editor(editor)
        if 0 <= index < len(self._tabs_data):
            data = self._tabs_data[index]
            is_modified = data["editor"].toPlainText() != data["original_content"]
            self.setWindowModified(is_modified)
            file_name = os.path.basename(data["file_path"]) if data["file_path"] else "untitled"
            title = f"JereIDE - {file_name}{' *' if is_modified else ''}"
            self.setWindowTitle(title)
            self.notebook.SetPageText(index, f"{file_name}{' *' if is_modified else ''}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
                return

            editor = QCodeEditor()
            title = os.path.basename(file_path)
            page_count = self.notebook.GetPageCount()
            self.notebook.AddPage(editor, title)
            self.notebook.SelectTab(page_count)
            idx = page_count
            self._tabs_data.append({
                "editor": editor,
                "file_path": file_path,
                "is_untitled": False,
                "original_content": content
            })
            editor.textChanged.connect(lambda: self.on_text_changed(editor))
            editor.setPlainText(content)
            self.on_tab_changed(idx)

    def save_file(self):
        idx = self.notebook.GetSelection()
        if 0 <= idx < len(self._tabs_data):
            self._save_current_tab(idx)
            self.on_tab_changed(idx)

    def save_as_file(self):
        idx = self.notebook.GetSelection()
        if 0 <= idx < len(self._tabs_data):
            self._save_as_current_tab(idx)
            self.on_tab_changed(idx)
