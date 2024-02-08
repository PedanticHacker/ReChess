from PySide6.QtWidgets import QHeaderView, QTableView
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSize, Slot


FIXED_RESIZE_MODE = QHeaderView.ResizeMode.Fixed
STRETCH_RESIZE_MODE = QHeaderView.ResizeMode.Stretch


class TableView(QTableView):
    """A view for showing chess notation in table form."""

    def __init__(self, table_model: QAbstractTableModel) -> None:
        super().__init__()

        self.setShowGrid(False)
        self.setModel(table_model)
        self.setFixedSize(QSize(300, 550))
        self.verticalHeader().setSectionResizeMode(FIXED_RESIZE_MODE)
        self.horizontalHeader().setSectionResizeMode(STRETCH_RESIZE_MODE)

        self.pressed.connect(self.on_item_pressed)

    def select_preceding_item(self) -> None:
        """Select the preceding chess notation item in the table."""
        current_index = self.currentIndex()
        current_column = current_index.column()
        preceding_row = current_index.row() - 1
        preceding_index = self.model().index(preceding_row, current_column)

        if preceding_index.isValid():
            self.setCurrentIndex(preceding_index)

    def select_following_item(self) -> None:
        """Select the following chess notation item in the table."""
        current_index = self.currentIndex()
        current_column = current_index.column()
        following_row = current_index.row() + 1
        following_index = self.model().index(following_row, current_column)

        if following_index.isValid():
            self.setCurrentIndex(following_index)

    @Slot(QModelIndex)
    def on_item_pressed(self, model_index: QModelIndex) -> None:
        """Respond to pressing a chess notation item."""
        self.setCurrentIndex(model_index)
