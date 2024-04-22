from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    Signal,
    QModelIndex,
    QAbstractTableModel,
    QItemSelectionModel,
)


class TableView(QTableView):
    """A view for showing notation items in a 2-column table."""

    item_selected: Signal = Signal()

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
        """Select the notation item before the last one."""
        last_row: int = self.model().rowCount() - 1
        second_column_index: QModelIndex = self.model().index(last_row, 1)
        has_second_column_data: bool = self.has_data(second_column_index)
        row: int = last_row if has_second_column_data else last_row - 1
        column: int = 0 if has_second_column_data else 1
        prelast_item_index: QModelIndex = self.model().index(row, column)
        self.select(prelast_item_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        if not self.has_selection():
            self.select_prelast_item()
            return

        previous_index: QModelIndex = self.get_previous_index()
        self.select(previous_index)

    def select_next_item(self) -> None:
        """Select the next notation item."""
        if not self.has_selection():
            first_index: QModelIndex = self.get_first_index()
            self.select(first_index)
            return

        next_index: QModelIndex = self.get_next_index()
        self.select(next_index)

    def get_first_index(self) -> QModelIndex:
        """Get an index of the first notation item."""
        return self.model().index(0, 0)

    def get_previous_index(self) -> QModelIndex:
        """Get a QModelIndex of the previous item."""
        previous_row, previous_column = divmod(self.linear_index - 1, 2)
        return self.model().index(previous_row, previous_column)

    def get_next_index(self) -> QModelIndex:
        """Get a QModelIndex of the next item."""
        next_row, next_column = divmod(self.linear_index + 1, 2)
        return self.model().index(next_row, next_column)

    def select(self, index: QModelIndex) -> None:
        """Select a notation item with the `index`."""
        self.selectionModel().setCurrentIndex(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def has_data(self, index: QModelIndex) -> bool:
        """Check whether a notation item with the `index` has data."""
        return self.model().data(index)

    def has_selection(self) -> bool:
        """Check whether any notation item is currently selected."""
        return self.selectionModel().hasSelection()

    @property
    def linear_index(self) -> int:
        """Get the linear index of a selected notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        if current_index.isValid():
            return 2 * current_index.row() + current_index.column()

        return -1

    @Slot()
    def on_selection_changed(self) -> None:
        """Emit the linear index of a selected notation item."""
        self.item_selected.emit(self.linear_index)
