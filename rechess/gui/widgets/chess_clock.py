from typing import Literal

from PySide6.QtWidgets import QLCDNumber
from PySide6.QtCore import QSize, Qt, QTimer, Slot

from rechess import ClockStyle
from rechess import get_config_value


class CountdownTimer(QTimer):
    """A 1-second countdown timer."""

    def __init__(self) -> None:
        super().__init__()

        self.setInterval(1000)
        self.setTimerType(Qt.TimerType.PreciseTimer)

    def start_timer(self) -> None:
        """Start the countdown timer."""
        self.start()

    def stop_timer(self) -> None:
        """Stop the countdown timer."""
        self.stop()


class ChessClock(QLCDNumber):
    """A digital chess clock with a 1-second countdown timer."""

    def __init__(self, clock_style: ClockStyle) -> None:
        super().__init__()

        self.setStyleSheet(clock_style)
        self.setFixedSize(QSize(200, 50))
        self.setSegmentStyle(self.SegmentStyle.Flat)

        self.countdown_timer: CountdownTimer = CountdownTimer()
        self.countdown_timer.timeout.connect(self.update_time)

        self.reset()

    def reset(self) -> None:
        """Reset the chess clock's time to values from the settings."""
        seconds: int = get_config_value("clock", "time")
        increment: int = get_config_value("clock", "increment")
        self.time: int = seconds + increment

        self.show_time()

    def show_time(self) -> None:
        """Show the current chess clock's time."""
        time_text, time_text_length = self.format_time()
        self.setDigitCount(time_text_length)
        self.display(time_text)

    def format_time(self) -> tuple[str, int]:
        """Format the chess clock's time as text and as text length."""
        hours, remaining_time = divmod(self.time, 3600)
        minutes, seconds = divmod(remaining_time, 60)

        text: str = (
            f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
            if hours
            else f"{minutes:02.0f}:{seconds:02.0f}"
        )
        text_length: int = len(text)
        return text, text_length

    @Slot()
    def update_time(self) -> None:
        """Subtract 1 second from the chess clock's time."""
        if self.time > 0:
            self.time -= 1
            self.show_time()
        else:
            self.countdown_timer.stop_timer()
            # self.notify_player_lost()
