from __future__ import annotations

from contextlib import suppress
from platform import system

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.utils import get_config_value


class Engine(QObject):
    """A mechanism to communicate with a UCI engine."""

    move_played: Signal = Signal(Move)
    best_move_analyzed: Signal = Signal(Move)
    san_variation_analyzed: Signal = Signal(str)
    white_score_analyzed: Signal = Signal(Score)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game
        self._analyzing: bool = False
        self._loaded_engine: SimpleEngine = SimpleEngine.popen_uci(
            f"rechess/resources/engines/stockfish-16.1/{system().lower()}/"
            f"stockfish{'.exe' if system() == 'Windows' else ''}"
        )

    def load(self, file_path: str) -> None:
        """Load an engine by the given `file_path`."""
        with suppress(EngineError):
            self._loaded_engine.quit()
            self._loaded_engine = SimpleEngine.popen_uci(file_path)

    def play_move(self) -> None:
        """Play a move by the loaded engine."""
        play_result: PlayResult = self._loaded_engine.play(
            limit=Limit(1.0),
            board=self._game.board,
            ponder=get_config_value("engine", "pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing the current position."""
        self._analyzing = True

        with self._loaded_engine.analysis(self._game.board) as analysis:
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
        """Stop analyzing the current position."""
        self._analyzing = False

    def quit(self) -> None:
        """End the CPU task of a loaded engine."""
        self._loaded_engine.quit()

    @property
    def name(self) -> str:
        """Get the name of a loaded engine."""
        return self._loaded_engine.id["name"]
