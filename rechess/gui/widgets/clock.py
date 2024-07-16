from PySide6.QtCore import QElapsedTimer, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QLCDNumber

from rechess.enums import ClockColor
from rechess.utils import setting_value


class Clock(QLCDNumber):
    """A clock with a countdown timer precise to 20 milliseconds."""

    time_expired: Signal = Signal()

    def __init__(self, clock_color: ClockColor) -> None:
        super().__init__()

        self.setStyleSheet(clock_color)
        self.setFixedSize(200, 50)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self._countdown_timer: QTimer = QTimer(self)
        self._countdown_timer.setInterval(20)
        self._countdown_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._countdown_timer.timeout.connect(self.update_time)

        self._elapsed_timer: QElapsedTimer = QElapsedTimer()

        self.reset()

    def reset(self) -> None:
        """Reset the clock's time to values from the settings."""
        seconds: float = setting_value("clock", "time")
        increment: float = setting_value("clock", "increment")
        self.time: float = seconds + increment
        self.display_time()

    def display_time(self) -> None:
        """Display the clock's time."""
        time_text: str = self.format_time()
        self.setDigitCount(len(time_text))
        self.display(time_text)

    def format_time(self) -> str:
        """Format the clock's time as text."""
        total_seconds: int = round(self.time)
        hours, remaining_time = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remaining_time, 60)
        return (
            f"{hours:02}:{minutes:02}:{seconds:02}"
            if hours
            else f"{minutes:02}:{seconds:02}"
        )

    def start_timer(self) -> None:
        """Start the countdown timer."""
        self._elapsed_timer.start()
        self._countdown_timer.start()

    def stop_timer(self) -> None:
        """Stop the countdown timer and update the remaining time."""
        if self._countdown_timer.isActive():
            self.update_elapsed_time()
            self._countdown_timer.stop()

    def update_elapsed_time(self) -> None:
        """Update the remaining time by subtracting the elapsed time."""
        elapsed_time: float = self._elapsed_timer.elapsed() / 1000.0
        self.time -= elapsed_time
        self._elapsed_timer.restart()
        self.display_time()

    @Slot()
    def update_time(self) -> None:
        """Update the remaining clock's time."""
        self.update_elapsed_time()

        if not self.time:
            self._countdown_timer.stop()
            self.time_expired.emit()
