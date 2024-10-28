from chess import svg
from PySide6.QtGui import QMouseEvent, QPaintEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.game import ChessGame
from rechess.utils import board_colors, setting_value


class SvgBoardWidget(QSvgWidget):
    """Board with interactive pieces as SVG widget."""

    svg.XX = "<circle id='xx' r='5' cx='22' cy='22' stroke='#303030' fill='#e5e5e5'/>"

    def __init__(self, game: ChessGame) -> None:
        super().__init__()

        self._game: ChessGame = game

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Locate square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square(x, y)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint current state of board."""
        svg_board: str = svg.board(
            arrows=self._game.arrows,
            board=self._game.board,
            check=self._game.king_square,
            colors=board_colors(),
            orientation=setting_value("board", "orientation"),
            squares=self._game.legal_moves,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)
        super().paintEvent(event)
