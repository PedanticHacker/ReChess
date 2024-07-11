from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLineEdit

from rechess.core import Game


class FenEditor(QLineEdit):
    """An editor for editing FEN (Forsyth-Edwards Notation) records."""

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self.setMaxLength(90)
        self.setFixedSize(500, 20)
        self.setText(self._game.fen)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.textEdited.connect(self.on_text_edited)

    def set_red_background_color(self) -> None:
        """Set the background color to red as a warning indication."""
        self.setStyleSheet("background: red;")

    def reset_background_color(self) -> None:
        """Reset the background color to the default lime color."""
        self.setStyleSheet("background: lime;")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Select all text and paste a FEN record from the clipboard."""
        self.selectAll()
        self.paste()

    @Slot(str)
    def on_text_edited(self, edited_text: str) -> None:
        """Try to set a valid position from `edited_text`."""
        try:
            board = self._game.board
            board.set_fen(edited_text)
        except (IndexError, ValueError):
            self.set_red_background_color()
        else:
            if board.is_valid():
                self.clearFocus()
                self.reset_background_color()
                self._game.board = board
                # self._svg_board.draw()
