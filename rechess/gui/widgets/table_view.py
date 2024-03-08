from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PySide6.QtCore import QAbstractTableModel, QItemSelectionModel, QSize

from rechess.core import Game


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
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table_model.layoutChanged.connect(self.scrollToBottom)

    def select_preceding_item(self) -> None:
        """Select the preceding notation item in the table."""

    def select_following_item(self) -> None:
        """Select the following notation item in the table."""
