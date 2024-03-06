from chess import STARTING_FEN
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QSize, Qt, Slot

from rechess.core import Game


class FENEditor(QLineEdit):
    """An editor for FEN (Forsyth-Edwards Notation) records."""

    def __init__(self) -> None:
        super().__init__()

        self.setMaxLength(90)
        self.setText(STARTING_FEN)
        self.setFixedSize(QSize(500, 20))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.textEdited.connect(self.on_fen_edited)

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
    def on_fen_edited(self, new_fen: str) -> None:
        """Try to set a valid position from `new_fen`."""
        try:
            position = Game.position
            position.set_fen(new_fen)
        except (IndexError, ValueError):
            self.set_red_background_color()
        else:
            if position.is_valid():
                self.clearFocus()
                self.reset_background_color()
                Game.position = position
