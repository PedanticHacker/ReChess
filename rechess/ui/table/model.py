from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class TableModel(QAbstractTableModel):
    """Model for managing SAN moves in two-column table."""

    def __init__(self, san_moves: list[str]) -> None:
        super().__init__()

        self._san_moves: list[str] = san_moves

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return SAN move at `index`."""
        if role == Qt.ItemDataRole.DisplayRole:
            san_move_index: int = 2 * index.row() + index.column()

            if 0 <= san_move_index < len(self._san_moves):
                return self._san_moves[san_move_index]

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        """Return flags as access to SAN move at `index`."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return number of rows needed to display all SAN moves."""
        all_san_moves = len(self._san_moves) + 1
        return all_san_moves // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Return two columns for SAN moves of White and Black."""
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
        """Reset model by clearing all SAN moves."""
        self.beginResetModel()
        self._san_moves.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh view to reflect model changes."""
        self.layoutChanged.emit()
