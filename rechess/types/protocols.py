from typing import Any, Protocol

from chess import Board, Move, Square
from chess.svg import Arrow


class Game(Protocol):
    """Protocol for implementing specific chess game."""

    move_played: Any  # Signal(Move)

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

    @property
    def result(self) -> str:
        """Return current chess game's result."""
        raise NotImplementedError("`result` property must be implemented")

    @property
    def turn(self) -> bool:
        """Return current turn."""
        raise NotImplementedError("`turn` property must be implemented")

    def clear_arrows(self) -> None:
        """Clear all arrows on chessboard."""
        raise NotImplementedError("`clear_arrows` method must be implemented")

    def delete_data_after(self, ply_index: int) -> None:
        """Delete positions and notation items after `ply_index`."""
        raise NotImplementedError("`delete_data_after` method must be implemented")

    def find_move(self, origin: Square, target: Square) -> None:
        """Find legal move from `origin` and `target` squares."""
        raise NotImplementedError("`find_move` method must be implemented")

    def locate_square(self, x: float, y: float) -> None:
        """Locate square from `x` and `y` coordinates."""
        raise NotImplementedError("`locate_square` method must be implemented")

    def push(self, move: Move) -> None:
        """Push `move` on chessboard."""
        raise NotImplementedError("`push` method must be implemented")

    def set_arrow(self, move: Move) -> None:
        """Set arrow on chessboard from `move`."""
        raise NotImplementedError("`set_arrow` method must be implemented")

    def set_move(self, ply_index: int) -> None:
        """Set move from `ply_index`."""
        raise NotImplementedError("`set_move` method must be implemented")

    def set_new_game(self) -> None:
        """Reset current chess game to starting state."""
        raise NotImplementedError("`set_new_game` method must be implemented")

    def set_root_position(self) -> None:
        """Set all pieces to their root position."""
        raise NotImplementedError("`set_root_position` method must be implemented")

    def is_engine_on_turn(self) -> bool:
        """Return True if chess engine is on turn, else False."""
        raise NotImplementedError("`is_engine_on_turn` method must be implemented")

    def is_in_progress(self) -> bool:
        """Return True if chess game is in progress, else False."""
        raise NotImplementedError("`is_in_progress` method must be implemented")

    def is_legal(self, move: Move) -> bool:
        """Return True if `move` is legal, else False."""
        raise NotImplementedError("`is_legal` method must be implemented")

    def is_over(self) -> bool:
        """Return True if chess game is over, else False."""
        raise NotImplementedError("`is_over` method must be implemented")

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn, else False."""
        raise NotImplementedError("`is_white_on_turn` method must be implemented")


class Engine(Protocol):
    """Protocol for implementing specific chess engine."""

    best_move_analyzed: Any  # Signal(Move)
    move_played: Any  # Signal(Move)
    san_variation_analyzed: Any  # Signal(str)
    white_score_analyzed: Any  # Signal(Score)

    _game: Game

    @property
    def name(self) -> str:
        """Return loaded chess engine's name."""
        raise NotImplementedError("`name` property must be implemented")

    def load(self, file_path: str) -> None:
        """Load chess engine from `file_path`."""
        raise NotImplementedError("`load` method must be implemented")

    def play_move(self) -> None:
        """Play move with loaded chess engine."""
        raise NotImplementedError("`play_move` method must be implemented")

    def start_analysis(self) -> None:
        """Start analyzing current chessboard position."""
        raise NotImplementedError("`start_analysis` method must be implemented")

    def stop_analysis(self) -> None:
        """Stop analyzing current chessboard position."""
        raise NotImplementedError("`stop_analysis` method must be implemented")

    def quit(self) -> None:
        """Quit loaded chess engine's CPU task."""
        raise NotImplementedError("`quit` method must be implemented")
