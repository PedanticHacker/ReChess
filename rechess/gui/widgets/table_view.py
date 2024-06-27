from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
)
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView


class TableView(QTableView):
    """A view for displaying chess notation items in a 2-column table."""

    item_selected: Signal = Signal()

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
        self.select_with_model_index(first_index)

    def select_last_item(self) -> None:
        """Select the last notation item with the last model index."""
        last_row = self.model().rowCount() - 1
        last_column = 1 if self.model().index(last_row, 1).data() else 0
        last_model_index = self.model().index(last_row, last_column)
        self.select_with_model_index(last_model_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        previous_index: QModelIndex = current_index.siblingAtRow(
            current_index.row() - 1
        )
        self.select_with_model_index(previous_index)

    def select_next_item(self) -> None:
        """Select the next notation item."""
        current_index = self.selectionModel().currentIndex()
        next_index = current_index.siblingAtRow(current_index.row() + 1)
        self.select_with_model_index(next_index)

    def select_with_sequential_index(self, sequential_index: int) -> None:
        """Select a notation item with the `sequential_index`."""
        row: int = sequential_index // 2
        column: int = sequential_index % 2
        model_index: QModelIndex = self.model().index(row, column)
        self.select_with_model_index(model_index)

    def select_with_model_index(self, model_index: QModelIndex) -> None:
        """Select a notation item with the `model_index`."""
        self.selectionModel().setCurrentIndex(
            model_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    @property
    def sequential_index(self) -> int:
        """Return the sequential index of a selected notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        return 2 * current_index.row() + current_index.column()
