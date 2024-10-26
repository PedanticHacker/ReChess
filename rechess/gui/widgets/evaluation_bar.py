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
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.valueChanged.connect(self.update)

        self.setRange(0, 1000)
        self.setFixedSize(40, 500)
        self.setSizePolicy(self._size_policy)
        self.setOrientation(Qt.Orientation.Vertical)

        self.reset_appearance()

    def reset_appearance(self) -> None:
        """Hide widget and flip widget's chunk appearance."""
        self.hide()
        self.flip_appearance()

    def flip_appearance(self) -> None:
        """Flip widget's chunk appearance per chessboard orientation."""
        board_orientation: bool = setting_value("board", "orientation")
        self.setInvertedAppearance(board_orientation)

    def animate(self, evaluation: Score) -> None:
        """Animate widget's chunk from `evaluation`."""
        if evaluation.is_mate():
            animation_value: int = 0 if evaluation.mate() > 0 else 1000
            evaluation_text: str = f"M{evaluation.mate()}"
        else:
            animation_value = 500 - evaluation.score()
            evaluation_text = f"{evaluation.score() / 100 :.2f}"

        self.setFormat(evaluation_text)
        self._animation.setEndValue(animation_value)
        self._animation.start()
