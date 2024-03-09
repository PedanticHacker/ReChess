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

        self.setShowGrid(False)
        self.setModel(table_model)
        self.setTabKeyNavigation(False)
        self.setFixedSize(QSize(300, 500))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self._table_model = self.model()
        self._selection_model = self.selectionModel()

        self._table_model.layoutChanged.connect(self.scrollToBottom)
        self._selection_model.selectionChanged.connect(
            self.on_selection_changed
        )

    def select_previous_item(self) -> None:
        """Select the previous notation item in the table."""
        if not self._selection_model.hasSelection():
            last_index = self._table_model.index(
                self._table_model.rowCount() - 1,
                0,
            )
            self._selection_model.setCurrentIndex(
                last_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
            return

        index = self._selection_model.currentIndex()
        previous_row = index.row() - (index.column() == 0)
        previous_column = 0 if index.column() == 1 else 1

        if previous_row >= 0:
            previous_index = self._table_model.index(
                previous_row,
                previous_column,
            )
            self._selection_model.setCurrentIndex(
                previous_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def select_next_item(self) -> None:
        """Select the next notation item in the table."""
        if not self._selection_model.hasSelection():
            last_index = self._table_model.index(
                self._table_model.rowCount() - 1,
                0,
            )
            self._selection_model.setCurrentIndex(
                last_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
            return

        index = self._selection_model.currentIndex()
        next_row = index.row() + (index.column() == 1)
        next_column = (index.column() + 1) % 2

        if next_row < self._table_model.rowCount():
            next_index = self._table_model.index(next_row, next_column)
            self._selection_model.setCurrentIndex(
                next_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
        else:
            return

    @Slot()
    def on_selection_changed(self) -> None:
        """Draw the position when the selected move has been played."""
        current_index = self._selection_model.currentIndex()

        if current_index.isValid():
            data = self._table_model.data(current_index)
            print(f"The data in the cell is: {data}")
