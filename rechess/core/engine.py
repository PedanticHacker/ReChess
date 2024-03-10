from platform import system
from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.core import Game
from rechess import get_config_value


class Engine(QObject):
    """A mechanism to communicate with a UCI engine."""

    move_played: Signal = Signal(Move)
    score_refreshed: Signal = Signal(Score)
    variation_refreshed: Signal = Signal(str)

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self._loaded_engine: SimpleEngine = SimpleEngine.popen_uci(
            f"rechess/resources/engines/stockfish-16.1/{system().lower()}/"
            f"stockfish{'.exe' if system() == 'Windows' else ''}"
        )
        self._resigned: bool = False
        self._analyzing: bool = False

    def has_resigned(self) -> bool:
        """Check whether the loaded engine has resigned."""
        return self._resigned

    def load(self, file_path: str) -> None:
        """Load an engine by the given `file_path`."""
        with suppress(EngineError):
            self._loaded_engine.quit()
            self._loaded_engine = SimpleEngine.popen_uci(file_path)

    def play_move(self) -> None:
        """Play a move by the loaded engine."""
        play_result: PlayResult = self._loaded_engine.play(
            limit=Limit(1.0),
            board=self._game.position,
            ponder=get_config_value("engine", "pondering"),
        )
        self._resigned = play_result.resigned
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing the current position."""
        self._analyzing = True

        with self._loaded_engine.analysis(self._game.position) as analysis:
            for info in analysis:
                if self._analyzing and "pv" in info:
                    variation_text = self._game.get_variation_text(info["pv"])
                    self.variation_refreshed.emit(variation_text)
                if not self._analyzing:
                    break

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
