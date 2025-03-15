from __future__ import annotations

from contextlib import suppress
from enum import EnumDict
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
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QDialog

from rechess.ui.dialogs import PromotionDialog
from rechess.utils import setting_value


BOARD_MARGIN: Final[float] = 20.0
SQUARE_SIZE: Final[float] = 70.0


class SoundEffectFileUrl(EnumDict):
    """File URL enum for sound effects of various game events."""

    Capture = QUrl("file:rechess/assets/audio/capture.wav")
    Castling = QUrl("file:rechess/assets/audio/castling.wav")
    Check = QUrl("file:rechess/assets/audio/check.wav")
    GameOver = QUrl("file:rechess/assets/audio/game-over.wav")
    Move = QUrl("file:rechess/assets/audio/move.wav")
    Promotion = QUrl("file:rechess/assets/audio/promotion.wav")


class Game(QObject):
    """Management for game state, moves, events, and UI interaction."""

    move_played: ClassVar[Signal] = Signal(Move)

    def __init__(self) -> None:
        super().__init__()

        self.board: Board = Board()

        self.arrow: list[tuple[Square, Square]] = []
        self.moves: list[str] = []
        self.positions: list[Board] = []

        self._capture_sound_effect: QSoundEffect = QSoundEffect(self)
        self._capture_sound_effect.setSource(SoundEffectFileUrl.Capture)

        self._castling_sound_effect: QSoundEffect = QSoundEffect(self)
        self._castling_sound_effect.setSource(SoundEffectFileUrl.Castling)

        self._check_sound_effect: QSoundEffect = QSoundEffect(self)
        self._check_sound_effect.setSource(SoundEffectFileUrl.Check)

        self._game_over_sound_effect: QSoundEffect = QSoundEffect(self)
        self._game_over_sound_effect.setSource(SoundEffectFileUrl.GameOver)

        self._move_sound_effect: QSoundEffect = QSoundEffect(self)
        self._move_sound_effect.setSource(SoundEffectFileUrl.Move)

        self._promotion_sound_effect: QSoundEffect = QSoundEffect(self)
        self._promotion_sound_effect.setSource(SoundEffectFileUrl.Promotion)

        self.reset_squares()

    @property
    def fen(self) -> str:
        """Return current position in FEN format."""
        return self.board.fen()

    @fen.setter
    def fen(self, value) -> None:
        """Initialize state and set new position based on `value`."""
        self.board.set_fen(value)
        self._initialize_state()

    @property
    def king_in_check(self) -> Square | None:
        """Return square of king in check."""
        if self.board.is_check():
            return self.board.king(self.board.turn)
        return None

    @property
    def legal_moves(self) -> list[Square] | None:
        """Get target squares that would be legal for piece."""
        if self.from_square == -1:
            return None

        square: Square = BB_SQUARES[self.from_square]
        legal_moves: Iterator[Move] = self.board.generate_legal_moves(square)
        return [legal_move.to_square for legal_move in legal_moves]

    @property
    def result(self) -> str:
        """Return result of current game."""
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

    def reset_squares(self) -> None:
        """Reset origin and target squares of piece."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def _initialize_state(self) -> None:
        """Clear game history and set squares to initial value."""
        self.arrow.clear()
        self.moves.clear()
        self.positions.clear()
        self.reset_squares()

    def prepare_new_game(self) -> None:
        """Reset board for new game and initialize state."""
        self._initialize_state()
        self.board.reset()

    def push(self, move: Move) -> None:
        """Update game state by pushing `move`."""
        self.set_arrow(move)
        self.play_sound_effect(move)

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

    def play_sound_effect(self, move: Move) -> None:
        """Play sound effect for `move`."""
        if self.is_over_after(move):
            self._game_over_sound_effect.play()
        elif self.is_check(move):
            self._check_sound_effect.play()
        elif move.promotion:
            self._promotion_sound_effect.play()
        elif self.board.is_capture(move):
            self._capture_sound_effect.play()
        elif self.board.is_castling(move):
            self._castling_sound_effect.play()
        else:
            self._move_sound_effect.play()

    def set_root_position(self) -> None:
        """Reset pieces on board to initial position."""
        self.board = self.board.root()

    def locate_square(self, x: float, y: float) -> None:
        """Get square location from `x` and `y` coordinates."""
        file, rank = self.locate_file_and_rank(x, y)

        if self.from_square == -1:
            self.from_square = square(file, rank)
        else:
            self.to_square = square(file, rank)
            self.find_move(self.from_square, self.to_square)
            self.reset_squares()

    def locate_file_and_rank(self, x: float, y: float) -> tuple[int, int]:
        """Get file and rank location from `x` and `y` coordinates."""
        if setting_value("board", "orientation") == WHITE:
            file_position: float = (x - BOARD_MARGIN) // SQUARE_SIZE
            rank_position: float = 7 - (y - BOARD_MARGIN) // SQUARE_SIZE
        else:
            file_position = 7 - (x - BOARD_MARGIN) // SQUARE_SIZE
            rank_position = (y - BOARD_MARGIN) // SQUARE_SIZE

        file_index: int = round(file_position)
        rank_index: int = round(rank_position)
        valid_file: int = max(0, min(7, file_index))
        valid_rank: int = max(0, min(7, rank_index))

        return valid_file, valid_rank

    def find_move(self, origin_square: Square, target_square: Square) -> None:
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

    def set_move(self, item_index: int) -> None:
        """Set move and arrow for it based on `item_index`."""
        self.board = self.positions[item_index].copy()
        self.set_arrow(self.board.move_stack[item_index])

    def delete_data_after(self, item_index: int) -> None:
        """Delete moves and positions data after `item_index`."""
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
