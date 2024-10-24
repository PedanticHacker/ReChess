from contextlib import suppress
from typing import Iterator

from chess import (
    BB_SQUARES,
    Board,
    IllegalMoveError,
    Move,
    PieceType,
    Square,
    square,
    WHITE,
)
from chess.svg import Arrow
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QDialog

from rechess.gui.dialogs import PromotionDialog
from rechess.utils import setting_value


class StandardChess(QObject):
    """Game with rules of standard chess."""

    move_played: Signal = Signal(Move)

    def __init__(self, board: Board) -> None:
        super().__init__()

        self._board: Board = board

        self._arrows: list[Arrow] = []
        self._positions: list[Board] = []
        self._notation_items: list[str] = []
        self._sound_effect: QSoundEffect = QSoundEffect()

        self.set_new_game()

    @property
    def arrows(self) -> list[Arrow]:
        """Return arrows on chessboard."""
        return self._arrows

    @property
    def board(self) -> Board:
        """Return current state of chessboard."""
        return self._board

    @property
    def king_square(self) -> Square | None:
        """Return square of king in check."""
        if self._board.is_check():
            return self._board.king(self._board.turn)
        return None

    @property
    def legal_moves(self) -> list[Square] | None:
        """Return legal moves for piece from its origin square."""
        if self.from_square == -1:
            return None

        square: Square = BB_SQUARES[self.from_square]
        legal_moves: Iterator[Move] = self._board.generate_legal_moves(square)
        return [legal_move.to_square for legal_move in legal_moves]

    @property
    def notation_items(self) -> list[str]:
        """Return notation items."""
        return self._notation_items

    @property
    def result(self) -> str:
        """Return current chess game's result."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins",
            "1-0": "White wins",
            "*": "Undetermined game",
        }
        return result_rewordings[self._board.result(claim_draw=True)]

    @property
    def turn(self) -> bool:
        """Return current turn."""
        return self._board.turn

    def set_new_game(self) -> None:
        """Reset current chess game to starting state."""
        self._board.reset()
        self._arrows.clear()
        self._positions.clear()
        self._notation_items.clear()

        self.reset_squares()

    def reset_squares(self) -> None:
        """Reset piece's origin and target squares."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def push(self, move: Move) -> None:
        """Push `move` on chessboard."""
        self.set_arrow(move)
        self.play_sound_effect(move)

        notation_item: str = self._board.san_and_push(move)
        self._notation_items.append(notation_item)

        position: Board = self._board.copy()
        self._positions.append(position)

    def set_arrow(self, move: Move) -> None:
        """Set arrow on chessboard from `move`."""
        self._arrows = [
            Arrow(
                tail=move.from_square,
                head=move.to_square,
                color="green",
            )
        ]

    def clear_arrows(self) -> None:
        """Clear all arrows on chessboard."""
        self._arrows.clear()

    def play_sound_effect(self, move: Move) -> None:
        """Play sound effect from `move`."""
        is_capture: bool = self._board.is_capture(move)
        file_name: str = "capture.wav" if is_capture else "move.wav"
        file_url: QUrl = QUrl(f"file:rechess/assets/audio/{file_name}")
        self._sound_effect.setSource(file_url)
        self._sound_effect.play()

    def set_root_position(self) -> None:
        """Set all pieces to their root position."""
        self._board = self._board.root()

    def locate_square(self, x: float, y: float) -> None:
        """Locate square from `x` and `y` coordinates."""
        file, rank = self.locate_file_and_rank(x, y)

        if self.from_square == -1:
            self.from_square = square(file, rank)
        else:
            self.to_square = square(file, rank)
            self.find_move(self.from_square, self.to_square)
            self.reset_squares()

    def locate_file_and_rank(self, x: float, y: float) -> tuple[int, int]:
        """Locate file and rank from `x` and `y` coordinates."""
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
                move.promotion = self.promotion_piece()

            self.move_played.emit(move)

    def promotion_piece(self) -> PieceType | None:
        """Return promotion piece from promotion dialog."""
        promotion_dialog: PromotionDialog = PromotionDialog(self._board.turn)

        if promotion_dialog.exec() == QDialog.DialogCode.Accepted:
            return promotion_dialog.piece

        return None

    def set_move(self, ply_index: int) -> None:
        """Set move from `ply_index`."""
        self._board = self._positions[ply_index].copy()

        move: Move = self._board.move_stack[ply_index]
        self.set_arrow(move)

    def delete_data_after(self, ply_index: int) -> None:
        """Delete positions and notation items after `ply_index`."""
        if ply_index < 0:
            self.set_new_game()
        else:
            after_ply_index: slice = slice(ply_index + 1, len(self._notation_items))
            del self._positions[after_ply_index]
            del self._notation_items[after_ply_index]

    def is_engine_on_turn(self) -> bool:
        """Return True if chess engine is on turn, else False."""
        return self._board.turn == setting_value("engine", "is_white")

    def is_in_progress(self) -> bool:
        """Return True if chess game is in progress, else False."""
        return bool(self._notation_items)

    def is_legal(self, move: Move) -> bool:
        """Return True if `move` is legal, else False."""
        return self._board.is_legal(move)

    def is_over(self) -> bool:
        """Return True if chess game is over, else False."""
        return self._board.is_game_over(claim_draw=True)

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn, else False."""
        return self._board.turn == WHITE
