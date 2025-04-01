from __future__ import annotations

from contextlib import suppress
from typing import ClassVar, Final, Iterator

from chess import (
    BB_SQUARES,
    WHITE,
    Board,
    IllegalMoveError,
    Move,
    PieceType,
    Square,
    square,
)
from PySide6.QtCore import QObject, QPoint, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QDialog

from rechess.ui.dialogs import PromotionDialog
from rechess.utils import setting_value


BOARD_MARGIN: Final[float] = 20.0
SQUARE_SIZE: Final[float] = 70.0


class Game(QObject):
    """Management for game state, moves, events, and UI interaction."""

    move_played: ClassVar[Signal] = Signal(Move)

    def __init__(self) -> None:
        super().__init__()

        self.board: Board = Board()
        self.arrow: list[tuple[Square, Square]] = []
        self.moves: list[str] = []
        self.positions: list[Board] = []
        self.is_historic_state: bool = False

        self._sound_effects: dict[str, QSoundEffect] = {}
        self._preload_sound_effects()

        self.reset_selected_squares()

    @property
    def fen(self) -> str:
        """Get current position in FEN format."""
        return self.board.fen()

    @fen.setter
    def fen(self, value) -> None:
        """Set new position in FEN format based on `value`."""
        self.board.set_fen(value)
        self._initialize_state()

    @property
    def checked_king_square(self) -> Square | None:
        """Get square of checked king."""
        if self.board.is_check():
            return self.board.king(self.board.turn)
        return None

    @property
    def legal_targets(self) -> list[Square] | None:
        """Get target squares considered as legal moves for piece."""
        if not self.origin_square:
            return None

        square: Square = BB_SQUARES[self.origin_square]
        legal_targets: Iterator[Move] = self.board.generate_legal_moves(square)
        return [move.to_square for move in legal_targets]

    @property
    def result(self) -> str:
        """Get result of current game."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins",
            "1-0": "White wins",
            "*": "Undetermined game",
        }
        return result_rewordings[self.board.result(claim_draw=True)]

    @property
    def turn(self) -> bool:
        """Return True if White is on turn."""
        return self.board.turn

    def _preload_sound_effects(self) -> None:
        """Preload all sound effects during initialization."""
        file_names: tuple[str, ...] = (
            "game-over",
            "check",
            "promotion",
            "capture",
            "castling",
            "move",
        )

        for file_name in file_names:
            file_url: QUrl = QUrl(f"file:rechess/assets/audio/{file_name}.wav")
            sound_effect: QSoundEffect = QSoundEffect(self)
            sound_effect.setSource(file_url)
            self._sound_effects[file_name] = sound_effect

    def _sound_effect_name(self, move: Move) -> str:
        """Get sound effect name based on `move`."""
        if self.is_over_after(move):
            return "game-over"
        if self.is_check(move):
            return "check"
        if move.promotion:
            return "promotion"
        if self.board.is_capture(move):
            return "capture"
        if self.board.is_castling(move):
            return "castling"
        return "move"

    def play_sound_effect(self, move: Move) -> None:
        """Play sound effect for `move`."""
        self._sound_effects[self._sound_effect_name(move)].play()

    def reset_selected_squares(self) -> None:
        """Reset origin and target squares."""
        self.origin_square: Square | None = None
        self.target_square: Square | None = None

    def _initialize_state(self) -> None:
        """Clear game history and set squares to initial value."""
        self.arrow.clear()
        self.moves.clear()
        self.positions.clear()
        self.reset_selected_squares()

    def prepare_new_game(self) -> None:
        """Initialize state and reset board for new game."""
        self._initialize_state()
        self.board.reset()

    def maybe_append_ellipsis(self) -> None:
        """If Black moves first, append ellipsis for White's move."""
        if not self.moves and not self.is_white_on_turn():
            self.moves.append("...")
            self.positions.append(self.board.copy())

    def push(self, move: Move) -> None:
        """Update game state by pushing `move`."""
        self.maybe_append_ellipsis()
        self.play_sound_effect(move)
        self.set_arrow(move)

        new_move: str = self.board.san_and_push(move)
        self.moves.append(new_move)

        position: Board = self.board.copy()
        self.positions.append(position)

    def set_arrow(self, move: Move) -> None:
        """Set arrow marker based on `move`."""
        self.arrow = [(move.from_square, move.to_square)]

    def clear_arrow(self) -> None:
        """Clear arrow marker from board."""
        self.arrow.clear()

    def set_root_position(self) -> None:
        """Reset pieces on board to initial position."""
        self.board = self.board.root()

    def select_square(self, cursor_point: QPointF) -> None:
        """Select square based on `cursor_point`."""
        selection_point: QPoint = self.selection_point(cursor_point)
        selected_square: Square = square(selection_point.x(), selection_point.y())

        if not self.origin_square:
            self.origin_square = selected_square
        else:
            self.target_square = selected_square
            self.find_legal_move(self.origin_square, self.target_square)
            self.reset_selected_squares()

    def selection_point(self, cursor_point: QPointF) -> QPoint:
        """Get selection point based on `cursor_point`."""
        if setting_value("board", "orientation") == WHITE:
            file: float = (cursor_point.x() - BOARD_MARGIN) // SQUARE_SIZE
            rank: float = 7 - (cursor_point.y() - BOARD_MARGIN) // SQUARE_SIZE
        else:
            file = 7 - (cursor_point.x() - BOARD_MARGIN) // SQUARE_SIZE
            rank = (cursor_point.y() - BOARD_MARGIN) // SQUARE_SIZE

        file_integer: int = round(file)
        rank_integer: int = round(rank)
        file_index: int = max(0, min(7, file_integer))
        rank_index: int = max(0, min(7, rank_integer))

        return QPoint(file_index, rank_index)

    def find_legal_move(self, origin_square: Square, target_square: Square) -> None:
        """Find legal move for `origin_square` and `target_square`."""
        with suppress(IllegalMoveError):
            move: Move = self.board.find_move(origin_square, target_square)

            if move.promotion:
                move.promotion = self.promotion_piece_type()

            self.move_played.emit(move)

    def promotion_piece_type(self) -> PieceType | None:
        """Get promotion piece type from promotion dialog."""
        promotion_dialog: PromotionDialog = PromotionDialog(self.board.turn)

        if promotion_dialog.exec() == QDialog.DialogCode.Accepted:
            return promotion_dialog.piece_type

        return None

    def piece_at(self, square: Square) -> Piece | None:
        """Get piece at `square`."""
        return self.board.piece_at(square)

    def set_move(self, item_index: int) -> None:
        """Set move and arrow based on `item_index`."""
        self.clear_arrow()
        self.board = self.positions[item_index].copy()

        if self.board.move_stack and self.moves[item_index] != "...":
            self.set_arrow(self.board.move_stack[-1])

    def delete_data_after(self, item_index: int) -> None:
        """Delete moves and positions after `item_index`."""
        if item_index < 0:
            self._initialize_state()
        else:
            after_item_index: slice = slice(item_index + 1, len(self.moves))
            del self.moves[after_item_index]
            del self.positions[after_item_index]

    def is_check(self, move: Move) -> bool:
        """Return True if `move` would put opponent king in check."""
        board: Board = self.board.copy()
        board.push(move)
        return board.is_check()

    def is_engine_on_turn(self) -> bool:
        """Return True if engine is on turn."""
        return self.board.turn == setting_value("engine", "is_white")

    def is_in_progress(self) -> bool:
        """Return True if game is in progress."""
        return bool(self.moves)

    def is_legal(self, move: Move) -> bool:
        """Return True if `move` would be considered as legal."""
        return self.board.is_legal(move)

    def is_over(self) -> bool:
        """Return True if game is over."""
        return self.board.is_game_over(claim_draw=True)

    def is_over_after(self, move: Move) -> bool:
        """Return True if `move` would make game be over."""
        board: Board = self.board.copy()
        board.push(move)
        return board.is_game_over(claim_draw=True)

    def is_valid(self) -> bool:
        """Return True if board setup is valid."""
        return self.board.is_valid()

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn."""
        return self.board.turn == WHITE
