from chess.engine import Score
from PySide6.QtWidgets import QProgressBar, QSizePolicy
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt

from rechess.core import Game
from rechess import get_config_value


class EvaluationBar(QProgressBar):
    """A bar showing an engine's evaluation of a position."""

    def __init__(self, game: Game) -> None:
        super().__init__()

        self._game: Game = game

        self.reset()
        self.setRange(0, 1000)
        self.setFixedSize(QSize(40, 500))
        self.setOrientation(Qt.Orientation.Vertical)

        self.set_animation()
        self.retain_size_when_hidden()

    def set_animation(self) -> None:
        """Set animation for the bar."""
        self._animation: QPropertyAnimation = QPropertyAnimation(self)
        self._animation.setTargetObject(self)
        self._animation.setPropertyName(b"value")
        self._animation.valueChanged.connect(self.update)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuint)

    def retain_size_when_hidden(self) -> None:
        """Retain the size of the bar when it is hidden."""
        evaluation_bar_size_policy: QSizePolicy = self.sizePolicy()
        evaluation_bar_size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(evaluation_bar_size_policy)

    def animate(self, evaluation: Score) -> None:
        """Animate the bar per the given `evaluation`."""
        if evaluation.is_mate():
            moves_to_mate: int = evaluation.mate() or 0
            is_white_matting: bool = moves_to_mate > 0
            animation_value: int = 0 if is_white_matting else 1000
            evaluation_text: str = f"M{moves_to_mate}"
        else:
            score: int = evaluation.score() or 0
            animation_value = 500 - score
            evaluation_text = f"{score / 100 :.2f}"

        self.setFormat(evaluation_text)
        self._animation.setEndValue(animation_value)
        self._animation.start()

    def flip_perspective(self) -> None:
        """Flip the bar's perspective if the engine plays as White."""
        self.setInvertedAppearance(self._game.perspective)

    def reset(self) -> None:
        """Reset the bar to its default state."""
        self.hide()
        self.flip_perspective()
