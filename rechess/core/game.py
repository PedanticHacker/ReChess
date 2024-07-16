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
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QDialog

from rechess.gui.dialogs import PromotionDialog
from rechess.utils import setting_value


class Game(QObject):
    """A standard chess game."""

    move_played: Signal = Signal(Move)

    def __init__(self) -> None:
        super().__init__()

        self.board: Board = Board()
        self.positions: list[Board] = []
        self.notation_items: list[str] = []
        self.arrow: list[tuple[Square, Square]] = []
        self.sound_effect: QSoundEffect = QSoundEffect()

        self.set_new_game()

    @property
    def fen_record(self) -> str:
        """Get a FEN record of the current chessboard position."""
        return self.board.fen()

    @property
    def king_square(self) -> Square | None:
        """Get the square of a king in check."""
        if self.board.is_check():
            return self.board.king(self.board.turn)
        return None

    @property
    def legal_moves(self) -> list[Square] | None:
        """Get all legal moves for a piece from its origin square."""
        if self.from_square == -1:
            return None

        square: Square = BB_SQUARES[self.from_square]
        legal_moves: Iterator[Move] = self.board.generate_legal_moves(square)
        return [legal_move.to_square for legal_move in legal_moves]

    @property
    def result(self) -> str:
        """Show the result of a game."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins",
            "1-0": "White wins",
            "*": "Undetermined game",
        }
        return result_rewordings[self.board.result(claim_draw=True)]

    def set_new_game(self) -> None:
        """Set the starting state of a standard chess game."""
        self.arrow.clear()
        self.board.reset()
        self.positions.clear()
        self.notation_items.clear()

        self.reset_squares()

    def reset_squares(self) -> None:
        """Reset the origin and target squares of a piece."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def push(self, move: Move) -> None:
        """Push the `move`."""
        self.set_arrow_for(move)
        self.play_sound_effect_for(move)

        notation_item: str = self.board.san_and_push(move)
        self.notation_items.append(notation_item)

        position: Board = self.board.copy()
        self.positions.append(position)

    def set_arrow_for(self, move: Move) -> None:
        """Set an arrow for the `move`."""
        self.arrow = [(move.from_square, move.to_square)]

    def clear_arrow(self) -> None:
        """Clear the arrow from the chessboard."""
        self.arrow.clear()

    def play_sound_effect_for(self, move: Move) -> None:
        """Play a WAV sound effect for the `move`."""
        is_capture: bool = self.board.is_capture(move)
        file_name: str = "capture.wav" if is_capture else "move.wav"
        file_url: QUrl = QUrl(f"file:rechess/resources/audio/{file_name}")
        self.sound_effect.setSource(file_url)
        self.sound_effect.play()

    def set_root_position(self) -> None:
        """Set all pieces to their root position."""
        self.board = self.board.root()

    def square_from(self, x: float, y: float) -> None:
        """Get a square from `x` and `y` coordinates."""
        file, rank = self.file_and_rank_from(x, y)

        if self.from_square == -1:
            self.from_square = square(file, rank)
        else:
            self.to_square = square(file, rank)
            self.find_move(self.from_square, self.to_square)
            self.reset_squares()

    def file_and_rank_from(self, x: float, y: float) -> tuple[int, int]:
        """Detect a file and a rank from the `x` and `y` coordinates."""
        if setting_value("board", "orientation") == WHITE:
            file: float = (x - 18) // 58
            rank: float = 7 - (y - 18) // 58
        else:
            file = 7 - (x - 18) // 58
            rank = (y - 18) // 58

        return round(file), round(rank)

    def find_move(self, origin: Square, target: Square) -> None:
        """Find a move from the `origin` and `target` squares."""
        with suppress(IllegalMoveError):
            move: Move = self.board.find_move(origin, target)

            if move.promotion:
                move.promotion = self.promotion_piece_type()

            self.move_played.emit(move)

    def promotion_piece_type(self) -> PieceType | None:
        """Show the promotion dialog to get a promotion piece type."""
        promotion_dialog: PromotionDialog = PromotionDialog(self.board.turn)

        if promotion_dialog.exec() == QDialog.DialogCode.Accepted:
            return promotion_dialog.piece_type

        return None

    def san_variation(self) -> str:
        """Get a variation of moves in SAN format from the move stack."""
        return Board().variation_san(self.board.move_stack)

    def set_move_with(self, ply_index: int) -> None:
        """Set a move with the `ply_index`."""
        self.board = self.positions[ply_index].copy()

        move: Move = self.board.move_stack[ply_index]
        self.set_arrow_for(move)

    def delete_data_after(self, ply_index: int) -> None:
        """Delete notation items and positions after `ply_index`."""
        if ply_index < 0:
            self.set_new_game()
        else:
            after_ply_index: slice = slice(ply_index + 1, len(self.notation_items))
            del self.positions[after_ply_index]
            del self.notation_items[after_ply_index]

    def is_engine_on_turn(self) -> bool:
        """Return True if the chess engine is on turn, else False."""
        return self.board.turn == setting_value("engine", "is_white")

    def is_game_in_progress(self) -> bool:
        """Return True if a chess game is in progress, else False."""
        return bool(self.notation_items)

    def is_game_over(self) -> bool:
        """Return True if the current chess game is over, else False."""
        return self.board.is_game_over(claim_draw=True)

    def is_legal(self, move: Move) -> bool:
        """Check whether the `move` is legal in the current position."""
        return self.board.is_legal(move)

    def is_white_on_turn(self) -> bool:
        """Return True if White is on turn, else False."""
        return self.board.turn == WHITE
