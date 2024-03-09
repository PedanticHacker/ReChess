from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import (
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

        table_model.layoutChanged.connect(self.scrollToBottom)

    def ensure_selection(self) -> None:
        """Ensure a selection, defaulting to the last notation item."""
        selection_model = self.selectionModel()
        if not selection_model.hasSelection():
            last_row = self.model().rowCount() - 1
            last_column = 1 if last_row >= 0 else 0
            last_index = self.model().index(last_row, last_column)
            selection_model.setCurrentIndex(
                last_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def select_preceding_item(self) -> None:
        """Select the preceding notation item in the table."""
        self.ensure_selection()

        selection_model = self.selectionModel()
        current_index = selection_model.currentIndex()

        if current_index.column() == 0 and current_index.row() > 0:
            new_row = current_index.row() - 1
            new_column = 1
        else:
            new_row = current_index.row()
            new_column = (current_index.column() - 1) % 2

        if new_row >= 0:
            previous_index = self.model().index(new_row, new_column)
            selection_model.setCurrentIndex(
                previous_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def select_following_item(self) -> None:
        """Select the following notation item in the table."""
        self.ensure_selection()

        selection_model = self.selectionModel()
        current_index = selection_model.currentIndex()

        if current_index.column() == 1:
            new_row = current_index.row() + 1
            new_column = 0
        else:
            new_row = current_index.row()
            new_column = (current_index.column() + 1) % 2

        if new_row < self.model().rowCount():
            next_index = self.model().index(new_row, new_column)
            selection_model.setCurrentIndex(
                next_index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
