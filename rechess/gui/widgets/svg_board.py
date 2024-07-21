from chess import svg
from PySide6.QtGui import QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.chess import ClassicChess
from rechess.utils import setting_value


class SvgBoard(QSvgWidget):
    """SVG chessboard with chess pieces."""

    svg.XX = "<circle id='xx' r='5' cx='22' cy='22' fill='lime' stroke='blue'/>"

    def __init__(self, game: ClassicChess) -> None:
        super().__init__()

        self._game: ClassicChess = game

        self._colors: dict[str, str] = {
            "coord": "white",
            "margin": "green",
            "square dark": "lime",
            "square light": "white",
            "arrow red": "#88202080",
            "arrow blue": "#00308880",
            "arrow green": "#15781b80",
            "arrow yellow": "#e68f0080",
            "square dark lastmove": "#e68f0080",
            "square light lastmove": "#e68f0080",
        }

        self.setFixedSize(500, 500)
        self.draw()

    def draw(self) -> None:
        """Draw current chessboard position."""
        svg_board: str = svg.board(
            colors=self._colors,
            board=self._game.board,
            arrows=self._game.arrows,
            check=self._game.king_square,
            squares=self._game.legal_moves,
            orientation=setting_value("board", "orientation"),
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Select square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square_from(x, y)
        self.draw()
