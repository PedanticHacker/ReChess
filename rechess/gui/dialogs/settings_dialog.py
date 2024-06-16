from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
)

from rechess.utils import get_config_value, set_config_value


class SettingsDialog(QDialog):
    """A dialog for changing the settings."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Settings")

        self._engine_group: QGroupBox = QGroupBox()
        self._engine_group.setTitle("Engine")
        # self._engine_group.setDisabled()

        self._time_control_group: QGroupBox = QGroupBox()
        self._time_control_group.setTitle("Time control")
        # self._time_control_group.setDisabled()

        self.create_options()
        self.set_vertical_layout()
        self.connect_events_with_handlers()

    def create_options(self) -> None:
        """Create options that will represent the settings."""
        is_engine_white: bool = get_config_value("engine", "white")
        is_engine_pondering: bool = get_config_value("engine", "pondering")

        clock_time: int = get_config_value("clock", "time")
        clock_increment: int = get_config_value("clock", "increment")

        self._engine_black_option: QRadioButton = QRadioButton()
        self._engine_black_option.setText("Black")
        self._engine_black_option.setChecked(not is_engine_white)

        self._engine_white_option: QRadioButton = QRadioButton()
        self._engine_white_option.setText("White")
        self._engine_white_option.setChecked(is_engine_white)

        self._engine_pondering_option: QCheckBox = QCheckBox()
        self._engine_pondering_option.setText("Pondering")
        self._engine_pondering_option.setChecked(is_engine_pondering)

        self._clock_time_option: QComboBox = QComboBox()
        self._clock_time_option.addItem("1 minute", 60)
        self._clock_time_option.addItem("3 minutes", 180)
        self._clock_time_option.addItem("5 minutes", 300)
        self._clock_time_option.addItem("10 minutes", 600)
        self._clock_time_option.addItem("20 minutes", 1200)
        self._clock_time_option.addItem("30 minutes", 1800)
        self._clock_time_option.addItem("1 hour", 3600)
        self._clock_time_option.addItem("2 hours", 7200)
        self._clock_time_option.setCurrentIndex(
            self._clock_time_option.findData(clock_time)
        )

        self._clock_increment_option: QComboBox = QComboBox()
        self._clock_increment_option.addItem("0 seconds", 0)
        self._clock_increment_option.addItem("6 seconds", 6)
        self._clock_increment_option.addItem("12 seconds", 12)
        self._clock_increment_option.addItem("30 seconds", 30)
        self._clock_increment_option.setCurrentIndex(
            self._clock_increment_option.findData(clock_increment)
        )

    def set_vertical_layout(self) -> None:
        """Set a vertical layout for the dialog."""
        self._button_box: QDialogButtonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        engine_layout: QVBoxLayout = QVBoxLayout()
        engine_layout.addWidget(self._engine_black_option)
        engine_layout.addWidget(self._engine_white_option)
        engine_layout.addWidget(self._engine_pondering_option)
        self._engine_group.setLayout(engine_layout)

        time_control_layout: QHBoxLayout = QHBoxLayout()
        time_control_layout.addWidget(self._clock_time_option)
        time_control_layout.addWidget(self._clock_increment_option)
        self._time_control_group.setLayout(time_control_layout)

        vertical_layout: QVBoxLayout = QVBoxLayout()
        vertical_layout.addWidget(self._engine_group)
        vertical_layout.addWidget(self._time_control_group)
        vertical_layout.addWidget(self._button_box)
        self.setLayout(vertical_layout)

    def connect_events_with_handlers(self) -> None:
        """Connect various events with specific handlers."""
        self.accepted.connect(self.on_save_settings)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

    @Slot()
    def on_save_settings(self) -> None:
        """Save any changed settings."""
        set_config_value(
            section="clock",
            key="time",
            value=self._clock_time_option.currentData(),
        )
        set_config_value(
            section="clock",
            key="increment",
            value=self._clock_increment_option.currentData(),
        )
        set_config_value(
            section="engine",
            key="white",
            value=self._engine_white_option.isChecked(),
        )
        set_config_value(
            section="engine",
            key="pondering",
            value=self._engine_pondering_option.isChecked(),
        )
