from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    QModelIndex,
    QAbstractTableModel,
    QItemSelectionModel,
)


class TableView(QTableView):
    """A view for showing notation items in a 2-column table."""

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setModel(table_model)

        self.configure_view()
        self.connect_events_with_handlers()

    def configure_view(self) -> None:
        """Configure the view to personal preferences."""
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

    def select_previous_item(self) -> None:
        """Select the previous notation item in the table."""
        if not self.selectionModel().hasSelection():
            last_row = self.model().rowCount() - 1
            last_column = self.model().columnCount() - 1
            last_index = self.model().index(last_row, last_column)
            self.selectionModel().setCurrentIndex(
                last_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
            return None

        current_index = self.selectionModel().currentIndex()
        previous_row = current_index.row() - (current_index.column() == 0)
        previous_column = 0 if current_index.column() == 1 else 1

        if previous_row >= 0:
            previous_index = self.model().index(previous_row, previous_column)
            self.selectionModel().setCurrentIndex(
                previous_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def select_next_item(self) -> None:
        """Select the next notation item in the table."""
        current_index = self.selectionModel().currentIndex()
        next_row = current_index.row() + (current_index.column() == 1)
        next_column = (current_index.column() + 1) % 2

        if next_row < self.model().rowCount():
            next_index = self.model().index(next_row, next_column)
            self.selectionModel().setCurrentIndex(
                next_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    @Slot()
    def on_selection_changed(self) -> None:
        """Show the position when a notation item has been selected."""
        current_index = self.selectionModel().currentIndex()

        if current_index.isValid():
            item_data = self.model().data(current_index)
            print(f"The data of the item is: {item_data}")
