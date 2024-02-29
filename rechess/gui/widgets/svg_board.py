from chess import svg
from chess.svg import board
from PySide6.QtGui import QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.core import ChessGame
from rechess import get_board_colors


class SVGBoard(QSvgWidget):
    """An SVG-based board with pieces."""

    def __init__(self) -> None:
        super().__init__()

        self._chess_game: ChessGame = ChessGame()

        self._set_legal_move_marker()
        self.draw()

    def _set_legal_move_marker(self) -> None:
        """Set a dot as the marker for a legal move."""
        svg.XX = (
            "<circle id='xx' r='5.5' cx='22.5' cy='22.5' fill='yellow' stroke='blue'/>"
        )

    def draw(self) -> None:
        """Draw the current position on the board."""
        svg_board: str = board(
            colors=get_board_colors(),
            arrows=self._chess_game.arrow,
            board=self._chess_game.position,
            check=self._chess_game.king_square,
            squares=self._chess_game.legal_moves,
            orientation=self._chess_game.orientation,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

    def flip_board(self) -> None:
        """Flip the board."""
        self._chess_game.flip_board()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Respond to pressing the primary mouse button."""
        x, y = event.position().x(), event.position().y()
        self._chess_game.get_square_from(x, y)
        self.draw()
