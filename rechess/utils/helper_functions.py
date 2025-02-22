from __future__ import annotations

import json
import os
import platform
import stat
import subprocess
import sys
from typing import Any, Callable

from psutil import cpu_count, virtual_memory
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton


def path_to_stockfish() -> str:
    """Return path to executable file of Stockfish 17 engine."""
    system: str = platform.system()
    suffix: str = ".exe" if system == "Windows" else ""
    return f"rechess/assets/engines/stockfish-17/{system}/stockfish{suffix}"


def engine_file_filter() -> str:
    """Return platform-specific filter for engine's executable file."""
    return "Chess engine (*.exe)" if platform.system() == "Windows" else ""


def delete_quarantine_attribute(path_to_file: str) -> None:
    """Delete quarantine attribute for file at `path_to_file`."""
    if platform.system() == "Darwin":
        subprocess.run(
            ["xattr", "-d", "com.apple.quarantine", path_to_file],
            stderr=subprocess.DEVNULL,
        )


def make_executable(path_to_file: str) -> None:
    """Make file at `path_to_file` be executable."""
    if platform.system() == "Linux":
        os.chmod(path_to_file, os.stat(path_to_file).st_mode | stat.S_IXUSR)


def _available_hash() -> int:
    """Return all available RAM in megabytes to be used as hash."""
    megabytes_factor: int = 1_048_576
    return virtual_memory().available // megabytes_factor


def _available_threads() -> int:
    """Return all available CPU threads, else at least one."""
    cpu_threads: int | None = cpu_count()
    return cpu_threads if cpu_threads is not None else 1


def engine_configuration() -> dict[str, int]:
    """Return configuration for engine based on available resources."""
    return {"Hash": _available_hash(), "Threads": _available_threads()}


def _settings() -> dict[str, dict[str, Any]]:
    """Return all settings from settings.json file."""
    with open("rechess/settings.json") as settings_file:
        return json.load(settings_file)


def setting_value(section: str, key: str) -> Any:
    """Return value of `key` from `section`."""
    settings_dict: dict[str, dict[str, Any]] = _settings()
    return settings_dict[section][key]


def set_setting_value(section: str, key: str, value: Any) -> None:
    """Set `value` to `key` for `section`."""
    settings_dict: dict[str, dict[str, Any]] = _settings()
    settings_dict[section][key] = value

    with open(
        "rechess/settings.json", mode="w", newline="\n"
    ) as settings_file:
        json.dump(settings_dict, settings_file, indent=2)
        settings_file.write("\n")


def find_opening(fen: str) -> tuple[str, str] | None:
    """Return ECO code and opening name based on `fen`."""
    with open("rechess/openings.json", encoding="utf-8") as json_file:
        openings = json.load(json_file)
    return openings.get(fen)


def style_name(filename: str) -> str:
    """Return human-readable style name based on `filename`."""
    styles: dict[str, str] = {
        "dark-forest": "Dark forest",
        "dark-mint": "Dark mint",
        "dark-nebula": "Dark nebula",
        "dark-ocean": "Dark ocean",
        "light-forest": "Light forest",
        "light-mint": "Light mint",
        "light-nebula": "Light nebula",
        "light-ocean": "Light ocean",
    }
    return styles[filename]


def show_warning(parent: MainWindow) -> None:
    """Warn about ReChess already running."""
    title: str = "Warning"
    text: str = "ReChess is already running!"
    QMessageBox.warning(parent, title, text)
    parent.destruct()
    sys.exit()


def create_action(
    handler: Callable, icon: QIcon, name: str, shortcut: str, status_tip: str
) -> QAction:
    """Create action for menubar menu or toolbar button."""
    action: QAction = QAction(icon, name)
    action.setShortcut(shortcut)
    action.setStatusTip(status_tip)
    action.triggered.connect(handler)
    return action


def create_app() -> QApplication:
    """Initialize QApplication with basic settings and return it."""
    app: QApplication = QApplication()
    app.setApplicationDisplayName("ReChess")
    app.setApplicationName("ReChess")
    app.setApplicationVersion("1.0")
    app.setDesktopFileName("ReChess")
    app.setStyle("fusion")
    app.setWindowIcon(svg_icon("logo"))
    return app


def create_button(icon: QIcon) -> QPushButton:
    """Create button with `icon`."""
    button: QPushButton = QPushButton()
    button.setIcon(icon)
    button.setIconSize(QSize(56, 56))
    return button


def colorize_icon(color: str) -> QIcon:
    """Return icon in 16 by 16 pixels filled with `color`."""
    pixmap: QPixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def svg_icon(filename: str) -> QIcon:
    """Return SVG icon from file at `filename`."""
    return QIcon(f":/icons/{filename}.svg")
