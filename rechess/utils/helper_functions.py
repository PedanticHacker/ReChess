import json
import os
import platform
import stat
import subprocess
from typing import Callable, Literal, TypeAlias, overload

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton


PATH_TO_SETTINGS_FILE: str = "rechess/settings.json"


BoardSection: TypeAlias = Literal["board"]
ClockSection: TypeAlias = Literal["clock"]
EngineSection: TypeAlias = Literal["engine"]
SettingSection: TypeAlias = BoardSection | ClockSection | EngineSection

BoardKey: TypeAlias = Literal["orientation"]
ClockKey: TypeAlias = Literal["time", "increment"]
EngineKey: TypeAlias = Literal["is_pondering", "is_white"]
SettingKey: TypeAlias = BoardKey | ClockKey | EngineKey

SettingValue: TypeAlias = bool | float
SettingsDict: TypeAlias = dict[str, dict[str, SettingValue]]


def platform_name() -> str:
    """Return platform name in lowercase."""
    name: str = platform.system().lower()
    return "macos" if name == "darwin" else name


def _stockfish_filename() -> str:
    """Return platform-specific filename of Stockfish chess engine."""
    return "stockfish.exe" if platform_name() == "windows" else "stockfish"


def path_to_stockfish() -> str:
    """Return path to executable file of Stockfish 17 chess engine."""
    return (
        f"rechess/assets/engines/stockfish-17/{platform_name()}"
        f"/{_stockfish_filename()}"
    )


def make_executable(path_to_file: str) -> None:
    """Make file at `path_to_file` be executable."""
    os.chmod(path_to_file, os.stat(path_to_file).st_mode | stat.S_IXUSR)


def delete_quarantine_attribute(path_to_file: str) -> None:
    """Delete quarantine attribute for file at `path_to_file` on macOS."""
    if platform_name() == "macos":
        file_attributes: str = subprocess.run(
            ["xattr", "-l", path_to_file],
            capture_output=True,
            text=True,
        ).stdout

        if "com.apple.quarantine" in file_attributes:
            subprocess.run(["xattr", "-d", "com.apple.quarantine", path_to_file])


def _optimal_cpu_threads() -> int:
    """Return all CPU threads, but reserve 1 for other CPU tasks."""
    cpu_threads: int | None = cpu_count()
    return 1 if not cpu_threads or cpu_threads == 1 else cpu_threads - 1


def _optimal_hash_size() -> int:
    """Return approximately 70% of available RAM."""
    SEVENTY_PERCENT: int = 1497966
    available_ram: int = virtual_memory().available
    return available_ram // SEVENTY_PERCENT


def engine_configuration() -> dict[str, int]:
    """Return optimal configuration for UCI chess engine."""
    return {"Hash": _optimal_hash_size(), "Threads": _optimal_cpu_threads()}


def _settings() -> SettingsDict:
    """Return all settings from settings file."""
    with open(PATH_TO_SETTINGS_FILE) as settings_file:
        return json.load(settings_file)


@overload
def setting_value(
    section: BoardSection,
    key: BoardKey,
) -> bool: ...


@overload
def setting_value(
    section: ClockSection,
    key: ClockKey,
) -> float: ...


@overload
def setting_value(
    section: EngineSection,
    key: EngineKey,
) -> bool: ...


def setting_value(
    section: SettingSection,
    key: SettingKey,
) -> SettingValue:
    """Return value of `key` from `section`."""
    settings: SettingsDict = _settings()
    return settings[section][key]


@overload
def set_setting_value(
    section: BoardSection,
    key: BoardKey,
    value: bool,
) -> None: ...


@overload
def set_setting_value(
    section: ClockSection,
    key: ClockKey,
    value: float,
) -> None: ...


@overload
def set_setting_value(
    section: EngineSection,
    key: EngineKey,
    value: bool,
) -> None: ...


def set_setting_value(
    section: SettingSection,
    key: SettingKey,
    value: SettingValue,
) -> None:
    """Set `value` to `key` for `section`."""
    settings_dict: SettingsDict = _settings()
    settings_dict[section][key] = value

    with open(
        PATH_TO_SETTINGS_FILE,
        mode="w",
        encoding="utf-8",
        newline="\n",
    ) as settings_file:
        json.dump(settings_dict, settings_file, indent=2)
        settings_file.write("\n")


def find_opening(fen: str) -> tuple[str, str] | None:
    """Return ECO code and opening name for `fen`."""
    with open("rechess/openings.json", encoding="utf-8") as json_file:
        openings = json.load(json_file)
    return openings.get(fen)


def initialize_app() -> QApplication:
    """Initialize app with basic settings."""
    app: QApplication = QApplication()
    app.setApplicationDisplayName("ReChess")
    app.setApplicationName("ReChess")
    app.setApplicationVersion("1.0")
    app.setDesktopFileName("ReChess")
    app.setStyle("fusion")
    app.setWindowIcon(svg_icon("logo"))
    return app


def create_action(
    handler: Callable,
    icon: QIcon,
    name: str,
    shortcut: str,
    status_tip: str,
) -> QAction:
    """Create action for menubar menu or toolbar button."""
    action: QAction = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_button(icon: QIcon) -> QPushButton:
    """Create button with `icon`."""
    button: QPushButton = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def style_icon(color: str) -> QIcon:
    """Return square icon filled with `color`."""
    pixmap: QPixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def svg_icon(filename: str) -> QIcon:
    """Return SVG icon from file at `filename`."""
    return QIcon(f":/icons/{filename}.svg")
