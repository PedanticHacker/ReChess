from platform import system
from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, SimpleEngine
from PySide6.QtCore import QObject, Signal, Slot

from rechess.core import Game
from rechess import get_config_value


class Engine(QObject):
    """A mechanism to communicate with a UCI engine."""

    move_played: Signal = Signal(Move)
    analysis_updated: Signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._game: Game = Game()
        self._loaded_engine: SimpleEngine = SimpleEngine.popen_uci(
            f"rechess/resources/engines/stockfish-16.1/{system().lower()}/"
            f"stockfish{'.exe' if system() == 'Windows' else ''}"
        )
        self.is_analyzing: bool = False

    def load(self, file_path: str) -> None:
        """Load an engine by the given `file_path`."""
        with suppress(EngineError):
            self._loaded_engine.quit()
            self._loaded_engine = SimpleEngine.popen_uci(file_path)

    def play_move(self) -> None:
        """Play a move with the loaded engine."""
        play_result: PlayResult = self._loaded_engine.play(
            limit=Limit(1.0),
            board=self._game.position,
            ponder=get_config_value("engine", "pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing the current position."""
        self.is_analyzing = True

        with self._loaded_engine.analysis(self._game.position) as analysis:
            for info in analysis:
                if not self.is_analyzing:
                    break
                if "pv" in info:
                    self.analysis_updated.emit(info["pv"])

    def stop_analysis(self) -> None:
        """Stop analyzing the current position."""
        self.is_analyzing = False

    def quit(self) -> None:
        """End the CPU task of a loaded engine."""
        self._loaded_engine.quit()

    @property
    def name(self) -> str:
        """Get the name of a loaded engine."""
        return self._loaded_engine.id["name"]
