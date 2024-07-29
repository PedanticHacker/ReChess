from typing import Protocol

from chess import Board, Move, Square
from chess.svg import Arrow


class Engine(Protocol):
    """Protocol for implementing specific chess engine."""

    _game: Game

    def play_move(self) -> None:
        raise NotImplementedError("`play_move` method must be implemented")

    def start_analysis(self) -> None:
        raise NotImplementedError("`start_analysis` method must be implemented")


class Game(Protocol):
    """Protocol for implementing specific chess game."""

    _board: Board

    @property
    def arrows(self) -> list[Arrow]:
        """Return arrows on chessboard."""
        raise NotImplementedError("`arrows` property must be implemented")

    @property
    def board(self) -> Board:
        """Return current state of chessboard."""
        raise NotImplementedError("`board` property must be implemented")

    @property
    def king_square(self) -> Square | None:
        """Return square of king in check."""
        raise NotImplementedError("`king_square` property must be implemented")

    @property
    def legal_moves(self) -> list[Square] | None:
        """Return legal moves for piece from its origin square."""
        raise NotImplementedError("`legal_moves` property must be implemented")

    @property
    def notation_items(self) -> list[str]:
        """Return notation items."""
        raise NotImplementedError("`notation_items` property must be implemented")

    def find_move(self, origin: Square, target: Square) -> None:
        """Find legal move from `origin` and `target` squares."""
        raise NotImplementedError("`find_move` method must be implemented")

    def locate_square(self, x: float, y: float) -> None:
        """Locate square from `x` and `y` coordinates."""
        raise NotImplementedError("`locate_square` method must be implemented")

    def push(self, move: Move) -> None:
        """Push `move` on chessboard."""
        raise NotImplementedError("`push` method must be implemented")
