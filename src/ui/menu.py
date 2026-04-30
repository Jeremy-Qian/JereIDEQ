from PySide6.QtWidgets import QMenuBar


class MenuBar:
    def __init__(self, window):
        self.window = window
        self.auto_indent_action = None
        self.line_numbers_action = None
        self.auto_pairing_action = None
        self.wrap_action = None

    def setup(self):
        menu_bar = self.window.menuBar()
        self._setup_file_menu(menu_bar)
        self._setup_options_menu(menu_bar)

    def _setup_file_menu(self, menu_bar):
        file_menu = menu_bar.addMenu("&File")

        new_action = file_menu.addAction("&New")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.window.new_file)

        open_action = file_menu.addAction("&Open")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.window.open_file)

        save_action = file_menu.addAction("&Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.window.save_file)

        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.triggered.connect(self.window.save_as_file)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.window.close)

    def _setup_options_menu(self, menu_bar):
        options_menu = menu_bar.addMenu("&Options")

        self.auto_indent_action = options_menu.addAction("&Auto Indent")
        self.auto_indent_action.setCheckable(True)
        self.auto_indent_action.setChecked(self.window.auto_indent_enabled)
        self.auto_indent_action.triggered.connect(self.window.toggle_auto_indent)

        self.line_numbers_action = options_menu.addAction("&Line Numbers")
        self.line_numbers_action.setCheckable(True)
        self.line_numbers_action.setChecked(self.window.line_numbers_enabled)
        self.line_numbers_action.triggered.connect(self.window.toggle_line_numbers)

        self.auto_pairing_action = options_menu.addAction("&Auto Pairing")
        self.auto_pairing_action.setCheckable(True)
        self.auto_pairing_action.setChecked(self.window.auto_pairing_enabled)
        self.auto_pairing_action.triggered.connect(self.window.toggle_auto_pairing)

        self.wrap_action = options_menu.addAction("&Word Wrap")
        self.wrap_action.setCheckable(True)
        self.wrap_action.setChecked(self.window.wrap_enabled)
        self.wrap_action.triggered.connect(self.window.toggle_wrap)