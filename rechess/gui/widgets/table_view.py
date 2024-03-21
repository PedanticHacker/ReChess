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

    index_selected: Signal = Signal(int)

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
        if not self.has_selection():
            last_row: int = self.model().rowCount() - 1
            second_column_data: str | None = self.model().data(
                self.model().index(last_row, 1)
            )
            row: int = last_row if second_column_data else last_row - 1
            column: int = 0 if second_column_data else 1
            index: QModelIndex = self.model().index(row, column)
            self.selectionModel().setCurrentIndex(
                index,
                QItemSelectionModel.SelectionFlag.Select,
            )
        else:
            current_index: QModelIndex = self.selectionModel().currentIndex()
            linear_index: int = 2 * current_index.row() + current_index.column() - 1
            previous_row: int = linear_index // 2
            previous_column: int = linear_index % 2

            if previous_row >= 0:
                previous_index: QModelIndex = self.model().index(
                    previous_row,
                    previous_column,
                )
                self.selectionModel().setCurrentIndex(
                    previous_index,
                    QItemSelectionModel.SelectionFlag.ClearAndSelect,
                )

    def select_next_item(self) -> None:
        """Select the next notation item in the table."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        linear_index: int = 2 * current_index.row() + current_index.column() + 1
        next_row: int = linear_index // 2
        next_column: int = linear_index % 2
        next_index: QModelIndex = self.model().index(next_row, next_column)

        if next_row < self.model().rowCount() and self.model().data(next_index):
            self.selectionModel().setCurrentIndex(
                next_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def has_selection(self) -> bool:
        """Check whether there's a selected notation item in the table."""
        return self.selectionModel().hasSelection()

    @property
    def linear_index(self) -> int:
        """Get a linear index of the currently selected item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        linear_index: int = 2 * current_index.row() + current_index.column()
        return linear_index

    @Slot()
    def on_selection_changed(self) -> None:
        """Emit the linear index of the selected notation item."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        linear_index: int = 2 * current_index.row() + current_index.column()
        self.index_selected.emit(linear_index)
