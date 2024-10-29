from chess import Board
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsColorizeEffect, QLineEdit


class FenEditorWidget(QLineEdit):
    """Widget for editing FEN (Forsyth-Edwards Notation)."""

    validated: Signal = Signal()

    def __init__(self, board: Board) -> None:
        super().__init__()

        self._board: Board = board

        self._create_colorize_effect()

        self.setMaxLength(90)
        self.setFixedSize(500, 20)
        self.setText(self._board.fen())

        self.textEdited.connect(self.on_text_edited)

    def _create_colorize_effect(self) -> None:
        """Create, configure, and initially hide colorize effect."""
        self._colorize_effect: QGraphicsColorizeEffect = QGraphicsColorizeEffect(self)
        self._colorize_effect.setColor(Qt.GlobalColor.red)
        self._colorize_effect.setStrength(0.5)
        self._colorize_effect.setEnabled(False)
        self.setGraphicsEffect(self._colorize_effect)

    def show_warning_effect(self) -> None:
        """Show colorize effect in red to indicate warning."""
        self._colorize_effect.setEnabled(True)

    def hide_warning_effect(self) -> None:
        """Hide colorize effect in red to indicate normal state."""
        self._colorize_effect.setEnabled(False)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Paste FEN from clipboard on mouse double-click."""
        self.clearFocus()
        self.selectAll()
        self.paste()

    @Slot(str)
    def on_text_edited(self, edited_text: str) -> None:
        """Try to set valid chessboard position from `edited_text`."""
        try:
            self._board.set_fen(edited_text)
        except (IndexError, ValueError):
            self.show_warning_effect()
        else:
            if self._board.is_valid():
                self.clearFocus()
                self.hide_warning_effect()
                self.validated.emit()
