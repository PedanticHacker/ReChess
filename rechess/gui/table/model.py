from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class TableModel(QAbstractTableModel):
    """Model for containing chess notation."""

    def __init__(self, notation_items: list[str]) -> None:
        super().__init__()

        self._notation_items: list[str] = notation_items

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return notation items and process them for display role."""
        if role == Qt.ItemDataRole.DisplayRole:
            notation_item_index: int = 2 * index.row() + index.column()

            if 0 <= notation_item_index < len(self._notation_items):
                return self._notation_items[notation_item_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Determine appropriate flag for notation item."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Count rows needed for all notation items."""
        all_notation_items = len(self._notation_items) + 1
        return all_notation_items // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Count fixed set of 2 columns for all notation items."""
        return 2

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Provide data for horizontal and vertical headers."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["White", "Black"][section]

            if orientation == Qt.Orientation.Vertical:
                return section + 1

    def reset(self) -> None:
        """Reset model by clearing all notation items."""
        self.beginResetModel()
        self._notation_items.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh view due to changes in model's layout."""
        self.layoutChanged.emit()
