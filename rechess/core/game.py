from contextlib import suppress
from typing import Iterator

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
from chess.svg import Arrow
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QDialog

from rechess.ui.dialogs import PromotionDialog
from rechess.utils import setting_value


class Game(QObject):
    """Chess game state, moves, and UI interactions."""

    move_played: Signal = Signal(Move)

    def __init__(self, board: Board) -> None:
        super().__init__()

        self._board: Board = board

        self._arrows: list[Arrow] = []
        self._positions: list[Board] = []
        self._san_moves: list[str] = []
        self._sound_effect: QSoundEffect = QSoundEffect()

        self.set_new_game()

    @property
    def arrows(self) -> list[Arrow]:
        """Return arrow markers shown on board."""
        return self._arrows

    @property
    def board(self) -> Board:
        """Return board with included positions and game state."""
        return self._board

    @property
    def fen(self) -> str:
        """Return current FEN."""
        return self._board.fen()

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
    def san_moves(self) -> list[str]:
        """Return moves in standard algebraic notation (SAN)."""
        return self._san_moves

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
        """Return which player is currently on turn."""
        return self._board.turn

    def set_new_game(self) -> None:
        """Reset current game to starting state."""
        self._arrows.clear()
        self._board.reset()
        self._san_moves.clear()
        self._positions.clear()

        self.reset_squares()

    def reset_squares(self) -> None:
        """Reset origin and target squares of piece."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def push(self, move: Move) -> None:
        """Execute `move` and update game state."""
        self.set_arrow(move)
        self.play_sound_effect(move)

        san_move: str = self._board.san_and_push(move)
        self._san_moves.append(san_move)

        position: Board = self._board.copy()
        self._positions.append(position)

    def set_arrow(self, move: Move) -> None:
        """Set arrow marker on board for `move`."""
        self._arrows = [Arrow(move.from_square, move.to_square)]

    def clear_arrows(self) -> None:
        """Clear all arrow markers from board."""
        self._arrows.clear()

    def play_sound_effect(self, move: Move) -> None:
        """Play sound effect for `move`."""
        is_capture: bool = self._board.is_capture(move)
        filename: str = "capture.wav" if is_capture else "move.wav"
        file_url: QUrl = QUrl.fromLocalFile(f"rechess/assets/audio/{filename}")
        self._sound_effect.setSource(file_url)
        self._sound_effect.play()

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
        """Convert square coordinates to file and rank."""
        if setting_value("board", "orientation") == WHITE:
            file: float = (x - 18) // 58
            rank: float = 7 - (y - 18) // 58
        else:
            file = 7 - (x - 18) // 58
            rank = (y - 18) // 58

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

    def set_move(self, ply_index: int) -> None:
        """Set move at `ply_index`."""
        self._board = self._positions[ply_index].copy()

        move: Move = self._board.move_stack[ply_index]
        self.set_arrow(move)

    def delete_data_after(self, ply_index: int) -> None:
        """Delete moves and positions after `ply_index`."""
        if ply_index < 0:
            self.set_new_game()
        else:
            after_ply_index: slice = slice(ply_index + 1, len(self._san_moves))
            del self._san_moves[after_ply_index]
            del self._positions[after_ply_index]

    def is_engine_on_turn(self) -> bool:
        """Return True if engine is on turn."""
        return self._board.turn == setting_value("engine", "is_white")

    def is_in_progress(self) -> bool:
        """Return True if game is in progress."""
        return bool(self._san_moves)

    def is_legal(self, move: Move) -> bool:
        """Return True if `move` is legal."""
        return self._board.is_legal(move)

    def is_over(self) -> bool:
        """Return True if game is over."""
        return self._board.is_game_over(claim_draw=True)

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn."""
        return self._board.turn == WHITE
