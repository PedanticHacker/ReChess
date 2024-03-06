from typing import Any

from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QAbstractTableModel,
    QPersistentModelIndex,
)

from rechess.core import Game


class TableModel(QAbstractTableModel):
    """The model of a table for notation items."""

    def __init__(self, notation_items: list[str]) -> None:
        super().__init__()

        self._notation_items = notation_items

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Prepare data of the notation items for display role."""
        if role == Qt.ItemDataRole.DisplayRole:
            notation_item_index: int = 2 * index.row() + index.column()

            if 0 <= notation_item_index < len(self._notation_items):
                return self._notation_items[notation_item_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Make notation items enabled and selectable if there's data."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Count the rows needed for the table."""
        all_notation_items = len(self._notation_items)
        return (all_notation_items + 1) // 2

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
        """Provide data for horizontal and vertical headers."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["White", "Black"][section]

            if orientation == Qt.Orientation.Vertical:
                return section + 1

    def refresh(self) -> None:
        """Refresh the model's layout of notation items."""
        self.layoutChanged.emit()
