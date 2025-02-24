from __future__ import annotations

from contextlib import suppress
from enum import EnumDict
from typing import ClassVar, Iterator

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


class SoundEffectFileUrl(EnumDict):
    """File URL enum for sound effects of various move types."""

    Capture = QUrl("file:rechess/assets/audio/capture.wav")
    Castling = QUrl("file:rechess/assets/audio/castling.wav")
    Check = QUrl("file:rechess/assets/audio/check.wav")
    GameOver = QUrl("file:rechess/assets/audio/game-over.wav")
    Move = QUrl("file:rechess/assets/audio/move.wav")
    Promotion = QUrl("file:rechess/assets/audio/promotion.wav")


class Game(QObject):
    """Chess game state, moves, and UI interaction management."""

    move_played: ClassVar[Signal] = Signal(Move)

    def __init__(self) -> None:
        super().__init__()

        self._board: Board = Board()

        self._arrow: list[tuple[Square, Square]] = []
        self._moves: list[str] = []
        self._positions: list[Board] = []

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
    def arrow(self) -> list[tuple[Square, Square]]:
        """Return current arrow marker."""
        return self._arrow

    @property
    def board(self) -> Board:
        """Return current state of board."""
        return self._board

    @property
    def fen(self) -> str:
        """Return current position in FEN format."""
        return self._board.fen()

    @fen.setter
    def fen(self, value) -> None:
        """Initialize state and set new position based on `value`."""
        self._board.set_fen(value)
        self._initialize_state()

    @property
    def king_in_check(self) -> Square | None:
        """Return square of king in check."""
        if self._board.is_check():
            return self._board.king(self._board.turn)
        return None

    @property
    def legal_moves(self) -> list[Square] | None:
        """Return squares that indicate legal moves for piece."""
        if self.from_square == -1:
            return None

        square: Square = BB_SQUARES[self.from_square]
        legal_moves: Iterator[Move] = self._board.generate_legal_moves(square)
        return [legal_move.to_square for legal_move in legal_moves]

    @property
    def moves(self) -> list[str]:
        """Return moves in Standard Algebraic Notation (SAN)."""
        return self._moves

    @property
    def result(self) -> str:
        """Return result of current game."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins",
            "1-0": "White wins",
            "*": "Undetermined game",
        }
        return result_rewordings[self._board.result(claim_draw=True)]

    @property
    def turn(self) -> bool:
        """Return True if White is on turn."""
        return self._board.turn

    def reset_squares(self) -> None:
        """Reset origin and target squares of piece."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def _initialize_state(self) -> None:
        """Clear game history and set squares to initial value."""
        self._arrow.clear()
        self._moves.clear()
        self._positions.clear()
        self.reset_squares()

    def prepare_new_game(self) -> None:
        """Reset board for new game and initialize state."""
        self._initialize_state()
        self._board.reset()

    def push(self, move: Move) -> None:
        """Update game state by pushing `move`."""
        self.set_arrow(move)
        self.play_sound_effect(move)

        new_move: str = self._board.san_and_push(move)
        self._moves.append(new_move)

        position: Board = self._board.copy()
        self._positions.append(position)

    def set_arrow(self, move: Move) -> None:
        """Set arrow marker based on `move`."""
        self._arrow = [(move.from_square, move.to_square)]

    def clear_arrow(self) -> None:
        """Clear arrow marker from board."""
        self._arrow.clear()

    def play_sound_effect(self, move: Move) -> None:
        """Play sound effect for `move`."""
        if self.is_over_after(move):
            self._game_over_sound_effect.play()
        elif self.is_check(move):
            self._check_sound_effect.play()
        elif move.promotion:
            self._promotion_sound_effect.play()
        elif self._board.is_capture(move):
            self._capture_sound_effect.play()
        elif self._board.is_castling(move):
            self._castling_sound_effect.play()
        else:
            self._move_sound_effect.play()

    def set_root_position(self) -> None:
        """Reset pieces on board to initial position."""
        self._board = self._board.root()

    def locate_square(self, x: float, y: float) -> None:
        """Convert mouse coordinates to square coordinates."""
        file, rank = self.locate_file_and_rank(x, y)

        if self.from_square == -1:
            self.from_square = square(file, rank)
        else:
            self.to_square = square(file, rank)
            self.find_move(self.from_square, self.to_square)
            self.reset_squares()

    def locate_file_and_rank(self, x: float, y: float) -> tuple[int, int]:
        """Convert `x` and `y` square coordinates to file and rank."""
        if setting_value("board", "orientation") == WHITE:
            file: float = (x - 20) // 70
            rank: float = 7 - (y - 20) // 70
        else:
            file = 7 - (x - 20) // 70
            rank = (y - 20) // 70

        return round(file), round(rank)

    def find_move(self, origin: Square, target: Square) -> None:
        """Find legal move from `origin` and `target` squares."""
        with suppress(IllegalMoveError):
            move: Move = self._board.find_move(origin, target)

            if move.promotion:
                move.promotion = self.promotion_piece_type()

            self.move_played.emit(move)

    def promotion_piece_type(self) -> PieceType | None:
        """Return promotion piece type from promotion dialog."""
        promotion_dialog: PromotionDialog = PromotionDialog(self._board.turn)

        if promotion_dialog.exec() == QDialog.DialogCode.Accepted:
            return promotion_dialog.piece_type

        return None

    def set_move(self, item_index: int) -> None:
        """Set move and arrow based on `item_index`."""
        self._board = self._positions[item_index].copy()
        self.set_arrow(self._board.move_stack[item_index])

    def delete_data_after(self, item_index: int) -> None:
        """Delete moves and positions after `item_index`."""
        if item_index < 0:
            self._initialize_state()
        else:
            after_item_index: slice = slice(item_index + 1, len(self._moves))
            del self._moves[after_item_index]
            del self._positions[after_item_index]

    def is_check(self, move: Move) -> bool:
        """Return True if `move` is check."""
        board: Board = self._board.copy()
        board.push(move)
        return board.is_check()

    def is_engine_on_turn(self) -> bool:
        """Return True if engine is on turn."""
        return self._board.turn == setting_value("engine", "is_white")

    def is_in_progress(self) -> bool:
        """Return True if game is in progress."""
        return bool(self._moves)

    def is_legal(self, move: Move) -> bool:
        """Return True if `move` is legal."""
        return self._board.is_legal(move)

    def is_over(self) -> bool:
        """Return True if game is over."""
        return self._board.is_game_over(claim_draw=True)

    def is_over_after(self, move: Move) -> bool:
        """Return True if `move` makes game be over."""
        board: Board = self._board.copy()
        board.push(move)
        return board.is_game_over(claim_draw=True)

    def is_valid(self) -> bool:
        """Return True if board setup is valid."""
        return self._board.is_valid()

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn."""
        return self._board.turn == WHITE
