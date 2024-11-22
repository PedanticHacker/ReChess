from chess.engine import Score
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QProgressBar

from rechess.utils import setting_value


class EvaluationBar(QProgressBar):
    """Chunk animator based on evaluation score."""

    def __init__(self) -> None:
        super().__init__()

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.valueChanged.connect(self.update)

        self.setRange(0, 1000)
        self.setFixedSize(50, 600)
        self.setOrientation(Qt.Orientation.Vertical)

    def reset_evaluation(self) -> None:
        """Set chunk to neutral evaluation."""
        self.reset()

    def invert_appearance(self) -> None:
        """Invert chunk's appearance based on board orientation."""
        self.setInvertedAppearance(setting_value("board", "orientation"))

    def animate(self, evaluation: Score) -> None:
        """Animate chunk based on `evaluation`."""
        if evaluation.is_mate():
            moves_to_mate: int = evaluation.mate() or 0
            animation_value: int = 0 if moves_to_mate > 0 else 1000
            evaluation_text: str = f"M{moves_to_mate}"
        else:
            evaluation_score: int = evaluation.score() or 0
            animation_value = 500 - evaluation_score
            evaluation_text = f"{evaluation_score / 100 :.2f}"

        self.setFormat(evaluation_text)
        self._animation.setEndValue(animation_value)
        self._animation.start()
