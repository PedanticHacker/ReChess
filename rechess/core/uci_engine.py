from platform import system
from contextlib import suppress

from chess import Board, Move
from chess.engine import EngineError, Limit, PlayResult, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess import get_config_value


DEFAULT_FILE_PATH: str = (
    f"rechess/resources/engines/Stockfish-16/{system()}/stockfish"
    f"{'.exe' if system() == 'Windows' else ''}"
)


class UCIEngine(QObject):
    """An implementation of UCI engine communication."""

    move_played: Signal = Signal(Move)
    analysis_updated: Signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._board: Board = Board()
        self.is_analysis_active: bool = False
        self._engine: SimpleEngine = SimpleEngine.popen_uci(DEFAULT_FILE_PATH)

    def load(self, file_path: str) -> None:
        """Load a chess engine by the given `file_path`."""
        with suppress(EngineError):
            self._engine.quit()
            self._engine = SimpleEngine.popen_uci(file_path)

    def play_move(self) -> None:
        """Play a move with the loaded chess engine."""
        play_result: PlayResult = self._engine.play(
            limit=Limit(1.0),
            board=self._board,
            ponder=get_config_value("engine", "pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing the current position."""
        self.is_analysis_active = True

        with self._engine.analysis(self._board) as analysis:
            for info in analysis:
                if self.is_analysis_active and "pv" in info:
                    self.analysis_updated.emit(info["pv"])
                elif not self.is_analysis_active:
                    break

    def stop_analysis(self) -> None:
        """Stop analyzing the current position."""
        self.is_analysis_active = False

    def quit(self) -> None:
        """Quit the CPU process of a loaded chess engine."""
        self._engine.quit()

    @property
    def name(self) -> str:
        """Get the name of a loaded chess engine."""
        return self._engine.id["name"]
