from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    QModelIndex,
    QAbstractTableModel,
    QItemSelectionModel,
)


CLEAR_AND_SELECT: QItemSelectionModel.SelectionFlag = (
    QItemSelectionModel.SelectionFlag.ClearAndSelect
)


class TableView(QTableView):
    """A view for showing notation items in a 2-column table."""

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setModel(table_model)

        self._table_model: QAbstractTableModel = table_model
        self._selection_model: QItemSelectionModel = self.selectionModel()

        self.configure_view()
        self.connect_events_with_handlers()

    def configure_view(self) -> None:
        """Configure the view to personal preferences."""
        self.setShowGrid(False)
        self.setFixedSize(300, 500)
        self.setTabKeyNavigation(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def connect_events_with_handlers(self) -> None:
        """Connect various events with specific handlers."""
        self._table_model.layoutChanged.connect(self.scrollToBottom)
        self._selection_model.selectionChanged.connect(self.on_selection_changed)

    def select_previous_item(self) -> None:
        """Select the previous notation item in the table."""
        if not self._selection_model.hasSelection():
            last_row = self._table_model.rowCount() - 1
            last_column = self._table_model.columnCount() - 1
            last_index = self._table_model.index(last_row, last_column)
            self._selection_model.setCurrentIndex(last_index, CLEAR_AND_SELECT)

        current_index = self._selection_model.currentIndex()
        previous_row = current_index.row() - (current_index.column() == 0)
        previous_column = 0 if current_index.column() == 1 else 1

        if previous_row >= 0:
            previous_index = self._table_model.index(previous_row, previous_column)
            self._selection_model.setCurrentIndex(previous_index, CLEAR_AND_SELECT)

    def select_next_item(self) -> None:
        """Select the next notation item in the table."""
        current_index = self._selection_model.currentIndex()
        next_row = current_index.row() + (current_index.column() == 1)
        next_column = (current_index.column() + 1) % 2

        if next_row < self._table_model.rowCount():
            next_index = self._table_model.index(next_row, next_column)
            self._selection_model.setCurrentIndex(next_index, CLEAR_AND_SELECT)

    @Slot()
    def on_selection_changed(self) -> None:
        """Show the position when a notation item has been selected."""
        current_index = self._selection_model.currentIndex()

        if current_index.isValid():
            item_data = self._table_model.data(current_index)
            print(f"The data of the item is: {item_data}")
