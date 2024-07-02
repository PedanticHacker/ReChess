from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView


class TableView(QTableView):
    """A view for displaying notation items in a 2-column table."""

    item_selected: Signal = Signal(int)

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setModel(table_model)

        self.setShowGrid(False)
        self.setFixedSize(200, 500)
        self.setTabKeyNavigation(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.model().layoutChanged.connect(self.scrollToBottom)
        self.selectionModel().currentChanged.connect(self.on_current_changed)

    def select_last_item(self) -> None:
        """Select the last notation item."""
        last_row: int = self.model().rowCount() - 1
        last_column: int = 1 if self.model().index(last_row, 1).data() else 0
        last_model_index: QModelIndex = self.model().index(last_row, last_column)
        self.select_model_index(last_model_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        self.select_model_index(self.get_previous_model_index())

    def select_next_item(self) -> None:
        """Select the next notation item."""
        self.select_model_index(self.get_next_model_index())

    def select_first_item(self) -> None:
        """Select the first notation item."""
        first_model_index = self.model().index(0, 0)
        self.select_model_index(first_model_index)

    def get_previous_model_index(self) -> QModelIndex:
        """Get a model index of the previous notation item."""
        if self.current_ply_index > -1:
            previous_row, previous_column = divmod(self.current_ply_index - 1, 2)
            return self.model().index(previous_row, previous_column)

    def get_next_model_index(self) -> QModelIndex:
        """Get a model index of the next notation item."""
        if self.current_ply_index == -1:
            return self.first_index()

        next_row, next_column = divmod(self.current_ply_index + 1, 2)
        return self.model().index(next_row, next_column)

    def select_model_index(self, model_index: QModelIndex) -> None:
        """Select a notation item with the `model_index`."""
        self.selectionModel().setCurrentIndex(
            model_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    @property
    def ply_index(self) -> int:
        """Get the index of a ply (i.e., a half-move)."""
        current_model_index: QModelIndex = self.selectionModel().currentIndex()
        return 2 * current_model_index.row() + current_model_index.column()
