from PySide6.QtWidgets import QHeaderView, QTableView
from PySide6.QtCore import QModelIndex, QSize, Slot

from rechess.core import TableModel


class TableView(QTableView):
    """A view for showing chess notation in table form."""

    def __init__(self) -> None:
        super().__init__()

        self.setShowGrid(False)
        self.setModel(TableModel())
        self.setFixedSize(QSize(300, 550))
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.pressed.connect(self.on_item_pressed)

    def select_preceding_item(self) -> None:
        """Select the preceding chess notation item in the table."""
        current_index = self.currentIndex()
        current_column = current_index.column()
        preceding_row = current_index.row() - 1
        preceding_index = self.model().index(preceding_row, current_column)
        self.setCurrentIndex(preceding_index)

    def select_following_item(self) -> None:
        """Select the following chess notation item in the table."""
        current_index = self.currentIndex()
        current_column = current_index.column()
        following_row = current_index.row() + 1
        following_index = self.model().index(following_row, current_column)
        self.setCurrentIndex(following_index)

    def refresh(self) -> None:
        """Refresh the model's layout."""
        self.model().layoutChanged.emit()

    @Slot(QModelIndex)
    def on_item_pressed(self, model_index: QModelIndex) -> None:
        """Respond to pressing a chess notation item."""
        self.setCurrentIndex(model_index)
