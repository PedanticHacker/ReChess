from chess import Color
from chess.engine import Score
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QProgressBar, QSizePolicy

from rechess.utils import setting_value


class EvaluationBarWidget(QProgressBar):
    """Bar widget for animating chessboard position evaluation."""

    def __init__(self) -> None:
        super().__init__()

        self._size_policy = self.sizePolicy()
        self._size_policy.setRetainSizeWhenHidden(True)

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuint)
        self._animation.valueChanged.connect(self.update)

        self.setRange(0, 1000)
        self.setFixedSize(40, 500)
        self.setSizePolicy(self._size_policy)
        self.setOrientation(Qt.Orientation.Vertical)

        self.reset_appearance()

    def reset_appearance(self) -> None:
        """Reset bar's appearance."""
        self.hide()
        self.reset()
        self.flip_appearance()

    def flip_appearance(self) -> None:
        """Flip bar's chunk appearance relative to orientation."""
        orientation: bool = setting_value("board", "orientation")
        self.setInvertedAppearance(orientation)

    def animate(self, evaluation: Score) -> None:
        """Animate bar's chunk from `evaluation`."""
        if evaluation.is_mate():
            moves_to_mate: int = evaluation.mate() or 0
            is_white_matting: bool = moves_to_mate > 0
            animation_value: int = 0 if is_white_matting else 1000
            evaluation_text: str = f"M{abs(moves_to_mate)}"
        else:
            score: int = evaluation.score() or 0
            animation_value = 500 - score
            evaluation_text = f"{score / 100 :.2f}"

        self.setFormat(evaluation_text)
        self._animation.setEndValue(animation_value)
        self._animation.start()
