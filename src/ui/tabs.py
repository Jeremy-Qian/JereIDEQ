"""Tab-based notebook widget for managing multiple editor tabs (PySide6 edition)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QPaintEvent, QFontMetrics
from PySide6.QtWidgets import (
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from const.theme import (
    TAB_SELECTED_BG,
    TAB_UNSELECTED_BG,
    TAB_BORDER,
    TAB_TEXT,
    TAB_CLOSE_HOVER_BG,
)


class JereIDETab(QWidget):
    """A single tab widget with a close button."""

    clicked = Signal(int)
    close_clicked = Signal(int)

    def __init__(self, parent: QWidget, label: str, index: int):
        super().__init__(parent)
        self.label = label
        self.index = index
        self.is_selected = False
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

    def set_label(self, label: str):
        self.label = label
        self._update_width()
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
        painter.fillRect(0, 0, width, height, background_color)

        if not self.is_selected:
            painter.setPen(QColor(TAB_BORDER))
            painter.drawLine(0, height - 1, width - 1, height - 1)
            painter.drawLine(0, 0, 0, height - 1)
            painter.drawLine(width, 0, width, height - 1)
        else:
            painter.setPen(QColor(TAB_BORDER))
            painter.drawLine(0, 0, 0, height - 1)
            painter.drawLine(width, 0, width, height - 1)

        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.label)
        min_left_padding = 21
        text_x = min_left_padding

        painter.setPen(QColor(TAB_TEXT))
        painter.drawText(text_x, (height // 2) + 4, self.label)

        self._text_right = text_x + text_width

        if self._is_close_hovered:
            hover_rect = self._close_hover_rect
            painter.setBrush(QColor(TAB_CLOSE_HOVER_BG))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hover_rect, 3, 3)

        if self._is_tab_hovered:
            close_rect = self._close_button_rect
            inset = 2
            painter.setPen(QColor(TAB_TEXT))
            painter.drawLine(
                close_rect.x() + inset, close_rect.y() + inset,
                close_rect.x() + close_rect.width() - inset, close_rect.y() + close_rect.height() - inset
            )
            painter.drawLine(
                close_rect.x() + close_rect.width() - inset, close_rect.y() + inset,
                close_rect.x() + inset, close_rect.y() + close_rect.height() - inset
            )
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
        self.setStyleSheet("QWidget { border: none; }")
        self._tabs: list[JereIDETab] = []
        self._current_selection = -1

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._tab_bar_widget = QWidget()
        self._tab_bar_layout = QHBoxLayout(self._tab_bar_widget)
        self._tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_bar_layout.setSpacing(0)
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
        tab = JereIDETab(self._tab_bar_widget, title, index)
        tab.clicked.connect(self._on_tab_clicked)
        tab.close_clicked.connect(self._on_tab_close_clicked)

        self._tabs.append(tab)
        insert_position = self._tab_bar_layout.count() - 1
        self._tab_bar_layout.insertWidget(insert_position, tab)

        self._stacked_widget.addWidget(page_widget)

        if self._current_selection == -1 or select:
            self.SelectTab(index)

        return True

    def SetPageText(self, index: int, title: str) -> bool:
        """Set the title of the tab at the given index."""
        if 0 <= index < len(self._tabs):
            self._tabs[index].set_label(title)
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

    def _on_tab_clicked(self, index: int) -> None:
        """Handle tab click events."""
        self.SelectTab(index)

    def _on_tab_close_clicked(self, index: int) -> None:
        """Handle tab close button click events."""
        self.page_close_requested.emit(index)
