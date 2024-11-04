from chess import Board
from PySide6.QtCore import Signal, Slot
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

    def show_warning(self) -> None:
        """Show background color in red to indicate invalid FEN."""
        self.setStyleSheet("background-color: red;")

    def hide_warning(self) -> None:
        """Hide background color in red to indicate valid FEN."""
        self.setStyleSheet("")
        self.clearFocus()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Paste FEN from clipboard on mouse double-click."""
        self.clearFocus()
        self.selectAll()
        self.paste()

    @Slot(str)
    def on_text_edited(self, edited_text: str) -> None:
        """Try to set valid position from `edited_text`."""
        try:
            self._board.set_fen(edited_text)
        except (IndexError, ValueError):
            self.show_warning()
        else:
            if self._board.is_valid():
                self.clearFocus()
                self.hide_warning()
                self.validated.emit()
