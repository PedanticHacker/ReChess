from typing import Any

from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QAbstractTableModel,
    QPersistentModelIndex,
)

from rechess.core import ChessGame


class TableModel(QAbstractTableModel):
    """The model of a table for chess notation items."""

    def __init__(self) -> None:
        super().__init__()

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Prepare data of the items for the display role."""
        if role == Qt.ItemDataRole.DisplayRole:
            notation_item_index: int = 2 * index.row() + index.column()

            if 0 <= notation_item_index < len(ChessGame.notation):
                return ChessGame.notation[notation_item_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Make items enabled and selectable if there is data."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Add rows for the table dynamically."""
        notation_items: int = len(ChessGame.notation)
        return (notation_items // 2) + 1

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Add two columns for the table."""
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
