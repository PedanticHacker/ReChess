from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.core import Game
from rechess.utils import (
    delete_quarantine_attribute,
    engine_configuration,
    make_executable,
    path_to_stockfish,
    setting_value,
)


class Engine(QObject):
    """Communication with UCI-compliant engine."""

    best_move_analyzed: Signal = Signal(Move)
    move_played: Signal = Signal(Move)
    score_analyzed: Signal = Signal(Score)
    variation_analyzed: Signal = Signal(str)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._analyzing: bool = False

        self.load_from_file_at(path_to_stockfish())

    def load_from_file_at(self, path_to_file: str) -> None:
        """Load engine from file at `path_to_file`."""
        delete_quarantine_attribute(path_to_file)
        make_executable(path_to_file)

        self.quit()
        self._engine = SimpleEngine.popen_uci(path_to_file)
        self._engine.configure(engine_configuration())

    def play_move(self) -> None:
        """Make engine to play move."""
        play_result: PlayResult = self._engine.play(
            board=self._game.board,
            limit=Limit(depth=30),
            ponder=setting_value("engine", "is_ponder_on"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing current position."""
        self._analyzing = True

        with self._engine.analysis(
            board=self._game.board,
            limit=Limit(depth=40),
        ) as analysis:
            for info in analysis:
                if not self._analyzing:
                    break

                if "pv" in info:
                    pv: list[Move] = info["pv"][0:36]

                    best_move: Move = pv[0]
                    variation: str = self._game.board.variation_san(pv)
                    score: Score = info["score"].white()

                    self.best_move_analyzed.emit(best_move)
                    self.score_analyzed.emit(score)
                    self.variation_analyzed.emit(variation)

    def stop_analysis(self) -> None:
        """Stop analyzing current position."""
        self._analyzing = False

    def quit(self) -> None:
        """Terminate engine's process."""
        with suppress(AttributeError):
            self._engine.quit()

    @property
    def name(self) -> str:
        """Return engine's name."""
        with suppress(AttributeError):
            return self._engine.id["name"]
        return ""
