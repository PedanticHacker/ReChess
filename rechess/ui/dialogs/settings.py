from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
)

from rechess.utils import set_setting_value, setting_value


Cancel: QDialogButtonBox.StandardButton = QDialogButtonBox.StandardButton.Cancel
Save: QDialogButtonBox.StandardButton = QDialogButtonBox.StandardButton.Save


class SettingsDialog(QDialog):
    """Dialog for editing and saving settings."""

    def __init__(self) -> None:
        super().__init__()

        self._initial_settings: dict[str, bool | float | str] = {
            "clock_increment": setting_value("clock", "increment"),
            "clock_time": setting_value("clock", "time"),
            "human_name": setting_value("human", "name"),
            "is_engine_ponder_on": setting_value("engine", "is_ponder_on"),
            "is_engine_white": setting_value("engine", "is_white"),
        }

        self._button_box: QDialogButtonBox = QDialogButtonBox(Save | Cancel)
        self._button_box.button(Save).setDisabled(True)

        self.set_title()
        self.create_groups()
        self.create_options()
        self.set_vertical_layout()
        self.connect_signals_to_slots()

    def set_title(self) -> None:
        """Set dialog title to be Settings."""
        self.setWindowTitle("Settings")

    def create_groups(self) -> None:
        """Create groups for related settings to be put together."""
        self._engine_group: QGroupBox = QGroupBox("Engine")
        self._human_name_group: QGroupBox = QGroupBox("Human name")
        self._time_control_group: QGroupBox = QGroupBox("Time control")

    def create_options(self) -> None:
        """Create options that represent settings."""
        self._engine_black_option: QRadioButton = QRadioButton()
        self._engine_black_option.setText("Black")
        self._engine_black_option.setChecked(not setting_value("engine", "is_white"))

        self._engine_white_option: QRadioButton = QRadioButton()
        self._engine_white_option.setText("White")
        self._engine_white_option.setChecked(setting_value("engine", "is_white"))

        self._engine_ponder_option: QCheckBox = QCheckBox()
        self._engine_ponder_option.setText("Ponder")
        self._engine_ponder_option.setChecked(setting_value("engine", "is_ponder_on"))

        self._clock_time_option: QComboBox = QComboBox()
        self._clock_time_option.addItem("1 minute", 60.0)
        self._clock_time_option.addItem("3 minutes", 180.0)
        self._clock_time_option.addItem("5 minutes", 300.0)
        self._clock_time_option.addItem("10 minutes", 600.0)
        self._clock_time_option.addItem("20 minutes", 1200.0)
        self._clock_time_option.addItem("30 minutes", 1800.0)
        self._clock_time_option.addItem("1 hour", 3600.0)
        self._clock_time_option.addItem("2 hours", 7200.0)
        self._clock_time_option.setCurrentIndex(
            self._clock_time_option.findData(setting_value("clock", "time"))
        )

        self._clock_increment_option: QComboBox = QComboBox()
        self._clock_increment_option.addItem("0 seconds", 0.0)
        self._clock_increment_option.addItem("6 seconds", 6.0)
        self._clock_increment_option.addItem("12 seconds", 12.0)
        self._clock_increment_option.addItem("30 seconds", 30.0)
        self._clock_increment_option.setCurrentIndex(
            self._clock_increment_option.findData(setting_value("clock", "increment"))
        )

        self._human_name_option: QLineEdit = QLineEdit()
        self._human_name_option.setMaxLength(24)
        self._human_name_option.setPlaceholderText("Human")
        self._human_name_option.setText(setting_value("human", "name"))

    def set_vertical_layout(self) -> None:
        """Set dialog layout for widgets to be vertically arranged."""
        human_name_layout: QVBoxLayout = QVBoxLayout()
        human_name_layout.addWidget(self._human_name_option)
        self._human_name_group.setLayout(human_name_layout)

        engine_layout: QVBoxLayout = QVBoxLayout()
        engine_layout.addWidget(self._engine_black_option)
        engine_layout.addWidget(self._engine_white_option)
        engine_layout.addWidget(self._engine_ponder_option)
        self._engine_group.setLayout(engine_layout)

        time_control_layout: QHBoxLayout = QHBoxLayout()
        time_control_layout.addWidget(self._clock_time_option)
        time_control_layout.addWidget(self._clock_increment_option)
        self._time_control_group.setLayout(time_control_layout)

        vertical_layout: QVBoxLayout = QVBoxLayout()
        vertical_layout.addWidget(self._human_name_group)
        vertical_layout.addWidget(self._engine_group)
        vertical_layout.addWidget(self._time_control_group)
        vertical_layout.addWidget(self._button_box)
        self.setLayout(vertical_layout)

    def connect_signals_to_slots(self) -> None:
        """Connect signals to appropriate slot methods."""
        self.accepted.connect(self.on_accepted)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self._clock_increment_option.currentIndexChanged.connect(self.on_edited)
        self._clock_time_option.currentIndexChanged.connect(self.on_edited)
        self._engine_black_option.toggled.connect(self.on_edited)
        self._engine_ponder_option.toggled.connect(self.on_edited)
        self._engine_white_option.toggled.connect(self.on_edited)
        self._human_name_option.textChanged.connect(self.on_edited)

    def disable_profile_groups(self) -> None:
        """Disable human name and time control groups."""
        self._human_name_group.setDisabled(True)
        self._time_control_group.setDisabled(True)

    def is_edited(self) -> bool:
        """Return True if any setting is edited."""
        current_settings: dict[str, bool | float | str] = {
            "clock_increment": self._clock_increment_option.currentData(),
            "clock_time": self._clock_time_option.currentData(),
            "human_name": self._human_name_option.text().strip() or "Human",
            "is_engine_ponder_on": self._engine_ponder_option.isChecked(),
            "is_engine_white": self._engine_white_option.isChecked(),
        }
        return current_settings != self._initial_settings

    @Slot()
    def on_edited(self) -> None:
        """Enable Save button if any setting is edited."""
        self._button_box.button(Save).setEnabled(self.is_edited())

    @Slot()
    def on_accepted(self) -> None:
        """Save settings for accepted dialog by Save button pressed."""
        set_setting_value(
            section="clock",
            key="time",
            value=self._clock_time_option.currentData(),
        )
        set_setting_value(
            section="clock",
            key="increment",
            value=self._clock_increment_option.currentData(),
        )
        set_setting_value(
            section="engine",
            key="is_white",
            value=self._engine_white_option.isChecked(),
        )
        set_setting_value(
            section="engine",
            key="is_ponder_on",
            value=self._engine_ponder_option.isChecked(),
        )
        set_setting_value(
            section="human",
            key="name",
            value=self._human_name_option.text().strip() or "Human",
        )
