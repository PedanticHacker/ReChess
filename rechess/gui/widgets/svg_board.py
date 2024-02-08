from chess import svg
from chess.svg import board
from PySide6.QtGui import QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.core import ChessGame


PERSONAL_BOARD_STYLE = {
    "coord": "white",
    "margin": "green",
    "square dark": "lime",
    "square light": "white",
    "arrow red": "#88202080",
    "arrow blue": "#00308880",
    "arrow green": "#15781b80",
    "arrow yellow": "#e68f0080",
    "square dark lastmove": "#8b000080",
    "square light lastmove": "#8b000080",
}


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
            colors=PERSONAL_BOARD_STYLE,
            arrows=self._chess_game.arrow,
            board=self._chess_game.position,
            orientation=self._chess_game.side,
            check=self._chess_game.king_square,
            squares=self._chess_game.legal_moves,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

    def flip_sides(self) -> None:
        """Flip the sides of the board."""
        self._chess_game.flip_sides()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Respond to pressing the primary mouse button."""
        x, y = event.position().x(), event.position().y()
        self._chess_game.get_square_from(x, y)
        self.draw()
