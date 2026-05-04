import keyword
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


WINDOW_TITLE = "JereIDE Tk"
EDITOR_FONT_FAMILY = "Monaco"
EDITOR_FONT_SIZE = 11
EDITOR_BACKGROUND = "#FFFFFF"
LINE_NUMBER_BACKGROUND = "#DCDCDC"
LINE_NUMBER_TEXT = "#000000"
CURRENT_LINE_BACKGROUND = "#FFFFD0"
STATUS_BAR_BACKGROUND = "#F5F5F5"
TAB_SELECTED_BACKGROUND = "#CEE6FC"
TAB_UNSELECTED_BACKGROUND = "#FFFFFF"
SYNTAX_KEYWORD = "#0000FF"
SYNTAX_STRING = "#A315AD"
SYNTAX_NUMBER = "#098658"
SYNTAX_COMMENT = "#008000"
SYNTAX_BUILTIN = "#795E26"
SYNTAX_DECORATOR = "#800000"
SYNTAX_DEFINITION = "#267F99"


class TabData:
    def __init__(self, editor, filePath=None, originalContent=""):
        self.editor = editor
        self.filePath = filePath
        self.originalContent = originalContent


class CodeEditor(tk.Frame):
    def __init__(self, parent, onTextChanged, onCursorMoved):
        super().__init__(parent, background=EDITOR_BACKGROUND)
        self.onTextChanged = onTextChanged
        self.onCursorMoved = onCursorMoved
        self.syntaxHighlightingEnabled = True
        self.autoIndentEnabled = True
        self.autoPairingEnabled = True
        self.lineNumbersEnabled = True
        self.wrapEnabled = False
        self._highlightJob = None
        self._lineNumberJob = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.lineNumbers = tk.Text(
            self,
            width=4,
            padx=4,
            takefocus=0,
            borderwidth=0,
            highlightthickness=0,
            background=LINE_NUMBER_BACKGROUND,
            foreground=LINE_NUMBER_TEXT,
            font=(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE),
            state="disabled",
        )
        self.lineNumbers.grid(row=0, column=0, sticky="ns")

        self.text = tk.Text(
            self,
            undo=True,
            wrap="none",
            borderwidth=0,
            highlightthickness=0,
            background=EDITOR_BACKGROUND,
            insertbackground="#000000",
            font=(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE),
        )
        self.text.grid(row=0, column=1, sticky="nsew")

        self.verticalScrollBar = ttk.Scrollbar(self, orient="vertical", command=self._scrollVertical)
        self.verticalScrollBar.grid(row=0, column=2, sticky="ns")
        self.horizontalScrollBar = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.horizontalScrollBar.grid(row=1, column=1, sticky="ew")

        self.text.configure(yscrollcommand=self._onTextScroll, xscrollcommand=self.horizontalScrollBar.set)
        self.lineNumbers.configure(yscrollcommand=self.verticalScrollBar.set)

        self._configureTags()
        self.text.bind("<<Modified>>", self._onModified)
        self.text.bind("<KeyRelease>", self._onKeyRelease)
        self.text.bind("<ButtonRelease-1>", self._onCursorMoved)
        self.text.bind("<KeyPress-Return>", self._handleReturn)
        self.text.bind("<KeyPress>", self._handleAutoPairing)
        self.text.bind("<MouseWheel>", self._onMouseWheel)
        self.text.bind("<Button-4>", self._onMouseWheel)
        self.text.bind("<Button-5>", self._onMouseWheel)
        self.text.bind("<Configure>", lambda event: self.updateLineNumbers())
        self.updateLineNumbers()
        self.highlightCurrentLine()

    def _configureTags(self):
        self.text.tag_configure("currentLine", background=CURRENT_LINE_BACKGROUND)
        self.text.tag_configure("keyword", foreground=SYNTAX_KEYWORD)
        self.text.tag_configure("builtin", foreground=SYNTAX_BUILTIN)
        self.text.tag_configure("string", foreground=SYNTAX_STRING)
        self.text.tag_configure("comment", foreground=SYNTAX_COMMENT)
        self.text.tag_configure("number", foreground=SYNTAX_NUMBER)
        self.text.tag_configure("decorator", foreground=SYNTAX_DECORATOR)
        self.text.tag_configure("definition", foreground=SYNTAX_DEFINITION)

    def _scrollVertical(self, *args):
        self.text.yview(*args)
        self.lineNumbers.yview(*args)
        self.updateLineNumbers()

    def _onTextScroll(self, first, last):
        self.verticalScrollBar.set(first, last)
        self.lineNumbers.yview_moveto(first)
        self.updateLineNumbers()

    def _onMouseWheel(self, event):
        self.after_idle(self.updateLineNumbers)

    def _onModified(self, event=None):
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self.onTextChanged(self)
        self._scheduleLineNumberUpdate()
        self._scheduleSyntaxHighlight()

    def _onKeyRelease(self, event=None):
        self._onCursorMoved()
        self.highlightCurrentLine()

    def _onCursorMoved(self, event=None):
        self.onCursorMoved(self)
        self.highlightCurrentLine()

    def _handleReturn(self, event):
        if not self.autoIndentEnabled:
            return None
        currentLine = self.text.get("insert linestart", "insert")
        indentation = re.match(r"\s*", currentLine).group(0)
        if currentLine.rstrip().endswith(":"):
            indentation += " " * 4
        self.text.insert("insert", "\n" + indentation)
        return "break"

    def _handleAutoPairing(self, event):
        if not self.autoPairingEnabled or len(event.char) != 1:
            return None
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        if event.char not in pairs:
            return None
        if self.text.tag_ranges("sel"):
            selectedText = self.text.get("sel.first", "sel.last")
            self.text.delete("sel.first", "sel.last")
            self.text.insert("insert", event.char + selectedText + pairs[event.char])
            return "break"
        self.text.insert("insert", event.char + pairs[event.char])
        self.text.mark_set("insert", "insert-1c")
        return "break"

    def _scheduleLineNumberUpdate(self):
        if self._lineNumberJob:
            self.after_cancel(self._lineNumberJob)
        self._lineNumberJob = self.after(20, self.updateLineNumbers)

    def _scheduleSyntaxHighlight(self):
        if self._highlightJob:
            self.after_cancel(self._highlightJob)
        self._highlightJob = self.after(120, self.highlightSyntax)

    def getContent(self):
        return self.text.get("1.0", "end-1c")

    def setContent(self, content):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_modified(False)
        self.updateLineNumbers()
        self.highlightSyntax()
        self.highlightCurrentLine()

    def focusEditor(self):
        self.text.focus_set()

    def setLineNumbersEnabled(self, enabled):
        self.lineNumbersEnabled = enabled
        if enabled:
            self.lineNumbers.grid()
            self.updateLineNumbers()
        else:
            self.lineNumbers.grid_remove()

    def setWordWrap(self, enabled):
        self.wrapEnabled = enabled
        self.text.configure(wrap="word" if enabled else "none")

    def setSyntaxHighlightingEnabled(self, enabled):
        self.syntaxHighlightingEnabled = enabled
        if enabled:
            self.highlightSyntax()
        else:
            self._clearSyntaxTags()

    def updateLineNumbers(self):
        if not self.lineNumbersEnabled:
            return
        firstLine = int(self.text.index("@0,0").split(".")[0])
        lastLine = int(self.text.index(f"@0,{self.text.winfo_height()}").split(".")[0])
        totalLines = int(self.text.index("end-1c").split(".")[0])
        lastLine = min(max(lastLine, firstLine), totalLines)
        numbers = "\n".join(str(lineNumber) for lineNumber in range(firstLine, lastLine + 1))
        self.lineNumbers.configure(state="normal")
        self.lineNumbers.delete("1.0", "end")
        self.lineNumbers.insert("1.0", numbers)
        self.lineNumbers.configure(state="disabled")
        self._lineNumberJob = None

    def highlightCurrentLine(self):
        self.text.tag_remove("currentLine", "1.0", "end")
        self.text.tag_add("currentLine", "insert linestart", "insert lineend+1c")
        self.text.tag_lower("currentLine")

    def _clearSyntaxTags(self):
        for tagName in ("keyword", "builtin", "string", "comment", "number", "decorator", "definition"):
            self.text.tag_remove(tagName, "1.0", "end")

    def highlightSyntax(self):
        self._highlightJob = None
        self._clearSyntaxTags()
        if not self.syntaxHighlightingEnabled:
            return

        content = self.getContent()
        keywordSet = set(keyword.kwlist)
        builtinSet = {
            "abs", "all", "any", "bool", "dict", "enumerate", "float", "int", "len",
            "list", "max", "min", "open", "print", "range", "set", "str", "sum",
            "tuple", "type", "zip",
        }
        patterns = (
            ("comment", r"#[^\n]*"),
            ("string", r"(?s)('''.*?'''|\"\"\".*?\"\"\"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")"),
            ("decorator", r"(?m)^\s*@\w+(?:\.\w+)*"),
            ("number", r"\b\d+(?:\.\d+)?\b"),
            ("definition", r"\b(?:class|def)\s+([A-Za-z_][A-Za-z0-9_]*)"),
            ("keyword", r"\b(" + "|".join(re.escape(word) for word in sorted(keywordSet)) + r")\b"),
            ("builtin", r"\b(" + "|".join(re.escape(word) for word in sorted(builtinSet)) + r")\b"),
        )
        for tagName, pattern in patterns:
            for match in re.finditer(pattern, content):
                if tagName == "definition" and match.lastindex:
                    startOffset, endOffset = match.span(1)
                else:
                    startOffset, endOffset = match.span()
                self.text.tag_add(tagName, f"1.0+{startOffset}c", f"1.0+{endOffset}c")

    def getCursorLineColumn(self):
        lineText, columnText = self.text.index("insert").split(".")
        return int(lineText), int(columnText) + 1

    def undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        self.text.event_generate("<<Cut>>")

    def copy(self):
        self.text.event_generate("<<Copy>>")

    def paste(self):
        self.text.event_generate("<<Paste>>")

    def selectAll(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        return "break"


class WelcomeFrame(tk.Frame):
    def __init__(self, parent, onNewFile, onOpenFile):
        super().__init__(parent, background=EDITOR_BACKGROUND)
        self.onNewFile = onNewFile
        self.onOpenFile = onOpenFile
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        contentFrame = tk.Frame(self, background=EDITOR_BACKGROUND)
        contentFrame.grid(row=0, column=0)
        tk.Label(
            contentFrame,
            text="JereIDE",
            font=(EDITOR_FONT_FAMILY, 32, "bold"),
            background=EDITOR_BACKGROUND,
        ).pack(pady=(0, 8))
        tk.Label(
            contentFrame,
            text="A lightweight Tkinter implementation",
            font=(EDITOR_FONT_FAMILY, 14),
            foreground="#888888",
            background=EDITOR_BACKGROUND,
        ).pack(pady=(0, 24))
        ttk.Button(contentFrame, text="New File", command=self.onNewFile).pack(fill="x", pady=4)
        ttk.Button(contentFrame, text="Open File", command=self.onOpenFile).pack(fill="x", pady=4)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{WINDOW_TITLE} - untitled")
        self.geometry("900x650")
        self.minsize(640, 420)

        self.syntaxHighlightingEnabled = True
        self.autoIndentEnabled = True
        self.lineNumbersEnabled = True
        self.autoPairingEnabled = True
        self.wrapEnabled = False
        self.fullScreenEnabled = False
        self.bottomPanelVisible = False
        self._tabsData = {}

        self._setupStyle()
        self._setupMenu()
        self._setupLayout()
        self._bindShortcuts()
        self.createNewTab()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _setupStyle(self):
        self.style = ttk.Style(self)
        self.style.configure("TNotebook", background=TAB_UNSELECTED_BACKGROUND, borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(12, 5))
        self.style.map("TNotebook.Tab", background=[("selected", TAB_SELECTED_BACKGROUND)])

    def _setupLayout(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.contentFrame = tk.Frame(self, background=EDITOR_BACKGROUND)
        self.contentFrame.grid(row=0, column=0, sticky="nsew")
        self.contentFrame.rowconfigure(0, weight=1)
        self.contentFrame.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.contentFrame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.notebook.bind("<<NotebookTabChanged>>", self.onTabChanged)

        self.welcomeFrame = WelcomeFrame(self.contentFrame, self.createNewTab, self.openFile)

        self.bottomPanel = tk.Frame(self, height=150, background=EDITOR_BACKGROUND)
        self.bottomPanel.grid_propagate(False)
        tk.Label(
            self.bottomPanel,
            text="Terminal dock placeholder",
            anchor="nw",
            background=EDITOR_BACKGROUND,
            foreground="#666666",
            font=(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE),
        ).pack(fill="both", expand=True, padx=8, pady=8)

        self.statusBar = tk.Frame(self, height=24, background=STATUS_BAR_BACKGROUND)
        self.statusBar.grid(row=2, column=0, sticky="ew")
        self.statusBar.grid_propagate(False)
        self.positionLabel = tk.Label(
            self.statusBar,
            text="1:1",
            background=STATUS_BAR_BACKGROUND,
            foreground="#666666",
            font=(EDITOR_FONT_FAMILY, 10),
        )
        self.positionLabel.pack(side="left", padx=8)
        self.dockButton = tk.Button(
            self.statusBar,
            text="Dock",
            command=self.toggleBottomPanel,
            relief="flat",
            background=STATUS_BAR_BACKGROUND,
            activebackground=STATUS_BAR_BACKGROUND,
        )
        self.dockButton.pack(side="right", padx=8)

    def _setupMenu(self):
        menuBar = tk.Menu(self)
        self.config(menu=menuBar)

        fileMenu = tk.Menu(menuBar, tearoff=False)
        fileMenu.add_command(label="New", accelerator="Command+N", command=self.newFile)
        fileMenu.add_command(label="Open", accelerator="Command+O", command=self.openFile)
        fileMenu.add_command(label="Save", accelerator="Command+S", command=self.saveFile)
        fileMenu.add_command(label="Save As...", command=self.saveAsFile)
        fileMenu.add_command(label="Close Tab", accelerator="Command+W", command=self.closeCurrentTab)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.close)
        menuBar.add_cascade(label="File", menu=fileMenu)

        editMenu = tk.Menu(menuBar, tearoff=False)
        editMenu.add_command(label="Undo", accelerator="Command+Z", command=self.undo)
        editMenu.add_command(label="Redo", accelerator="Command+Shift+Z", command=self.redo)
        editMenu.add_separator()
        editMenu.add_command(label="Cut", accelerator="Command+X", command=self.cut)
        editMenu.add_command(label="Copy", accelerator="Command+C", command=self.copy)
        editMenu.add_command(label="Paste", accelerator="Command+V", command=self.paste)
        editMenu.add_separator()
        editMenu.add_command(label="Select All", accelerator="Command+A", command=self.selectAll)
        editMenu.add_separator()
        editMenu.add_command(label="Find...", accelerator="Command+F", command=self.find)
        editMenu.add_command(label="Replace...", accelerator="Command+H", command=self.replace)
        menuBar.add_cascade(label="Edit", menu=editMenu)

        optionsMenu = tk.Menu(menuBar, tearoff=False)
        self.syntaxHighlightingVar = tk.BooleanVar(value=self.syntaxHighlightingEnabled)
        self.autoIndentVar = tk.BooleanVar(value=self.autoIndentEnabled)
        self.lineNumbersVar = tk.BooleanVar(value=self.lineNumbersEnabled)
        self.autoPairingVar = tk.BooleanVar(value=self.autoPairingEnabled)
        self.wrapVar = tk.BooleanVar(value=self.wrapEnabled)
        optionsMenu.add_checkbutton(
            label="Syntax Highlighting",
            variable=self.syntaxHighlightingVar,
            command=self.toggleSyntaxHighlighting,
        )
        optionsMenu.add_checkbutton(label="Auto Indent", variable=self.autoIndentVar, command=self.toggleAutoIndent)
        optionsMenu.add_checkbutton(label="Line Numbers", variable=self.lineNumbersVar, command=self.toggleLineNumbers)
        optionsMenu.add_checkbutton(label="Auto Pairing", variable=self.autoPairingVar, command=self.toggleAutoPairing)
        optionsMenu.add_checkbutton(label="Word Wrap", variable=self.wrapVar, command=self.toggleWrap)
        menuBar.add_cascade(label="Options", menu=optionsMenu)

        viewMenu = tk.Menu(menuBar, tearoff=False)
        viewMenu.add_command(label="Toggle Full Screen", accelerator="Command+F", command=self.toggleFullScreen)
        menuBar.add_cascade(label="View", menu=viewMenu)

    def _bindShortcuts(self):
        shortcuts = {
            "<Command-n>": self.newFile,
            "<Control-n>": self.newFile,
            "<Command-o>": self.openFile,
            "<Control-o>": self.openFile,
            "<Command-s>": self.saveFile,
            "<Control-s>": self.saveFile,
            "<Command-S>": self.saveAsFile,
            "<Control-S>": self.saveAsFile,
            "<Command-w>": self.closeCurrentTab,
            "<Control-w>": self.closeCurrentTab,
            "<Command-z>": self.undo,
            "<Control-z>": self.undo,
            "<Command-Z>": self.redo,
            "<Control-y>": self.redo,
            "<Command-a>": self.selectAll,
            "<Control-a>": self.selectAll,
            "<Command-f>": self.find,
            "<Control-f>": self.find,
            "<Command-h>": self.replace,
            "<Control-h>": self.replace,
            "<Command-F>": self.toggleFullScreen,
        }
        for shortcut, callback in shortcuts.items():
            self.bind_all(shortcut, lambda event, callback=callback: self._invokeShortcut(callback))

    def _invokeShortcut(self, callback):
        callback()
        return "break"

    def createNewTab(self, title="untitled", filePath=None, content=""):
        self._showNotebook()
        editor = CodeEditor(self.notebook, self.onTextChanged, self.onCursorMoved)
        editor.autoIndentEnabled = self.autoIndentEnabled
        editor.autoPairingEnabled = self.autoPairingEnabled
        editor.setLineNumbersEnabled(self.lineNumbersEnabled)
        editor.setWordWrap(self.wrapEnabled)
        editor.setSyntaxHighlightingEnabled(self.syntaxHighlightingEnabled)
        editor.setContent(content)
        self.notebook.add(editor, text=title)
        tabId = str(editor)
        self._tabsData[tabId] = TabData(editor=editor, filePath=filePath, originalContent=content)
        self.notebook.select(editor)
        editor.focusEditor()
        self.onTabChanged()

    def _showNotebook(self):
        self.welcomeFrame.grid_remove()
        self.notebook.grid(row=0, column=0, sticky="nsew")

    def _showWelcome(self):
        self.notebook.grid_remove()
        self.welcomeFrame.grid(row=0, column=0, sticky="nsew")
        self.title(WINDOW_TITLE)
        self.positionLabel.configure(text="1:1")

    def _getCurrentTabData(self):
        tabId = self.notebook.select()
        if not tabId:
            return None
        return self._tabsData.get(tabId)

    def _getTabDataByEditor(self, editor):
        return self._tabsData.get(str(editor))

    def _getTabTitle(self, tabData):
        return os.path.basename(tabData.filePath) if tabData.filePath else "untitled"

    def _setTabModified(self, tabData, modified):
        tabTitle = self._getTabTitle(tabData)
        if modified:
            tabTitle += "*"
        self.notebook.tab(tabData.editor, text=tabTitle)

    def _updateWindowTitle(self, tabData=None):
        if tabData is None:
            tabData = self._getCurrentTabData()
        if tabData is None:
            self.title(WINDOW_TITLE)
            return
        fileName = self._getTabTitle(tabData)
        isModified = tabData.editor.getContent() != tabData.originalContent
        self.title(f"{WINDOW_TITLE} - {fileName}{' *' if isModified else ''}")

    def newFile(self):
        self.createNewTab()

    def openFile(self):
        filePath = filedialog.askopenfilename(title="Open File", filetypes=[("All Files", "*")])
        if not filePath:
            return
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as error:
            messagebox.showerror("Error", f"Could not open file: {error}")
            return
        self.createNewTab(os.path.basename(filePath), filePath, content)

    def _saveTabData(self, tabData):
        if not tabData.filePath:
            return self._saveTabDataAs(tabData)
        try:
            content = tabData.editor.getContent()
            with open(tabData.filePath, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as error:
            messagebox.showerror("Error", f"Could not save file: {error}")
            return False
        tabData.originalContent = content
        self._setTabModified(tabData, False)
        self._updateWindowTitle(tabData)
        return True

    def _saveTabDataAs(self, tabData):
        filePath = filedialog.asksaveasfilename(
            title="Save File As",
            filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*")],
        )
        if not filePath:
            return False
        tabData.filePath = filePath
        return self._saveTabData(tabData)

    def saveFile(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            self._saveTabData(tabData)

    def saveAsFile(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            self._saveTabDataAs(tabData)

    def onTextChanged(self, editor):
        tabData = self._getTabDataByEditor(editor)
        if tabData is None:
            return
        isModified = editor.getContent() != tabData.originalContent
        self._setTabModified(tabData, isModified)
        if self._getCurrentTabData() == tabData:
            self._updateWindowTitle(tabData)

    def onCursorMoved(self, editor):
        lineNumber, columnNumber = editor.getCursorLineColumn()
        self.positionLabel.configure(text=f"{lineNumber}:{columnNumber}")

    def onTabChanged(self, event=None):
        tabData = self._getCurrentTabData()
        if tabData is None:
            return
        self._updateWindowTitle(tabData)
        self.onCursorMoved(tabData.editor)
        tabData.editor.focusEditor()

    def closeCurrentTab(self):
        tabData = self._getCurrentTabData()
        if tabData is None:
            return True
        if not self._confirmSaveIfNeeded(tabData):
            return False
        tabId = str(tabData.editor)
        self.notebook.forget(tabData.editor)
        self._tabsData.pop(tabId, None)
        if not self._tabsData:
            self._showWelcome()
        return True

    def _confirmSaveIfNeeded(self, tabData):
        if tabData.editor.getContent() == tabData.originalContent:
            return True
        fileName = self._getTabTitle(tabData)
        choice = messagebox.askyesnocancel("Unsaved Changes", f"Save changes to {fileName}?")
        if choice is None:
            return False
        if choice:
            return self._saveTabData(tabData)
        return True

    def close(self):
        for tabId in list(self._tabsData):
            self.notebook.select(tabId)
            tabData = self._tabsData[tabId]
            if not self._confirmSaveIfNeeded(tabData):
                return
        self.destroy()

    def toggleAutoIndent(self):
        self.autoIndentEnabled = self.autoIndentVar.get()
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.autoIndentEnabled = self.autoIndentEnabled

    def toggleLineNumbers(self):
        self.lineNumbersEnabled = self.lineNumbersVar.get()
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.setLineNumbersEnabled(self.lineNumbersEnabled)

    def toggleAutoPairing(self):
        self.autoPairingEnabled = self.autoPairingVar.get()
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.autoPairingEnabled = self.autoPairingEnabled

    def toggleWrap(self):
        self.wrapEnabled = self.wrapVar.get()
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.setWordWrap(self.wrapEnabled)

    def toggleSyntaxHighlighting(self):
        self.syntaxHighlightingEnabled = self.syntaxHighlightingVar.get()
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.setSyntaxHighlightingEnabled(self.syntaxHighlightingEnabled)

    def undo(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.undo()

    def redo(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.redo()

    def cut(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.cut()

    def copy(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.copy()

    def paste(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            tabData.editor.paste()

    def selectAll(self):
        tabData = self._getCurrentTabData()
        if tabData is not None:
            return tabData.editor.selectAll()
        return None

    def find(self):
        tabData = self._getCurrentTabData()
        if tabData is None:
            return
        query = self._askSimpleString("Find", "Find:")
        if not query:
            return
        startIndex = tabData.editor.text.search(query, "insert", stopindex="end", nocase=False)
        if not startIndex:
            startIndex = tabData.editor.text.search(query, "1.0", stopindex="end", nocase=False)
        if startIndex:
            endIndex = f"{startIndex}+{len(query)}c"
            tabData.editor.text.tag_remove("sel", "1.0", "end")
            tabData.editor.text.tag_add("sel", startIndex, endIndex)
            tabData.editor.text.mark_set("insert", endIndex)
            tabData.editor.text.see(startIndex)
        else:
            messagebox.showinfo("Find", f"Could not find '{query}'.")

    def replace(self):
        tabData = self._getCurrentTabData()
        if tabData is None:
            return
        query = self._askSimpleString("Replace", "Find:")
        if not query:
            return
        replacement = self._askSimpleString("Replace", "Replace with:")
        if replacement is None:
            return
        content = tabData.editor.getContent()
        tabData.editor.setContent(content.replace(query, replacement, 1))
        self.onTextChanged(tabData.editor)

    def _askSimpleString(self, title, prompt):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text=prompt).pack(padx=12, pady=(12, 4))
        entry = ttk.Entry(dialog, width=40)
        entry.pack(padx=12, pady=4)
        result = {"value": None}

        def submit():
            result["value"] = entry.get()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        buttonFrame = ttk.Frame(dialog)
        buttonFrame.pack(pady=(4, 12))
        ttk.Button(buttonFrame, text="Cancel", command=cancel).pack(side="left", padx=4)
        ttk.Button(buttonFrame, text="OK", command=submit).pack(side="left", padx=4)
        entry.bind("<Return>", lambda event: submit())
        entry.focus_set()
        self.wait_window(dialog)
        return result["value"]

    def toggleBottomPanel(self):
        self.bottomPanelVisible = not self.bottomPanelVisible
        if self.bottomPanelVisible:
            self.bottomPanel.grid(row=1, column=0, sticky="ew")
        else:
            self.bottomPanel.grid_remove()

    def toggleFullScreen(self):
        self.fullScreenEnabled = not self.fullScreenEnabled
        self.attributes("-fullscreen", self.fullScreenEnabled)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
