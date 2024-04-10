from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    Signal,
    QModelIndex,
    QAbstractTableModel,
    QItemSelectionModel,
)

SELECT: QItemSelectionModel.SelectionFlag = (
    QItemSelectionModel.SelectionFlag.ClearAndSelect
)


class TableView(QTableView):
    """A view for showing notation items in a 2-column table."""

    index_selected: Signal = Signal(int)

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
        """Select the notation item before the last."""
        last_row = self.model().rowCount() - 1
        second_column_index = self.model().index(last_row, 1)
        second_column_data = self.model().data(second_column_index)
        row = last_row if second_column_data else last_row - 1
        column = 0 if second_column_data else 1
        prelast_item_index = self.model().index(row, column)
        self.selectionModel().setCurrentIndex(prelast_item_index, SELECT)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        if not self.has_selection() and self.linear_index != -1:
            self.select_prelast_item()
            return

        previous_index = self.get_previous_index()

        if previous_index.isValid():
            self.selectionModel().setCurrentIndex(previous_index, SELECT)

    def select_next_item(self) -> None:
        """Select the next notation item."""
        if not self.has_selection():
            first_index = self.model().index(0, 0)
            self.selectionModel().setCurrentIndex(first_index, SELECT)
            return

        next_index: QModelIndex = self.get_next_index()

        if self.model().data(next_index):
            self.selectionModel().setCurrentIndex(next_index, SELECT)

    def get_previous_index(self) -> QModelIndex:
        """Get the QModelIndex of the previous item, if valid."""
        if self.linear_index < 0:
            return QModelIndex()

        previous_row, previous_column = divmod(self.linear_index - 1, 2)
        return self.model().index(previous_row, previous_column)

    def get_next_index(self) -> QModelIndex:
        """Get the QModelIndex of the next item, if valid."""
        next_row, next_column = divmod(self.linear_index + 1, 2)

        if next_row >= self.model().rowCount():
            return QModelIndex()

        return self.model().index(next_row, next_column)

    def has_selection(self) -> bool:
        """Check whether there's any notation item that's selected."""
        return self.selectionModel().hasSelection()

    @property
    def linear_index(self) -> int:
        """Get a linear index of the currently selected item."""
        current_index = self.selectionModel().currentIndex()

        if not current_index.isValid():
            return -1

        return 2 * current_index.row() + current_index.column()

    @Slot()
    def on_selection_changed(self) -> None:
        """Emit the selected notation item's linear index."""
        if self.has_selection():
            self.index_selected.emit(self.linear_index)
        else:
            self.index_selected.emit(-1)
