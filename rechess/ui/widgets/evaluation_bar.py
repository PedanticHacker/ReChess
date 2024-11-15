from chess import Color
from chess.engine import Score
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QProgressBar, QSizePolicy

from rechess.utils import setting_value


class EvaluationBar(QProgressBar):
    """Bar for animating position evaluation."""

    def __init__(self) -> None:
        super().__init__()

        self._size_policy = self.sizePolicy()
        self._size_policy.setRetainSizeWhenHidden(True)

        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.valueChanged.connect(self.update)

        self.setRange(0, 1000)
        self.setFixedSize(45, 500)
        self.setSizePolicy(self._size_policy)
        self.setOrientation(Qt.Orientation.Vertical)

        self.reset_appearance()

    def reset_appearance(self) -> None:
        """Hide widget and flip widget's chunk appearance."""
        self.hide()
        self.flip_appearance()

    def flip_appearance(self) -> None:
        """Flip widget's chunk appearance based on board orientation."""
        board_orientation: bool = setting_value("board", "orientation")
        self.setInvertedAppearance(board_orientation)

    def animate(self, evaluation: Score) -> None:
        """Animate widget's chunk to display `evaluation`."""
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
