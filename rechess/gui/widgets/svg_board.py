from chess import svg
from PySide6.QtCore import Property
from PySide6.QtGui import QColor, QMouseEvent, QPaintEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.game import ChessGame
from rechess.utils import setting_value


svg.XX = "<circle id='xx' r='5' cx='22' cy='22' stroke='#303030' fill='#e5e5e5'/>"


class SvgBoardWidget(QSvgWidget):
    """Board with interactive pieces as SVG widget."""

    arrow_blue: Property = Property(
        QColor,
        lambda self: self._arrow_blue,
        lambda self, color: setattr(self, "_arrow_blue", color),
    )

    arrow_green: Property = Property(
        QColor,
        lambda self: self._arrow_green,
        lambda self, color: setattr(self, "_arrow_green", color),
    )

    arrow_red: Property = Property(
        QColor,
        lambda self: self._arrow_red,
        lambda self, color: setattr(self, "_arrow_red", color),
    )

    arrow_yellow: Property = Property(
        QColor,
        lambda self: self._arrow_yellow,
        lambda self, color: setattr(self, "_arrow_yellow", color),
    )

    coord: Property = Property(
        QColor,
        lambda self: self._coord,
        lambda self, color: setattr(self, "_coord", color),
    )

    inner_border: Property = Property(
        QColor,
        lambda self: self._inner_border,
        lambda self, color: setattr(self, "_inner_border", color),
    )

    margin: Property = Property(
        QColor,
        lambda self: self._margin,
        lambda self, color: setattr(self, "_margin", color),
    )

    outer_border: Property = Property(
        QColor,
        lambda self: self._outer_border,
        lambda self, color: setattr(self, "_outer_border", color),
    )

    square_dark: Property = Property(
        QColor,
        lambda self: self._square_dark,
        lambda self, color: setattr(self, "_square_dark", color),
    )

    square_dark_lastmove: Property = Property(
        QColor,
        lambda self: self._square_dark_lastmove,
        lambda self, color: setattr(self, "_square_dark_lastmove", color),
    )

    square_light: Property = Property(
        QColor,
        lambda self: self._square_light,
        lambda self, color: setattr(self, "_square_light", color),
    )

    square_light_lastmove: Property = Property(
        QColor,
        lambda self: self._square_light_lastmove,
        lambda self, color: setattr(self, "_square_light_lastmove", color),
    )

    def __init__(self, game: ChessGame) -> None:
        super().__init__()

        self._game: ChessGame = game

        self._arrow_blue: QColor = QColor()
        self._arrow_green: QColor = QColor()
        self._arrow_red: QColor = QColor()
        self._arrow_yellow: QColor = QColor()
        self._coord: QColor = QColor()
        self._inner_border: QColor = QColor()
        self._margin: QColor = QColor()
        self._outer_border: QColor = QColor()
        self._square_dark: QColor = QColor()
        self._square_dark_lastmove: QColor = QColor()
        self._square_light: QColor = QColor()
        self._square_light_lastmove: QColor = QColor()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Locate square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square(x, y)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint current state of board."""
        board_colors: dict[str, str] = {
            "arrow blue": getattr(self, "_arrow_blue").name(),
            "arrow green": getattr(self, "_arrow_green").name(),
            "arrow red": getattr(self, "_arrow_red").name(),
            "arrow yellow": getattr(self, "_arrow_yellow").name(),
            "coord": getattr(self, "_coord").name(),
            "inner border": getattr(self, "_inner_border").name(),
            "margin": getattr(self, "_margin").name(),
            "outer border": getattr(self, "_outer_border").name(),
            "square dark": getattr(self, "_square_dark").name(),
            "square dark lastmove": getattr(self, "_square_dark_lastmove").name(),
            "square light": getattr(self, "_square_light").name(),
            "square light lastmove": getattr(self, "_square_light_lastmove").name(),
        }

        svg_board: str = svg.board(
            arrows=self._game.arrows,
            board=self._game.board,
            check=self._game.king_square,
            colors=board_colors,
            orientation=setting_value("board", "orientation"),
            squares=self._game.legal_moves,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)

        super().paintEvent(event)
