"""Tab-based notebook widget for managing multiple editor tabs (PySide6 edition)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QPaintEvent, QFontMetrics, QPolygon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from const.theme import (
    TAB_STRIP_BG,
    TAB_SELECTED_BG,
    TAB_UNSELECTED_BG,
    TAB_BORDER,
    TAB_SELECTED_TEXT,
    TAB_UNSELECTED_TEXT,
    TAB_SELECTED_CLOSE_HOVER_BG,
    TAB_UNSELECTED_CLOSE_HOVER_BG,
    TAB_SEPARATOR,
)


class TabScrollArrow(QWidget):
    """A scroll arrow button for the tab bar."""

    clicked = Signal(bool)

    def __init__(self, parent: QWidget, left: bool = True):
        super().__init__(parent)
        self.left = left
        self._is_hovered = False
        self.setFixedWidth(20)
        self.setMouseTracking(True)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()
        center_y = height // 2

        if self._is_hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(TAB_UNSELECTED_CLOSE_HOVER_BG))
            painter.drawRect(0, 0, width, height)

        painter.setPen(QColor(TAB_UNSELECTED_TEXT))
        painter.setBrush(QColor(TAB_UNSELECTED_TEXT))

        if self.left:
            points = [
                (width - 6, center_y - 4),
                (width - 10, center_y),
                (width - 6, center_y + 4),
            ]
        else:
            points = [
                (6, center_y - 4),
                (10, center_y),
                (6, center_y + 4),
            ]
        polygon = QPolygon([QPoint(x, y) for x, y in points])
        painter.drawPolygon(polygon)
        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._is_hovered:
            self._is_hovered = True
            self.update()

    def leaveEvent(self, event) -> None:
        if self._is_hovered:
            self._is_hovered = False
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.left)


class JereIDETab(QWidget):
    """A single tab widget with a close button."""

    clicked = Signal(int)
    close_clicked = Signal(int)

    def __init__(self, parent: QWidget, label: str, index: int, notebook: "JereIDEBook" = None):
        super().__init__(parent)
        self.label = label
        self.index = index
        self.notebook = notebook
        self.is_selected = False
        self.is_modified = False
        self._is_close_hovered = False
        self._is_tab_hovered = False
        self._text_right = 0

        self.setFixedHeight(30)
        self.setMouseTracking(True)
        self._update_width()

    def _update_width(self):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.label)
        self.setMinimumWidth(text_width + 50)

    def set_label(self, label: str, is_modified: bool = False):
        self.label = label
        self.is_modified = is_modified
        self._update_width()
        self.update()

    def set_modified(self, modified: bool):
        self.is_modified = modified
        self.update()

    @property
    def _close_button_rect(self):
        height = self.height()
        close_y = (height // 2) - 4
        gap = (self.width() - self._text_right) // 2
        return QRect(self._text_right + gap, close_y, 8, 8)



    @property
    def _close_hover_rect(self):
        """Calculate the hover-sensitive area for the close button."""
        rect = self._close_button_rect
        return QRect(rect.x() - 3, rect.y() - 3, rect.width() + 6, rect.height() + 6)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        width = self.width()
        height = self.height()

        background_color = QColor(TAB_SELECTED_BG) if self.is_selected else QColor(TAB_UNSELECTED_BG)
        painter.fillRect(0, 0, width, height - 1, background_color)

        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.label)
        min_left_padding = 21
        text_x = min_left_padding

        font = self.font()
        if self.is_modified:
            font.setItalic(True)
            painter.setFont(font)
        text_color = QColor(TAB_SELECTED_TEXT) if self.is_selected else QColor(TAB_UNSELECTED_TEXT)
        painter.setPen(text_color)
        display_label = f"{self.label}*" if self.is_modified else self.label
        painter.drawText(text_x, (height // 2) + 4, display_label)

        self._text_right = text_x + text_width

        if self._is_close_hovered:
            hover_rect = self._close_hover_rect
            close_hover_color = TAB_SELECTED_CLOSE_HOVER_BG if self.is_selected else TAB_UNSELECTED_CLOSE_HOVER_BG
            hover_bg = QColor(close_hover_color)
            painter.setBrush(hover_bg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hover_rect, 3, 3)

        if self._is_tab_hovered:
            close_rect = self._close_button_rect
            inset = 2
            painter.setPen(text_color)
            painter.drawLine(
                close_rect.x() + inset, close_rect.y() + inset,
                close_rect.x() + close_rect.width() - inset, close_rect.y() + close_rect.height() - inset
            )
            painter.drawLine(
                close_rect.x() + close_rect.width() - inset, close_rect.y() + inset,
                close_rect.x() + inset, close_rect.y() + close_rect.height() - inset
            )

        next_tab = self.notebook._tabs[self.index + 1] if self.notebook and self.index + 1 < len(self.notebook._tabs) else None
        if not self.is_selected:
            painter.setPen(QColor(TAB_SEPARATOR))
            if next_tab and not next_tab.is_selected:
                painter.drawLine(width - 1, 10, width - 1, height - 10)
            elif not next_tab:
                painter.drawLine(width - 1, 10, width - 1, height - 10)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._close_hover_rect.contains(event.pos()):
                self.close_clicked.emit(self.index)
            else:
                self.clicked.emit(self.index)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        was_close_hovered = self._is_close_hovered
        was_tab_hovered = self._is_tab_hovered
        self._is_close_hovered = self._close_hover_rect.contains(event.pos())
        self._is_tab_hovered = True
        if was_close_hovered != self._is_close_hovered or was_tab_hovered != self._is_tab_hovered:
            self.update()

    def leaveEvent(self, event) -> None:
        self._is_close_hovered = False
        self._is_tab_hovered = False
        self.update()


class JereIDEBook(QWidget):
    """A notebook widget that manages multiple tabs with closeable tab headers."""

    page_changed = Signal(int)
    page_close_requested = Signal(int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._tabs: list[JereIDETab] = []
        self._current_selection = -1
        self._scroll_offset = 0

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._tab_bar_widget = QFrame()
        self._tab_bar_widget.setFixedHeight(30)
        self._tab_bar_widget.setStyleSheet(
            f"QFrame {{ background-color: {TAB_STRIP_BG}; border-bottom: 1px solid {TAB_BORDER}; }}"
        )
        self._tab_bar_layout = QHBoxLayout(self._tab_bar_widget)
        self._tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_bar_layout.setSpacing(0)

        self._left_arrow = TabScrollArrow(self._tab_bar_widget, True)
        self._left_arrow.clicked.connect(self._on_scroll_arrow_clicked)
        self._tab_bar_layout.addWidget(self._left_arrow)

        self._right_arrow = TabScrollArrow(self._tab_bar_widget, False)
        self._right_arrow.clicked.connect(self._on_scroll_arrow_clicked)
        self._tab_bar_layout.addWidget(self._right_arrow)

        self._tab_bar_layout.addStretch()

        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setStyleSheet("QStackedWidget { border: none; background-color: white; }")

        main_layout.addWidget(self._tab_bar_widget)
        main_layout.addWidget(self._stacked_widget, 1)

    def GetSelection(self) -> int:
        """Return the currently selected page index, or -1."""
        return self._current_selection

    def GetPage(self, index: int) -> QWidget | None:
        """Return the page widget at the given index."""
        if 0 <= index < self._stacked_widget.count():
            return self._stacked_widget.widget(index)
        return None

    def AddPage(self, page_widget: QWidget, title: str, select: bool = False) -> bool:
        """Add a new page to the notebook."""
        index = len(self._tabs)
        tab = JereIDETab(self._tab_bar_widget, title, index, self)
        tab.clicked.connect(self._on_tab_clicked)
        tab.close_clicked.connect(self._on_tab_close_clicked)

        self._tabs.append(tab)
        insert_position = self._tab_bar_layout.count() - 1
        self._tab_bar_layout.insertWidget(insert_position, tab)

        self._stacked_widget.addWidget(page_widget)

        if self._current_selection == -1 or select:
            self.SelectTab(index)

        self._update_arrow_states()
        self._tab_bar_widget.show()
        return True

    def SetPageText(self, index: int, title: str) -> bool:
        """Set the title of the tab at the given index."""
        if 0 <= index < len(self._tabs):
            self._tabs[index].set_label(title)
            return True
        return False

    def SetPageModified(self, index: int, modified: bool) -> bool:
        """Set the modified state of the tab at the given index."""
        if 0 <= index < len(self._tabs):
            self._tabs[index].set_modified(modified)
            return True
        return False

    def GetPageIndex(self, page: QWidget) -> int:
        """Return the index of the given page, or -1."""
        index = self._stacked_widget.indexOf(page)
        return index if index >= 0 else -1

    def SetSelection(self, index: int) -> int:
        """Set the selection to the page at the given index. Returns previous selection."""
        old_selection = self._current_selection
        self.SelectTab(index)
        return old_selection

    def GetPageCount(self) -> int:
        """Return the number of pages."""
        return len(self._tabs)

    def DeletePage(self, index: int) -> None:
        """Delete the page at the given index."""
        if 0 <= index < len(self._tabs):
            self.page_close_requested.emit(index)

    def SelectTab(self, index: int) -> None:
        """Select the tab at the given index."""
        for i, tab in enumerate(self._tabs):
            tab.is_selected = (i == index)
            tab.update()

        if 0 <= index < self._stacked_widget.count():
            self._stacked_widget.setCurrentIndex(index)
            self._current_selection = index
            self.page_changed.emit(index)

        self._update_arrow_states()

    def CloseTab(self, index: int) -> None:
        """Close and remove the tab at the given index."""
        if index < 0 or index >= len(self._tabs):
            return

        tab = self._tabs.pop(index)
        page = self._stacked_widget.widget(index)

        self._tab_bar_layout.removeWidget(tab)
        tab.deleteLater()
        self._stacked_widget.removeWidget(page)
        page.deleteLater()

        for i, remaining_tab in enumerate(self._tabs):
            remaining_tab.index = i

        if self._current_selection >= len(self._tabs):
            self._current_selection = len(self._tabs) - 1

        if self._tabs:
            self.SelectTab(self._current_selection)
        else:
            self._current_selection = -1
            self._tab_bar_widget.hide()

        self._update_arrow_states()

    def _on_tab_clicked(self, index: int) -> None:
        """Handle tab click events."""
        self.SelectTab(index)

    def _on_tab_close_clicked(self, index: int) -> None:
        """Handle tab close button click events."""
        self.page_close_requested.emit(index)

    def _on_scroll_arrow_clicked(self, left: bool) -> None:
        """Handle scroll arrow click events."""
        if not self._tabs:
            return

        current = self._current_selection

        if left:
            if current > 0:
                self.SelectTab(current - 1)
        else:
            if current < len(self._tabs) - 1:
                self.SelectTab(current + 1)

    def _update_arrow_states(self) -> None:
        """Update enabled state of scroll arrows based on current tab position."""
        has_tabs = bool(self._tabs)
        current = self._current_selection

        self._left_arrow.setEnabled(has_tabs and current > 0)
        self._right_arrow.setEnabled(has_tabs and current < len(self._tabs) - 1)
