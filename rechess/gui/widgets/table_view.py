from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Signal,
    Slot,
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
        self.model().dataChanged.connect(self.select_last_item)
        self.model().rowsInserted.connect(self.select_last_item)
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def select_last_item(self) -> None:
        """Select the last notation item."""
        last_row = self.model().rowCount() - 1
        last_column = 1 if self.model().index(last_row, 1).data() else 0
        last_index = self.model().index(last_row, last_column)
        self.select(last_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item by selecting its index."""
        if not self.has_selection():
            self.select_first_item()
            return

        previous_index: QModelIndex = self.previous_index()
        self.select(previous_index)

    def select_next_item(self) -> None:
        """Select the next notation item by selecting its index."""
        if not self.has_selection():
            self.select_first_item()
            return

        next_index: QModelIndex = self.next_index()
        self.select(next_index)

    def select_first_item(self) -> None:
        """Select the first notation item by selecting its index."""
        first_index = self.model().index(0, 0)
        self.select(first_index)

    def previous_index(self) -> QModelIndex:
        """Get an index of the previous notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        previous_row, previous_column = divmod(self.sequential_index - 1, 2)
        return self.model().index(previous_row, previous_column)

    def next_index(self) -> QModelIndex:
        """Get an index of the next notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        next_row, next_column = divmod(self.sequential_index + 1, 2)
        return self.model().index(next_row, next_column)

    def select(self, index: QModelIndex) -> None:
        """Select a notation item with the `index`."""
        self.selectionModel().setCurrentIndex(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def has_data(self, index: QModelIndex) -> bool:
        """Check whether an item with the `index` has data."""
        return bool(self.model().data(index))

    def has_selection(self) -> bool:
        """Check whether any item is currently selected."""
        return self.selectionModel().hasSelection()

    @property
    def sequential_index(self) -> int:
        """Return the sequential index of a selected notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        return 2 * current_index.row() + current_index.column()

    @Slot(int)
    def on_selection_changed(self) -> None:
        """Emit the sequential index of a selected notation item."""
        self.item_selected.emit(self.sequential_index)
