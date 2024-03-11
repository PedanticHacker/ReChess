from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
    Slot,
    QSize,
    QModelIndex,
    QAbstractTableModel,
    QItemSelectionModel,
)


class TableView(QTableView):
    """A view for showing notation items in a 2-column table."""

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.table_model = table_model

        self.setShowGrid(False)
        self.setModel(table_model)
        self.setTabKeyNavigation(False)
        self.setFixedSize(QSize(300, 500))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_model.layoutChanged.connect(self.scrollToBottom)
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def select_previous_item(self) -> None:
        """Select the previous notation item in the table."""
        if not self.selectionModel().hasSelection():
            last_index = self.table_model.index(self.table_model.rowCount() - 1, 0)
            self.selectionModel().setCurrentIndex(
                last_index,
                QItemSelectionModel.SelectionFlag.Select,
            )
            return

        current_index = self.selectionModel().currentIndex()
        previous_row = current_index.row() - (current_index.column() == 0)
        previous_column = 0 if current_index.column() == 1 else 1

        if previous_row >= 0:
            previous_index = self.table_model.index(previous_row, previous_column)
            self.selectionModel().setCurrentIndex(
                previous_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def select_next_item(self) -> None:
        """Select the next notation item in the table."""
        current_index = self.selectionModel().currentIndex()
        next_row = current_index.row() + (current_index.column() == 1)
        next_column = (current_index.column() + 1) % 2

        if next_row < self.table_model.rowCount():
            next_index = self.table_model.index(next_row, next_column)
            self.selectionModel().setCurrentIndex(
                next_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    @Slot()
    def on_selection_changed(self) -> None:
        """Draw the position when the selected move has been played."""
        current_index = self.selectionModel().currentIndex()

        if current_index.isValid():
            data = self.table_model.data(current_index)
            print(f"The data in the cell is: {data}")
