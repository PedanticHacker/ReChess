from contextlib import suppress

from chess import Move
from chess.engine import EngineError, Limit, PlayResult, Score, SimpleEngine
from PySide6.QtCore import QObject, Signal

from rechess.game import ClassicGame
from rechess.utils import engine_configuration, setting_value, stockfish


class UciEngine(QObject):
    """UCI chess engine manager."""

    move_played: Signal = Signal(Move)
    best_move_analyzed: Signal = Signal(Move)
    san_variation_analyzed: Signal = Signal(str)
    white_score_analyzed: Signal = Signal(Score)

    def __init__(self, game: ClassicGame) -> None:
        super().__init__()

        self._game: ClassicGame = game

        self._analyzing: bool = False

        self._loaded_engine: SimpleEngine = SimpleEngine.popen_uci(stockfish())
        self._loaded_engine.configure(engine_configuration())

    def load(self, file_path: str) -> None:
        """Load a UCI chess engine with `file_path`."""
        with suppress(EngineError):
            self._loaded_engine.quit()
            self._loaded_engine = SimpleEngine.popen_uci(file_path)
            self._loaded_engine.configure(engine_configuration())

    def play_move(self) -> None:
        """Play a move with the loaded UCI chess engine."""
        play_result: PlayResult = self._loaded_engine.play(
            board=self._game.board,
            limit=Limit(depth=30),
            ponder=setting_value("engine", "is_pondering"),
        )
        self.move_played.emit(play_result.move)

    def start_analysis(self) -> None:
        """Start analyzing the current chessboard position."""
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
        """Stop analyzing the current chessboard position."""
        self._analyzing = False

    def quit(self) -> None:
        """Quit the loaded UCI chess engine's CPU process."""
        self._loaded_engine.quit()

    @property
    def name(self) -> str:
        """Return the loaded UCI chess engine's name."""
        return self._loaded_engine.id["name"]
