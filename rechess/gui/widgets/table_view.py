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

        first_column: int = 0
        last_column: int = 1
        last_row: int = model.rowCount() - 1

        if self.has_data(model.index(last_row, last_column)):
            prelast_item_index: QModelIndex = model.index(last_row, last_column)
        else:
            prelast_item_index = model.index(last_row, first_column)

        self.select(prelast_item_index)

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
        previous_row, previous_column = divmod(self.linear_index - 1, 2)
        return self.model().index(previous_row, previous_column)

    def next_index(self) -> QModelIndex:
        """Get an index of the next item."""
        next_row, next_column = divmod(self.linear_index + 1, 2)
        return self.model().index(next_row, next_column)

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
    def linear_index(self) -> int:
        """Return a linear index of the currently selected item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()

        if current_index.isValid():
            return 2 * current_index.row() + current_index.column()

        return -1

    @Slot(int)
    def on_selection_changed(self) -> None:
        """Emit the index of the currently selected row."""
        row_index: int = self.selectionModel().currentIndex().row()
        self.item_selected.emit(row_index)
