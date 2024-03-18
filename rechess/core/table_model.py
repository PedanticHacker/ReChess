from typing import Any

from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QAbstractTableModel,
    QPersistentModelIndex,
)


class TableModel(QAbstractTableModel):
    """The model of a table for chess notation."""

    def __init__(self, data: list[str]) -> None:
        super().__init__()

        self._data = data

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Get chess notation data and process it for display role."""
        if role == Qt.ItemDataRole.DisplayRole:
            item_index: int = 2 * index.row() + index.column()

            if 0 <= item_index < len(self._data):
                return self._data[item_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Set flags for table cells to be enabled and selectable."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Count the rows needed for the table."""
        all_data = len(self._data) + 1
        return all_data // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Count a fixed set of 2 columns for the table."""
        return 2

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Get the data for horizontal and vertical headers."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["White", "Black"][section]

            if orientation == Qt.Orientation.Vertical:
                return section + 1

    def reset(self) -> None:
        """Reset the model by clearing all the data."""
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh the view due to changes in the model's layout."""
        self.layoutChanged.emit()
