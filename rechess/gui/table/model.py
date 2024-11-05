from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class TableModel(QAbstractTableModel):
    """Model for displaying moves in two-column table format."""

    def __init__(self, moves: list[str]) -> None:
        super().__init__()

        self._moves: list[str] = moves

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return move at `index` for default display `role`."""
        if role == Qt.ItemDataRole.DisplayRole:
            move_index: int = 2 * index.row() + index.column()

            if 0 <= move_index < len(self._moves):
                return self._moves[move_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Return flags for enabling and selecting items with moves."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return number of rows needed to display all moves."""
        all_moves = len(self._moves) + 1
        return all_moves // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return two columns for moves of White and Black."""
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
        """Reset model by clearing all moves."""
        self.beginResetModel()
        self._moves.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh view to reflect model changes."""
        self.layoutChanged.emit()
