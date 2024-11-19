from chess import Board
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLineEdit


class FenEditor(QLineEdit):
    """Editor for Forsyth-Edwards notation (FEN)."""

    fen_validated: Signal = Signal()

    def __init__(self, board: Board) -> None:
        super().__init__()

        self._board: Board = board

        self.setMaxLength(90)
        self.setFixedSize(600, 20)
        self.setText(self._board.fen())
        self.textEdited.connect(self.validate_fen)

    def show_warning(self) -> None:
        """Show red background color to indicate invalid FEN."""
        self.setStyleSheet("background-color: red;")

    def hide_warning(self) -> None:
        """Hide red background color to indicate valid FEN."""
        self.setStyleSheet("")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Paste FEN from clipboard on mouse double-click."""
        self.selectAll()
        self.paste()

    @Slot(str)
    def validate_fen(self, fen: str) -> None:
        """Validate `fen` to set new position based on it."""
        try:
            self._board.set_fen(fen)
        except (IndexError, ValueError):
            self.show_warning()
        else:
            if self._board.is_valid():
                self.fen_validated.emit()
