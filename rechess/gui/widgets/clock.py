from typing import Literal

from PySide6.QtWidgets import QLCDNumber
from PySide6.QtCore import QSize, Qt, QTimer, Slot

from rechess import ClockStyle
from rechess import get_config_value


class Clock(QLCDNumber):
    """A clock with a 1-second countdown timer."""

    def __init__(self, style: ClockStyle) -> None:
        super().__init__()

        self.setStyleSheet(style)
        self.setFixedSize(QSize(200, 50))
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self._countdown_timer: QTimer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._countdown_timer.timeout.connect(self.update_time)

        self.reset()

    def reset(self) -> None:
        """Reset the clock's time to values from the settings."""
        seconds: int = get_config_value("clock", "time")
        increment: int = get_config_value("clock", "increment")
        self.time: int = seconds + increment

        self.show_time()

    def show_time(self) -> None:
        """Show the current clock's time."""
        time_text, time_text_length = self.format_time()
        self.setDigitCount(time_text_length)
        self.display(time_text)

    def format_time(self) -> tuple[str, int]:
        """Format the clock's time as text and as text length."""
        hours, remaining_time = divmod(self.time, 3600)
        minutes, seconds = divmod(remaining_time, 60)

        text: str = (
            f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
            if hours
            else f"{minutes:02.0f}:{seconds:02.0f}"
        )
        text_length: int = len(text)
        return text, text_length

    def start_timer(self) -> None:
        """Start the countdown timer."""
        self._countdown_timer.start()

    def stop_timer(self) -> None:
        """Stop the countdown timer."""
        self._countdown_timer.stop()

    @Slot()
    def update_time(self) -> None:
        """Subtract 1 second from the clock's time."""
        if self.time > 0:
            self.time -= 1
            self.show_time()
        else:
            self._countdown_timer.stop()
            # self.notify_player_lost()