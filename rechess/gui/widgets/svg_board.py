from chess import svg
from PySide6.QtGui import QMouseEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.game import StandardChess
from rechess.utils import board_colors, setting_value


class SvgBoardWidget(QSvgWidget):
    """SVG chessboard widget with interactive chess pieces."""

    svg.XX = "<circle id='xx' r='5' cx='22' cy='22' stroke='green' fill='lime'/>"

    def __init__(self, game: StandardChess) -> None:
        super().__init__()

        self._game: StandardChess = game

        self.draw()

    def draw(self) -> None:
        """Draw current chessboard position."""
        svg_board: str = svg.board(
            colors=board_colors(),
            board=self._game.board,
            arrows=self._game.arrows,
            check=self._game.king_square,
            squares=self._game.legal_moves,
            orientation=setting_value("board", "orientation"),
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Locate square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square(x, y)
        self.draw()
