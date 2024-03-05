from pathlib import Path

from chess import Move
from chess.engine import Score
from PySide6.QtCore import QThreadPool, Slot
from PySide6.QtGui import QCloseEvent, QWheelEvent
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QStatusBar,
    QFileDialog,
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
)

from rechess import ClockStyle
from rechess.gui.dialogs import SettingsDialog
from rechess.core import Engine, Game, TableModel
from rechess import create_action, get_opening_from, get_svg_icon
from rechess.gui.widgets import (
    Clock,
    SVGBoard,
    FENEditor,
    TableView,
    EvaluationBar,
)


class MainWindow(QMainWindow):
    """The main window of ReChess."""

    def __init__(self) -> None:
        super().__init__()

        self.create_widgets()
        self.create_actions()
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.set_personal_layout()
        self.connect_events_with_handlers()

    def create_widgets(self) -> None:
        """Create widgets for the main window."""
        self._game: Game = Game()
        self._engine: Engine = Engine()
        self._table_model: TableModel = TableModel(Game.notation)

        self._svg_board: SVGBoard = SVGBoard()
        self._fen_editor: FENEditor = FENEditor()
        self._black_clock: Clock = Clock(ClockStyle.Black)
        self._white_clock: Clock = Clock(ClockStyle.White)
        self._evaluation_bar: EvaluationBar = EvaluationBar()
        self._table_view: TableView = TableView(self._table_model)

        self._opening_label: QLabel = QLabel()
        self._notifications_label: QLabel = QLabel()
        self._engine_name_label: QLabel = QLabel(self._engine.name)

    def create_actions(self) -> None:
        """Create actions for menu bar and tool bar."""
        self.about_action = create_action(
            name="About",
            shortcut="Ctrl+I",
            handler=self.show_about,
            icon=get_svg_icon("about"),
            status_tip="Shows the About message.",
        )
        self.flip_action = create_action(
            name="Flip",
            handler=self.flip,
            shortcut="Ctrl+Shift+F",
            icon=get_svg_icon("flip"),
            status_tip="Flips the viewpoint.",
        )
        self.load_engine_action = create_action(
            shortcut="Ctrl+E",
            name="Load engine...",
            handler=self.load_engine,
            icon=get_svg_icon("load-engine"),
            status_tip="Shows the file manager.",
        )
        self.new_game_action = create_action(
            name="New game",
            shortcut="Ctrl+Shift+N",
            handler=self.offer_new_game,
            icon=get_svg_icon("new-game"),
            status_tip="Offers a new game.",
        )
        self.push_move_now_action = create_action(
            name="Push move now",
            shortcut="Ctrl+Shift+P",
            handler=self.push_move_now,
            icon=get_svg_icon("push-move-now"),
            status_tip="Forces the chess engine to push a move.",
        )
        self.settings_action = create_action(
            name="Settings...",
            shortcut="Ctrl+Shift+S",
            icon=get_svg_icon("settings"),
            handler=self.show_settings_dialog,
            status_tip="Shows the Settings dialog.",
        )
        self.start_analysis_action = create_action(
            name="Start analysis",
            shortcut="Ctrl+Shift+A",
            handler=self.start_analysis,
            icon=get_svg_icon("start-analysis"),
            status_tip="Starts chess engine analysis.",
        )
        self.stop_analysis_action = create_action(
            name="Stop analysis",
            shortcut="Ctrl+Shift+X",
            handler=self.stop_analysis,
            icon=get_svg_icon("stop-analysis"),
            status_tip="Stops chess engine analysis.",
        )
        self.quit_action = create_action(
            name="Quit...",
            handler=self.quit,
            shortcut="Ctrl+Q",
            icon=get_svg_icon("quit"),
            status_tip="Offers to quit RexChess.",
        )

    def create_menu_bar(self) -> None:
        """Create a menu bar with actions in separate menus."""

        # Menu bar
        menu_bar = self.menuBar()

        # General menu
        general_menu = menu_bar.addMenu("General")

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        # General menu > Load engine...
        general_menu.addAction(self.load_engine_action)

        # General menu separator
        general_menu.addSeparator()

        # General menu > Quit...
        general_menu.addAction(self.quit_action)

        # Edit menu > Settings...
        edit_menu.addAction(self.settings_action)

        # Help menu > About
        help_menu.addAction(self.about_action)

    def create_tool_bar(self) -> None:
        """Create a tool bar with buttons in separate areas."""

        # General area
        general_area = self.addToolBar("General")

        # Edit area
        edit_area = self.addToolBar("Edit")

        # Help area
        help_area = self.addToolBar("Help")

        # General area > Quit
        general_area.addAction(self.quit_action)

        # Edit area > New game
        edit_area.addAction(self.new_game_action)

        # Edit area > Flip sides
        edit_area.addAction(self.flip_action)

        # Edit area > Push move now
        edit_area.addAction(self.push_move_now_action)

        # Edit area > Start analysis
        edit_area.addAction(self.start_analysis_action)

        # Edit area > Stop analysis
        edit_area.addAction(self.stop_analysis_action)

        # Edit area > Settings
        edit_area.addAction(self.settings_action)

        # Edit area > Load engine
        edit_area.addAction(self.load_engine_action)

        # Help area > About
        help_area.addAction(self.about_action)

    def create_status_bar(self) -> None:
        """Create a status bar to show various information."""
        status_bar: QStatusBar = self.statusBar()
        status_bar.addWidget(self._opening_label)
        status_bar.addPermanentWidget(self._engine_name_label)
        self._engine_name_label.setText(self._engine.name)

    def set_personal_layout(self) -> None:
        """Set a personal layout for widgets on the main window."""
        self._clock_layout: QVBoxLayout = QVBoxLayout()
        self._clock_layout.addWidget(self._black_clock)
        self._clock_layout.addSpacing(550)
        self._clock_layout.addWidget(self._white_clock)

        self.grid_layout: QGridLayout = QGridLayout()
        self.grid_layout.addLayout(self._clock_layout, 0, 0)
        self.grid_layout.addWidget(self._svg_board, 0, 1)
        self.grid_layout.addWidget(self._evaluation_bar, 0, 2)
        self.grid_layout.addWidget(self._table_view, 0, 3)
        self.grid_layout.addWidget(self._fen_editor, 1, 1)
        self.grid_layout.addWidget(self._notifications_label, 2, 1)

        self.widget_container: QWidget = QWidget()
        self.widget_container.setLayout(self.grid_layout)
        self.setCentralWidget(self.widget_container)

        if self._game.is_orientation_flipped():
            self.flip_clocks()

    def connect_events_with_handlers(self) -> None:
        """Connect `move_played` event with `push_engine_move` handler."""
        self._engine.engine_move_pushed.connect(self.push_engine_move)
        self._engine.engine_analysis_updated.connect(self.show_engine_analysis)

    def invoke_engine(self) -> None:
        """Invoke the currently loaded engine to play a move."""
        QThreadPool.globalInstance().start(self._engine.play_move)

    def invoke_analysis(self) -> None:
        """Invoke the loaded engine to start an analysis."""
        QThreadPool.globalInstance().start(self._engine.start_analysis)

    def show_maximized(self) -> None:
        """Show the main window in maximized size."""
        self.showMaximized()

    def quit(self) -> None:
        """Trigger the main window's close event."""
        self.close()

    def flip(self) -> None:
        """Flip the orientation of clocks, board and evaluation bar."""
        self.flip_clocks()
        self._svg_board.flip_board()
        self._evaluation_bar.flip_orientation()
        self._svg_board.draw()

    def push_move_now(self) -> None:
        """Pass the turn to the loaded engine to push a move."""
        self._game.pass_turn_to_engine()

    def show_settings_dialog(self) -> None:
        """Show the Settings dialog."""
        settings_dialog: SettingsDialog = SettingsDialog()
        settings_dialog.exec()

    def load_engine(self) -> None:
        """Show the file manager to load a UCI engine."""
        engine_file, _ = QFileDialog.getOpenFileName(
            self,
            "File Manager",
            Path.home().as_posix(),
            "UCI chess engine (*.exe)",
        )

        if engine_file:
            self._engine.load(engine_file)
            self.invoke_engine()

    def show_about(self) -> None:
        """Show the About message."""
        QMessageBox.about(
            self,
            "About",
            (
                "A GUI app for playing chess against a UCI engine.\n\n"
                "Copyright 2024 Boštjan Mejak\n"
                "MIT License"
            ),
        )

    def flip_clocks(self) -> None:
        """Flip the bottom and top chess clocks."""
        bottom_clock = self._clock_layout.takeAt(2).widget()
        top_clock = self._clock_layout.takeAt(0).widget()
        self._clock_layout.insertWidget(0, bottom_clock)
        self._clock_layout.insertWidget(2, top_clock)

    def start_analysis(self) -> None:
        """Start analyzing the current chessboard position."""
        self.invoke_analysis()
        self._evaluation_bar.show()

    def stop_analysis(self) -> None:
        """Stop analyzing the current chessboard position."""
        self._engine.stop_analysis()

    def show_fen(self) -> None:
        """Show a FEN (Forsyth-Edwards Notation) in the FEN editor."""
        self._fen_editor.reset_background_color()
        self._fen_editor.setText(self._game.position.fen())

    def show_evaluation(self, evaluation: Score) -> None:
        """Show position evaluation by the given `evaluation`."""
        self._evaluation_bar.animate(evaluation)

    def show_variation(self, variation: str) -> None:
        """Show a variation of chess moves by the given `variation`."""
        self._notifications_label.setText(variation)

    def show_opening(self) -> None:
        """Show an ECO code along with a chess opening name."""
        variation: str = self._game.variation
        eco_code, opening_name = get_opening_from(variation)
        self._opening_label.setText(f"{eco_code}: {opening_name}")

    def update_game_state(self) -> None:
        """Update the current state of a game."""
        self.show_opening()
        self.toggle_clock_state()
        self._evaluation_bar.reset()
        self._engine.stop_analysis()

        if self._game.is_game_over():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(self.get_result())

            self.offer_new_game()

        if self._engine.has_resigned():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(f"{self._engine.name} has resigned!")

        self._svg_board.draw()

    def toggle_clock_state(self) -> None:
        """Toggle the started/stopped state of both clocks."""
        if self._game.is_white_on_turn():
            self._black_clock.stop_timer()
            self._white_clock.start_timer()
        else:
            self._white_clock.stop_timer()
            self._black_clock.start_timer()

    def show_result(self) -> str:
        """Show the result of a game."""
        result_rewordings = {
            "1/2-1/2": "Draw",
            "0-1": "Black wins!",
            "1-0": "White wins!",
            "*": "Undetermined game",
        }
        return result_rewordings[self._board.result()]

    def offer_new_game(self) -> None:
        """Offer to start a new game."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "New Game",
            "Do you want to start a new game?",
        )

        if answer == answer.Yes:
            self.start_new_game()

    def start_new_game(self) -> None:
        """Start a new game by resetting everything."""
        if self._game.is_orientation_flipped():
            self.flip_clocks()

        self._black_clock.reset()
        self._white_clock.reset()
        self._opening_label.clear()
        self._table_model.refresh()
        self._engine.stop_analysis()
        self._evaluation_bar.reset()
        self._game.prepare_new_game()
        self._notifications_label.clear()

        self.toggle_clocks()
        self.invoke_engine()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Respond to the event of closing the main window of ReChess.

        Ask the user with a dialog whether ReChess should quit before
        the main window is closed.
        """
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Quit",
            "Do you want to quit ReChess?",
        )

        if answer == answer.Yes:
            self._engine.quit()
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Respond to the event of rolling the wheel of a pointing device.

        This event handler deals with wheel events of either a mouse or
        a touchpad, be it an upward or a downward roll of the wheel.
        """
        upward_roll = event.angleDelta().y() > 0
        downward_roll = event.angleDelta().y() < 0

        if upward_roll:
            self._table_view.select_preceding_item()
        elif downward_roll:
            self._table_view.select_following_item()

    @Slot(Move)
    def push_engine_move(self, move: Move) -> None:
        """Push the given `move` made by the engine."""
        self._game.push(move)
        self.update_game_state()

    @Slot(str)
    def show_engine_analysis(self, variation: str) -> None:
        self._notifications_label.setText(variation)
