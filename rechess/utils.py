from json import dump, load
from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QPushButton


def create_action(
    name: str,
    icon: QIcon,
    shortcut: str,
    status_tip: str,
    handler: Callable,
) -> QAction:
    """Create an action for a tool bar item or a menu bar item."""
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


def get_app_style(file_name: str) -> str:
    """Get an app style by the given `file_name`."""
    with open(f"rechess/resources/styles/{file_name}.qss") as qss_file:
        return qss_file.read()


def get_config_value(section: str, key: str) -> int | bool:
    """Get the config value of a `key` from the given `section`."""
    with open("rechess/config.json") as config_file:
        config_contents = load(config_file)

    return config_contents[section][key]


def set_config_values(new_config_values: dict[str, dict[str, int | bool]]) -> None:
    """Set config values from the given `new_config_values`."""
    with open("rechess/config.json") as config_file:
        config_contents = load(config_file)

    config_contents |= new_config_values

    with open("rechess/config.json", mode="w", newline="\n") as config_file:
        dump(config_contents, config_file, indent=4)
        config_file.write("\n")


def get_svg_icon(file_name: str) -> QIcon:
    """Get an SVG icon from the given `file_name`."""
    return QIcon(f"rechess/resources/icons/{file_name}.svg")


def get_openings() -> dict[str, tuple[str, str]]:
    """Get a dictionary of openings."""
    return {}
