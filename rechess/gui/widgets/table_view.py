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
        self.select_item_with(last_model_index)

    def select_previous_item(self) -> None:
        """Select the previous notation item."""
        self.select_item_with(self.previous_index())

    def select_next_item(self) -> None:
        """Select the next notation item."""
        self.select_item_with(self.next_index())

    def first_index(self) -> QModelIndex:
        """Get a model index of the first notation item."""
        return self.model().index(0, 0)

    def previous_index(self) -> QModelIndex:
        """Get a model index of the previous notation item."""
        if self.current_ply_index > -1:
            previous_row, previous_column = divmod(self.current_ply_index - 1, 2)
            return self.model().index(previous_row, previous_column)

        return QModelIndex()

    def next_index(self) -> QModelIndex:
        """Get a model index of the next notation item."""
        if self.current_ply_index == -1:
            return self.first_index()

        next_row, next_column = divmod(self.current_ply_index + 1, 2)
        return self.model().index(next_row, next_column)

    def select_item_with(self, model_index: QModelIndex) -> None:
        """Select a notation item with the `model_index`."""
        self.selectionModel().setCurrentIndex(
            model_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    @property
    def current_ply_index(self) -> int:
        """Get an index of the current ply (i.e., a half-move)."""
        current_index: QModelIndex = self.selectionModel().currentIndex()
        return (
            2 * current_index.row() + current_index.column()
            if current_index.isValid()
            else -1
        )

    @Slot()
    def on_current_changed(self) -> None:
        """Emit the current ply index of a selected notation item."""
        self.item_selected.emit(self.current_ply_index)
