from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.types import Game
from rechess.utils import (
    delete_quarantine_attribute,
    engine_configuration,
    make_executable,
    setting_value,
    stockfish,
)


class UciEngine(QObject):
    """UCI chess engine manager."""

    best_move_analyzed: Signal = Signal(Move)
    move_played: Signal = Signal(Move)
    score_analyzed: Signal = Signal(Score)
    variation_analyzed: Signal = Signal(str)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self._analyzing: bool = False

        self.load(stockfish())

    def load(self, file_name: str) -> None:
        """Load UCI chess engine from `file_name`."""
        with suppress(EngineError):
            delete_quarantine_attribute(file_name)
            make_executable(file_name)

            self._loaded_engine = SimpleEngine.popen_uci(file_name)
            self._loaded_engine.configure(engine_configuration())

    def play_move(self) -> None:
        """Play move with loaded UCI chess engine."""
        play_result: PlayResult = self._loaded_engine.play(
            board=self._game.board,
            limit=Limit(depth=30),
            ponder=setting_value("engine", "is_pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing current chessboard position."""
        self._analyzing = True

        with self._loaded_engine.analysis(
            board=self._game.board,
            limit=Limit(depth=40),
        ) as analysis:
            for info in analysis:
                if not self._analyzing:
                    break

                if "pv" in info:
                    pv: list[Move] = info["pv"][0:15]

                    best_move: Move = pv[0]
                    variation: str = self._game.board.variation_san(pv)
                    score: Score = info["score"].white()

                    self.best_move_analyzed.emit(best_move)
                    self.score_analyzed.emit(score)
                    self.variation_analyzed.emit(variation)

    def stop_analysis(self) -> None:
        """Stop analyzing current chessboard position."""
        self._analyzing = False

    def quit(self) -> None:
        """Quit loaded UCI chess engine's CPU task."""
        self._loaded_engine.quit()

    @property
    def name(self) -> str:
        """Return loaded UCI chess engine's name."""
        return self._loaded_engine.id["name"]
