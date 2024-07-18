from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.core import Game
from rechess.utils import engine_configuration, setting_value, stockfish


class Engine(QObject):
    """UCI chess engine manager."""

    move_played: Signal = Signal(Move)
    best_move_analyzed: Signal = Signal(Move)
    san_variation_analyzed: Signal = Signal(str)
    white_score_analyzed: Signal = Signal(Score)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self._analyzing: bool = False

        self._loaded_engine: SimpleEngine = SimpleEngine.popen_uci(stockfish())
        self._loaded_engine.configure(engine_configuration())

    def load(self, file_path: str) -> None:
        """Load UCI chess engine with `file_path`."""
        with suppress(EngineError):
            self._loaded_engine.quit()
            self._loaded_engine = SimpleEngine.popen_uci(file_path)
            self._loaded_engine.configure(engine_configuration())

    def play_move(self) -> None:
        """Play move with loaded chess engine."""
        play_result: PlayResult = self._loaded_engine.play(
            board=self._game.board,
            limit=Limit(depth=30),
            ponder=setting_value("engine", "is_pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing chessboard position."""
        self._analyzing = True

        with self._loaded_engine.analysis(
            board=self._game.board,
            limit=Limit(depth=40),
        ) as analysis:
            for info in analysis:
                if not self._analyzing:
                    break

                if "pv" in info:
                    pv: list[Move] = info["pv"]
                    best_move: Move = pv[0]
                    san_variation: str = self._game.board.variation_san(pv)
                    white_score: Score = info["score"].white()

                    self.best_move_analyzed.emit(best_move)
                    self.white_score_analyzed.emit(white_score)
                    self.san_variation_analyzed.emit(san_variation)

    def stop_analysis(self) -> None:
        """Stop analyzing chessboard position."""
        self._analyzing = False

    def quit(self) -> None:
        """Quit CPU process of loaded chess engine."""
        self._loaded_engine.quit()

    @property
    def name(self) -> str:
        """Return name of loaded chess engine."""
        return self._loaded_engine.id["name"]
