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
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def select_prelast_item(self) -> None:
        """Select an item before the last."""
        model: QAbstractItemModel = self.model()

        last_row: int = model.rowCount() - 1
        prelast_row: int = last_row - 1
        first_column: int = 0
        last_column: int = 1

        last_index: QModelIndex = model.index(last_row, last_column)
        first_column_index: QModelIndex = model.index(last_row, first_column)
        second_column_index: QModelIndex = model.index(prelast_row, last_column)
        prelast_index: QModelIndex = (
            first_column_index if self.has_data(last_index) else second_column_index
        )

        self.select(prelast_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item by selecting its index."""
        previous_index: QModelIndex = self.previous_index()

        if not self.has_selection():
            self.select_prelast_item()
            return

        if self.has_data(previous_index):
            self.select(previous_index)
        else:
            self.clearFocus()
            self.clearSelection()
            self.item_selected.emit(-1)

    def select_next_item(self) -> None:
        """Select the next notation item by selecting its index."""
        next_index: QModelIndex = self.next_index()

        if self.has_data(next_index):
            self.select(next_index)

    def first_index(self) -> QModelIndex:
        """Get an index of the first notation item."""
        return self.model().index(0, 0)

    def previous_index(self) -> QModelIndex:
        """Get an index of the previous item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        previous_row, previous_column = divmod(self.sequential_index - 1, 2)
        new_index: QModelIndex = self.model().index(previous_row, previous_column)

        return new_index

    def next_index(self) -> QModelIndex:
        """Get an index of the next item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        next_row, next_column = divmod(self.sequential_index + 1, 2)
        new_index: QModelIndex = self.model().index(next_row, next_column)

        return new_index

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
