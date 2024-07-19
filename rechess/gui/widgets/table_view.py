from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView


class TableView(QTableView):
    """View for displaying notation items in 2-column table."""

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
        """Select last notation item."""
        last_row: int = self.model().rowCount() - 1
        last_column: int = 1 if self.model().index(last_row, 1).data() else 0
        last_model_index: QModelIndex = self.model().index(last_row, last_column)
        self.select_model_index(last_model_index)

    def select_previous_item(self) -> None:
        """Select previous notation item."""
        self.select_model_index(self.previous_model_index)

    def select_next_item(self) -> None:
        """Select next notation item."""
        if self.ply_index < 0:
            next_model_index: QModelIndex = self.model().index(0, 0)
        else:
            next_model_index = self.next_model_index

        if next_model_index.isValid():
            self.select_model_index(next_model_index)

    def select_model_index(self, model_index: QModelIndex) -> None:
        """Select notation item with `model_index`."""
        self.selectionModel().setCurrentIndex(
            model_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    @property
    def ply_index(self) -> int:
        """Return index of ply (i.e., half-move)."""
        current_model_index: QModelIndex = self.selectionModel().currentIndex()
        return 2 * current_model_index.row() + current_model_index.column()

    @property
    def previous_model_index(self) -> QModelIndex:
        """Return model index of previous notation item."""
        previous_row, previous_column = divmod(self.ply_index - 1, 2)
        return self.model().index(previous_row, previous_column)

    @property
    def next_model_index(self) -> QModelIndex:
        """Return model index of next notation item."""
        all_rows: int = self.model().rowCount()
        next_row, next_column = divmod(self.ply_index + 1, 2)

        if next_row < all_rows:
            return self.model().index(next_row, next_column)

        return QModelIndex()

    @Slot()
    def on_current_changed(self) -> None:
        """Emit ply index of currently selected notation item."""
        self.item_selected.emit(self.ply_index)
