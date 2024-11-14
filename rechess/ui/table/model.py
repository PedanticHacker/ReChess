from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class TableModel(QAbstractTableModel):
    """Model for managing items in table."""

    def __init__(self, items: list[str]) -> None:
        super().__init__()

        self._items: list[str] = items

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return item at `index`."""
        if role == Qt.ItemDataRole.DisplayRole:
            san_move_index: int = 2 * index.row() + index.column()

            if 0 <= san_move_index < len(self._items):
                return self._items[san_move_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Return flags as access to item at `index`."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return number of rows needed to display all items."""
        all_items = len(self._items) + 1
        return all_items // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return two columns for items."""
        return 2

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return column headers and row numbers."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["White", "Black"][section]

            if orientation == Qt.Orientation.Vertical:
                return section + 1

    def reset(self) -> None:
        """Reset model by clearing all items."""
        self.beginResetModel()
        self._items.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh view to reflect model changes."""
        self.layoutChanged.emit()
