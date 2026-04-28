import sys
import objc
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer

# Import only on macOS
if sys.platform == "darwin":
    from AppKit import NSApplication, NSToolbar, NSToolbarItem, NSImage, NSObject

    # 1. Create a PURE Objective-C delegate class
    # Do NOT inherit from QMainWindow or any Qt class here.
    class ToolbarDelegate(NSObject):
        def toolbarAllowedItemIdentifiers_(self, toolbar):
            return ["AddBtn", "NSToolbarFlexibleSpaceItemIdentifier"]

        def toolbarDefaultItemIdentifiers_(self, toolbar):
            return ["AddBtn", "NSToolbarFlexibleSpaceItemIdentifier"]

        def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(self, toolbar, identifier, flag):
            item = NSToolbarItem.alloc().initWithItemIdentifier_(identifier)
            if identifier == "AddBtn":
                item.setLabel_("Add Item")
                item.setImage_(NSImage.imageNamed_("NSAddTemplate"))
                item.setTarget_(self)
                # Signature 'v@:@' is critical for Apple Silicon stability
                item.setAction_(objc.selector(self.onNativeClick_, signature=b"v@:@"))
            return item

        @objc.python_method
        def set_callback(self, func):
            self.callback = func

        def onNativeClick_(self, sender):
            if hasattr(self, 'callback'):
                self.callback()

class NativeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.unique_id = "MyNativeToolbarApp_v1"
        self.setWindowTitle(self.unique_id)
        self.resize(600, 400)
        self.Push = QPushButton("Native NSToolbar (Signal 4 Fixed)")
        self.setCentralWidget(self.Push)

        # Initialize the separate delegate
        if sys.platform == "darwin":
            self.native_delegate = ToolbarDelegate.alloc().init()
            self.native_delegate.set_callback(self.on_toolbar_click)
            # Short delay to let the OS register the window
            QTimer.singleShot(200, self.attach_toolbar)

    def attach_toolbar(self):
        app = NSApplication.sharedApplication()
        for window in app.windows():
            if window.title() == self.unique_id:
                toolbar = NSToolbar.alloc().initWithIdentifier_("MainToolbar")
                toolbar.setDelegate_(self.native_delegate)
                window.setToolbar_(toolbar)
                self.setWindowTitle("Native Toolbar App")
                break

    def on_toolbar_click(self):
        print("Success! Native toolbar button clicked without crashing.")

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    app.setStyle("Android")
    win = NativeApp()
    win.show()
    sys.exit(app.exec())
