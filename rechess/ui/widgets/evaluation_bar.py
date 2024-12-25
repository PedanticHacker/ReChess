from chess.engine import Score
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QProgressBar, QSizePolicy

from rechess.utils import setting_value


class EvaluationBar(QProgressBar):
    """Chunk animator based on evaluation score."""

    def __init__(self) -> None:
        super().__init__()

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.valueChanged.connect(self.update)

        self._size_policy: QSizePolicy = self.sizePolicy()
        self._size_policy.setRetainSizeWhenHidden(True)

        self.setRange(0, 1000)
        self.setFixedSize(50, 600)
        self.setSizePolicy(self._size_policy)
        self.setOrientation(Qt.Orientation.Vertical)

        self.reset_state()

    def reset_state(self) -> None:
        """Hide widget, set chunk to neutral evaluation, and flip it."""
        self.hide()
        self.reset()
        self.flip_chunk()

    def flip_chunk(self) -> None:
        """Flip chunk based on board orientation."""
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
