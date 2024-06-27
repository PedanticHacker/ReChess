from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Signal,
)
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView


class TableView(QTableView):
    """A view for displaying chess notation items in a 2-column table."""

    item_selected: Signal = Signal(int)

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setModel(table_model)

        self.setShowGrid(False)
        self.setFixedSize(200, 500)
        self.setTabKeyNavigation(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.model().layoutChanged.connect(self.scrollToBottom)

    def select_first_item(self) -> None:
        """Select the first notation item with the first model index."""
        first_index: QModelIndex = self.model().index(0, 0)
        self.selectionModel().setCurrentIndex(
            first_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        self.item_selected.emit(self.sequential_index)

    def select_last_item(self) -> None:
        """Select the last notation item with the last model index."""
        last_row: int = self.model().rowCount() - 1
        last_column: int = 1 if self.model().index(last_row, 1).data() else 0
        last_model_index: QModelIndex = self.model().index(last_row, last_column)
        self.selectionModel().setCurrentIndex(
            last_model_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        self.item_selected.emit(self.sequential_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        previous_index: int = self.sequential_index() - 1
        self.item_selected.emit(previous_index)

    def select_next_item(self) -> None:
        """Select the next notation item."""
        next_index: int = self.sequential_index() + 1
        self.item_selected.emit(next_index)

    def sequential_index(self) -> int:
        """Return the sequential index of a selected notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        return 2 * current_index.row() + current_index.column()
