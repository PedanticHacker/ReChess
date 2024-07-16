import json
from platform import system
from typing import Callable, Literal, overload, TypeAlias

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QPushButton


BoardSection: TypeAlias = Literal["board"]
ClockSection: TypeAlias = Literal["clock"]
EngineSection: TypeAlias = Literal["engine"]
SettingSection: TypeAlias = BoardSection | ClockSection | EngineSection

BoardKey: TypeAlias = Literal["orientation"]
ClockKey: TypeAlias = Literal["time", "increment"]
EngineKey: TypeAlias = Literal["is_pondering", "is_white"]
SettingKey: TypeAlias = BoardKey | ClockKey | EngineKey

SettingValue: TypeAlias = bool | float


def _optimal_hash_size() -> int:
    """Get 70% of available RAM in MB as optimal hash size."""
    available_ram = virtual_memory().available
    megabytes_factor = 1048576
    seventy_percent = 0.70
    return round(available_ram / megabytes_factor * seventy_percent)


def _optimal_cpu_threads() -> int:
    """Get optimal CPU threads, reserving 1 for other tasks."""
    available_threads = cpu_count(logical=True)
    reserved_threads = 1
    minimum_threads = 1
    return max(minimum_threads, available_threads - reserved_threads)


@overload
def setting_value(section: BoardSection, key: BoardKey) -> bool:
    ...


@overload
def setting_value(section: ClockSection, key: ClockKey) -> float:
    ...


@overload
def setting_value(section: EngineSection, key: EngineKey) -> bool:
    ...


def setting_value(section: SettingSection, key: SettingKey) -> SettingValue:
    """Get a JSON value of the `key` from the `section`."""
    with open("rechess/settings.json") as settings_file:
        settings_data = json.load(settings_file)
    return settings_data[section][key]


@overload
def set_setting_value(section: BoardSection, key: BoardKey, value: bool) -> None:
    ...


@overload
def set_setting_value(section: ClockSection, key: ClockKey, value: float) -> None:
    ...


@overload
def set_setting_value(section: EngineSection, key: EngineKey, value: bool) -> None:
    ...


def set_setting_value(
    section: SettingSection, key: SettingKey, value: SettingValue
) -> None:
    """Set the JSON `value` to the `key` for the `section`."""
    with open("rechess/settings.json") as settings_file:
        settings_data = json.load(settings_file)
    settings_data[section][key] = value

    with open("rechess/settings.json", mode="w", newline="\n") as settings_file:
        json.dump(settings_data, settings_file, indent=4)
        settings_file.write("\n")


def app_style(file_name: str) -> str:
    """Get an app style with the `file_name`."""
    with open(f"rechess/resources/styles/{file_name}.qss") as qss_file:
        return qss_file.read()


def create_action(
    name: str,
    icon: QIcon,
    shortcut: str,
    status_tip: str,
    handler: Callable,
) -> QAction:
    """Create an action for a toolbar or a menubar item."""
    action = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_button(icon: QIcon) -> QPushButton:
    button = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def engine_configuration() -> dict[str, int]:
    """Get the optimal configuration for a UCI chess engine."""
    return {"Hash": _optimal_hash_size(), "Threads": _optimal_cpu_threads()}


def stockfish_engine() -> str:
    """Return a path to the Stockfish chess engine."""
    return (
        f"rechess/resources/engines/stockfish-16.1/{system().lower()}/"
        f"stockfish{'.exe' if system() == 'Windows' else ''}"
    )


def svg_icon(file_name: str) -> QIcon:
    """Get an SVG icon with the `file_name`."""
    return QIcon(f"rechess/resources/icons/{file_name}.svg")
