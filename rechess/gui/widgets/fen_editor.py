from chess import Board
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLineEdit


class FenEditorWidget(QLineEdit):
    """Widget for editing FEN (Forsyth-Edwards Notation)."""

    validated: Signal = Signal()

    def __init__(self, board: Board) -> None:
        super().__init__()

        self._board: Board = board

        self.setMaxLength(90)
        self.setFixedSize(500, 20)
        self.setText(self._board.fen())

        self.textEdited.connect(self.on_text_edited)

    def set_red_background_color(self) -> None:
        """Set background color to red as warning."""
        self.setStyleSheet("background-color: red;")

    def reset_background_color(self) -> None:
        """Reset background color to default lime."""
        self.setStyleSheet("background-color: lime;")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Paste FEN from clipboard on mouse double-click."""
        self.selectAll()
        self.paste()

    @Slot(str)
    def on_text_edited(self, edited_text: str) -> None:
        """Try to set valid chessboard position from `edited_text`."""
        try:
            self._board.set_fen(edited_text)
        except (IndexError, ValueError):
            self.set_red_background_color()
        else:
            if self._board.is_valid():
                self.clearFocus()
                self.reset_background_color()
                self.validated.emit()
