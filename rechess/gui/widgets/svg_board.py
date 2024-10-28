from chess import svg
from PySide6.QtCore import Property
from PySide6.QtGui import QMouseEvent, QPaintEvent
from PySide6.QtSvgWidgets import QSvgWidget

from rechess.game import ChessGame
from rechess.utils import setting_value


class SvgBoardWidget(QSvgWidget):
    """Board with interactive pieces as SVG widget."""

    svg.XX: str = "<circle id='xx' r='5' cx='22' cy='22' stroke='green' fill='gray'/>"

    def __init__(self, game: ChessGame) -> None:
        super().__init__()

        self._game: ChessGame = game

        self._arrow_blue_color: str = ""
        self._arrow_green_color: str = ""
        self._arrow_red_color: str = ""
        self._arrow_yellow_color: str = ""
        self._coord_color: str = ""
        self._dark_lastmove_color: str = ""
        self._dark_square_color: str = ""
        self._inner_border_color: str = ""
        self._light_lastmove_color: str = ""
        self._light_square_color: str = ""
        self._margin_color: str = ""
        self._outer_border_color: str = ""

        self.update()

    @Property(str)
    def arrowBlueColor(self) -> str:
        return self._arrow_blue_color

    @arrowBlueColor.setter
    def arrowBlueColor(self, color: str) -> None:
        self._arrow_blue_color = color
        self.update()

    @Property(str)
    def arrowGreenColor(self) -> str:
        return self._arrow_green_color

    @arrowGreenColor.setter
    def arrowGreenColor(self, color: str) -> None:
        self._arrow_green_color = color
        self.update()

    @Property(str)
    def arrowRedColor(self) -> str:
        return self._arrow_red_color

    @arrowRedColor.setter
    def arrowRedColor(self, color: str) -> None:
        self._arrow_red_color = color
        self.update()

    @Property(str)
    def arrowYellowColor(self) -> str:
        return self._arrow_yellow_color

    @arrowYellowColor.setter
    def arrowYellowColor(self, color: str) -> None:
        self._arrow_yellow_color = color
        self.update()

    @Property(str)
    def coordColor(self) -> str:
        return self._coord_color

    @coordColor.setter
    def coordColor(self, color: str) -> None:
        self._coord_color = color
        self.update()

    @Property(str)
    def darkLastmoveColor(self) -> str:
        return self._dark_lastmove_color

    @darkLastmoveColor.setter
    def darkLastmoveColor(self, color: str) -> None:
        self._dark_lastmove_color = color
        self.update()

    @Property(str)
    def darkSquareColor(self) -> str:
        return self._dark_square_color

    @darkSquareColor.setter
    def darkSquareColor(self, color: str) -> None:
        self._dark_square_color = color
        self.update()

    @Property(str)
    def innerBorderColor(self) -> str:
        return self._inner_border_color

    @innerBorderColor.setter
    def innerBorderColor(self, color: str) -> None:
        self._inner_border_color = color
        self.update()

    @Property(str)
    def lightLastmoveColor(self) -> str:
        return self._light_lastmove_color

    @lightLastmoveColor.setter
    def lightLastmoveColor(self, color: str) -> None:
        self._light_lastmove_color = color
        self.update()

    @Property(str)
    def lightSquareColor(self) -> str:
        return self._light_square_color

    @lightSquareColor.setter
    def lightSquareColor(self, color: str) -> None:
        self._light_square_color = color
        self.update()

    @Property(str)
    def marginColor(self) -> str:
        return self._margin_color

    @marginColor.setter
    def marginColor(self, color: str) -> None:
        self._margin_color = color
        self.update()

    @Property(str)
    def outerBorderColor(self) -> str:
        return self._outer_border_color

    @outerBorderColor.setter
    def outerBorderColor(self, color: str) -> None:
        self._outer_border_color = color
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Locate square on mouse button press."""
        x: float = event.position().x()
        y: float = event.position().y()
        self._game.locate_square(x, y)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint state of SVG board widget."""
        svg_board: str = svg.board(
            board=self._game.board,
            arrows=self._game.arrows,
            check=self._game.king_square,
            colors={
                "arrow blue": self._arrow_blue_color,
                "arrow green": self._arrow_green_color,
                "arrow red": self._arrow_red_color,
                "arrow yellow": self._arrow_yellow_color,
                "coord": self._coord_color,
                "inner border": self._inner_border_color,
                "margin": self._margin_color,
                "outer border": self._outer_border_color,
                "square dark": self._dark_square_color,
                "square dark lastmove": self._dark_lastmove_color,
                "square light": self._light_square_color,
                "square light lastmove": self._light_lastmove_color,
            },
            orientation=setting_value("board", "orientation"),
            squares=self._game.legal_moves,
        )
        encoded_svg_board: bytes = svg_board.encode()
        self.load(encoded_svg_board)
        super().paintEvent(event)
