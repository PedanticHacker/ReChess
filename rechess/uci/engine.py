from __future__ import annotations

from contextlib import suppress
from typing import ClassVar

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.utils import (
    delete_quarantine_attribute,
    engine_configuration,
    make_executable,
    path_to_stockfish,
    setting_value,
)


class Engine(QObject):
    """Communication with UCI-compliant engine."""

    best_move_analyzed: ClassVar[Signal] = Signal(Move)
    move_played: ClassVar[Signal] = Signal(Move)
    score_analyzed: ClassVar[Signal] = Signal(Score)
    variation_analyzed: ClassVar[Signal] = Signal(str)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._analyzing: bool = False

        self.load_from_file_at(path_to_stockfish())

    def load_from_file_at(self, path_to_file: str) -> None:
        """Load engine from file at `path_to_file`."""
        delete_quarantine_attribute(path_to_file)
        make_executable(path_to_file)

        with suppress(EngineError):
            active_engine: SimpleEngine = SimpleEngine.popen_uci(path_to_file)
            active_engine.configure(engine_configuration())

            self.quit()
            self._engine: SimpleEngine = active_engine

    def play_move(self) -> None:
        """Invoke engine to play move."""
        play_result: PlayResult = self._engine.play(
            board=self._game.board,
            limit=Limit(depth=30),
            ponder=setting_value("engine", "is_ponder_on"),
        )

        if not self._game.is_in_previous_state:
            self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing current position."""
        self._analyzing = True

        with self._engine.analysis(self._game.board) as analysis:
            for info in analysis:
                if not self._analyzing:
                    break

                if "pv" in info:
                    pv: list[Move] = info["pv"]

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
        """Terminate engine process."""
        if hasattr(self, "_engine"):
            self._engine.quit()

    @property
    def name(self) -> str:
        """Get engine name."""
        name: str = self._engine.id["name"]
        return f"{name[0:20]}..." if len(name) > 20 else name
