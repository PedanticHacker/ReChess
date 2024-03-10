from typing import Iterator
from contextlib import suppress

from chess import square
from chess import BB_SQUARES, BLACK, WHITE
from chess import Board, Color, IllegalMoveError, Move, PieceType, Square
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QObject, QUrl, Signal

from rechess import get_config_value
from rechess.gui.dialogs import PromotionDialog


class Game(QObject):
    """An implementation of the standard game."""

    move_played: Signal = Signal(Move)

    def __init__(self) -> None:
        super().__init__()

        self.notation: list[str] = []
        self.position: Board = Board()
        self.arrow: list[tuple[Square, Square]] = []
        self.sound_effect: QSoundEffect = QSoundEffect()

        self.prepare_new_game()

    def push(self, move: Move) -> None:
        """Push the given `move`."""
        self.set_arrow_for(move)
        self.play_sound_effect_for(move)
        self.set_notation_item_for(move)

    def prepare_new_game(self) -> None:
        """Prepare the starting state of a game."""
        self.arrow.clear()
        self.position.reset()

        self._engine_color: Color = get_config_value("engine", "white")
        self.perspective: Color = not self._engine_color

        self.reset_squares()

    def reset_squares(self) -> None:
        """Reset the origin and target squares of a piece."""
        self.from_square: Square = -1
        self.to_square: Square = -1

    def set_notation_item_for(self, move: Move) -> None:
        """Set a notation item for the given `move`."""
        notation_item: str = self.position.san_and_push(move)
        self.notation.append(notation_item)

    def flip_board(self) -> None:
        """Flip the board's perspective."""
        self.perspective = not self.perspective

    def get_square_from(self, x: float, y: float) -> None:
        """Detect a square from `x` and `y` coordinates."""
        file, rank = self.detect_file_and_rank_from(x, y)

        if self.from_square == -1:
            self.from_square = square(file, rank)
        else:
            self.to_square = square(file, rank)
            self.find_move(self.from_square, self.to_square)
            self.reset_squares()

    def detect_file_and_rank_from(self, x: float, y: float) -> tuple[int, int]:
        """Detect a file and a rank from `x` and `y` coordinates."""
        if self.perspective == WHITE:
            file = (x - 18) // 58
            rank = 7 - (y - 18) // 58
        else:
            file = 7 - (x - 18) // 58
            rank = (y - 18) // 58

        return round(file), round(rank)

    def find_move(self, origin: Square, target: Square) -> None:
        """Find a move from the given `origin` and `target` squares."""
        with suppress(IllegalMoveError):
            move: Move = self.position.find_move(origin, target)

            if move.promotion:
                move.promotion = self.get_promotion_piece()

            self.move_played.emit(move)

    def get_promotion_piece(self) -> PieceType:
        """Show the promotion dialog to get a promotion piece."""
        promotion_dialog: PromotionDialog = PromotionDialog(self.position.turn)
        return promotion_dialog.piece_type

    def get_fen(self) -> str:
        """Get a FEN of the current position."""
        return self.position.fen()

    def get_result(self) -> str:
        """Show the result of a game."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins!",
            "1-0": "White wins!",
            "*": "Undetermined game",
        }
        return result_rewordings[self.position.result()]

    def get_variation_text(self, variation: list[Move]) -> str:
        """Get a variation in the form of `1. e4 e5 2. Nf3`."""
        return self.position.variation_san(variation)

    def play_sound_effect_for(self, move: Move) -> None:
        """Play a WAV sound effect for the given `move`."""
        file_name = (
            "capture.wav" if self.position.is_capture(move) else "move.wav"
        )
        file_path = f"rechess/resources/audio/{file_name}"
        file_url = QUrl.fromLocalFile(file_path)
        self.sound_effect.setSource(file_url)
        self.sound_effect.play()

    def set_arrow_for(self, move: Move) -> None:
        """Set an arrow for the given `move`."""
        self.arrow = [(move.from_square, move.to_square)]

    def pass_turn_to_engine(self) -> None:
        """Pass the current turn to the engine."""
        self._engine_color = not self._engine_color
        # utils.set_config_values()

    def is_black_on_turn(self) -> bool:
        """Return True if Black is on turn, else False."""
        return self.position.turn == BLACK

    def is_game_in_progress(self) -> bool:
        """Return True if a game is in progress, else False."""
        return bool(self.notation)

    def is_game_over(self) -> bool:
        """Return `True` if the current game is over, else `False`."""
        return self.position.is_game_over(claim_draw=True)

    def is_engine_on_turn(self) -> bool:
        """Return `True` if the engine is on turn, else `False`."""
        return self.position.turn == self._engine_color

    def is_perspective_flipped(self) -> bool:
        """Return `True` if Black plays from the bottom, else `False`."""
        return self.perspective == BLACK

    def is_white_on_turn(self) -> bool:
        """Return `True` if White is on turn, else `False`."""
        return self.position.turn == WHITE

    @property
    def king_square(self) -> Square | None:
        """Get the square of a king in check."""
        if self.position.is_check():
            return self.position.king(self.position.turn)
        return None

    @property
    def legal_moves(self) -> list[Square] | None:
        """Get all legal moves for a piece from its origin square."""
        if self.from_square == -1:
            return None

        square: Square = BB_SQUARES[self.from_square]
        legal_moves: Iterator[Move] = self.position.generate_legal_moves(square)
        return [legal_move.to_square for legal_move in legal_moves]
