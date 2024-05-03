from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    Signal,
    QModelIndex,
    QAbstractItemModel,
    QAbstractTableModel,
    QItemSelectionModel,
)


class TableView(QTableView):
    """A view for displaying chess notation items in a 2-column table."""

    item_selected: Signal = Signal(int)

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setModel(table_model)

        self.configure_view()
        self.connect_events_with_handlers()

    def configure_view(self) -> None:
        """Configure the view to non-default settings."""
        self.setShowGrid(False)
        self.setFixedSize(200, 500)
        self.setTabKeyNavigation(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def connect_events_with_handlers(self) -> None:
        """Connect various events with specific handlers."""
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
        """Select the previous notation item."""
        if not self.has_selection():
            self.select_prelast_item()
            return

        self.select(self.previous_index())

    def select_next_item(self) -> None:
        """Select the next notation item by selecting its index."""
        if not self.has_selection():
            self.select(self.first_index())
            return

        self.select(self.next_index())

    def first_index(self) -> QModelIndex:
        """Get an index of the first notation item."""
        return self.model().index(0, 0)

    def previous_index(self) -> QModelIndex:
        """Get an index of the previous item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        previous_row, previous_column = divmod(self.sequential_index - 1, 2)
        new_index: QModelIndex = self.model().index(previous_row, previous_column)

        return new_index if new_index.isValid() else current_index

    def next_index(self) -> QModelIndex:
        """Get an index of the next item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        next_row, next_column = divmod(self.sequential_index + 1, 2)
        new_index: QModelIndex = self.model().index(next_row, next_column)

        return new_index if new_index.isValid() else current_index

    def select(self, index: QModelIndex) -> None:
        """Select a notation item with the `index`."""
        self.selectionModel().setCurrentIndex(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def has_data(self, index: QModelIndex) -> bool:
        """Check whether an item with the `index` has data."""
        return self.model().data(index)

    def has_selection(self) -> bool:
        """Check whether any item is currently selected."""
        return self.selectionModel().hasSelection()

    @property
    def sequential_index(self) -> int:
        """Return the sequential index of a selected item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        return (
            2 * current_index.row() + current_index.column()
            if current_index.isValid()
            else -1
        )

    @Slot(int)
    def on_selection_changed(self) -> None:
        """Emit the sequential index of a selected item."""
        self.item_selected.emit(self.sequential_index)
