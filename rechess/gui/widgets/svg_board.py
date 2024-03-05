from chess import svg
from PySide6.QtGui import QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.core import Game


svg.XX: str = "<circle id='xx' r='5' cx='22' cy='22' fill='lime' stroke='blue'/>"


class SVGBoard(QSvgWidget):
    """An SVG-based board with pieces."""

    def __init__(self) -> None:
        super().__init__()

        self._game: Game = Game()
        self._colors: dict[str, str] = {
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

        self.draw()

    def draw(self) -> None:
        """Draw the current position on the board."""
        svg_board: str = svg.board(
            colors=self._colors,
            arrows=self._game.arrow,
            board=self._game.position,
            check=self._game.king_square,
            squares=self._game.legal_moves,
            orientation=self._game.orientation,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

    def flip_board(self) -> None:
        """Flip the board's orientation."""
        self._game.flip_board()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Respond to pressing the primary mouse button."""
        x, y = event.position().x(), event.position().y()
        self._game.get_square_from(x, y)
        self.draw()
