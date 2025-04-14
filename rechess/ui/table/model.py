from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class TableModel(QAbstractTableModel):
    """Model for storing move history in SAN format."""

    def __init__(self, plies: list[str]) -> None:
        super().__init__()

        self._plies: list[str] = plies

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Get SAN representation for ply at `index`."""
        if role == Qt.ItemDataRole.DisplayRole:
            ply_index: int = 2 * index.row() + index.column()

            if 0 <= ply_index < len(self._plies):
                return self._plies[ply_index]

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        """Get interaction state based on data existence at `index`."""
        if self.data(index):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.NoItemFlags

    def rowCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Get count of rows needed for representing moves."""
        all_plies: int = len(self._plies) + 1
        return all_plies // 2

    def columnCount(
        self,
        index: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        """Get fixed count of two columns for White/Black plies."""
        return 2

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Get 'White'/'Black' column labels and numbers for rows."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["White", "Black"][section]

            if orientation == Qt.Orientation.Vertical:
                return section + 1

    def reset(self) -> None:
        """Clear stored move history data from model."""
        self.beginResetModel()
        self._plies.clear()
        self.endResetModel()

    def refresh_view(self) -> None:
        """Refresh view to reflect model changes."""
        self.layoutChanged.emit()
