from pathlib import Path

from chess import Move
from chess.engine import Score
from PySide6.QtCore import Qt, QThreadPool, Slot
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

from rechess.gui.dialogs import SettingsDialog
from rechess.core import Engine, Game, TableModel
from rechess import create_action, get_openings, get_svg_icon
from rechess.gui.widgets import (
    Clock,
    SvgBoard,
    FenEditor,
    TableView,
    EvaluationBar,
)


BLACK_CLOCK_STYLE: str = "color: white; background: black;"
WHITE_CLOCK_STYLE: str = "color: black; background: white;"

TOP: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop
BOTTOM: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignBottom


class MainWindow(QMainWindow):
    """The main window of ReChess."""

    def __init__(self) -> None:
        super().__init__()

        self.create_widgets()
        self.create_actions()
        self.create_menu_bar()
        self.create_tool_bar()
        self.set_grid_layout()
        self.set_minimum_size()
        self.create_status_bar()
        self.adjust_engine_buttons()
        self.connect_events_with_handlers()

    def create_widgets(self) -> None:
        """Create widgets for the main window."""
        self._game: Game = Game()
        self._engine: Engine = Engine(self._game)
        self._svg_board: SvgBoard = SvgBoard(self._game)
        self._fen_editor: FenEditor = FenEditor(self._game)
        self._evaluation_bar: EvaluationBar = EvaluationBar(self._game)

        self._table_model: TableModel = TableModel(self._game.notation)
        self._table_view: TableView = TableView(self._table_model)

        self._black_clock: Clock = Clock(BLACK_CLOCK_STYLE)
        self._white_clock: Clock = Clock(WHITE_CLOCK_STYLE)

        self._opening_label: QLabel = QLabel()
        self._engine_name_label: QLabel = QLabel()
        self._notifications_label: QLabel = QLabel()
        self._engine_analysis_label: QLabel = QLabel()
        self._engine_analysis_label.setWordWrap(True)

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
            status_tip="Flips the current perspective.",
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
        self.play_move_now_action = create_action(
            name="Play move now",
            shortcut="Ctrl+Shift+P",
            handler=self.play_move_now,
            icon=get_svg_icon("play-move-now"),
            status_tip="Forces the engine to play a move.",
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
            status_tip="Starts the engine analysis.",
        )
        self.stop_analysis_action = create_action(
            name="Stop analysis",
            shortcut="Ctrl+Shift+X",
            handler=self.stop_analysis,
            icon=get_svg_icon("stop-analysis"),
            status_tip="Stops the engine analysis.",
        )
        self.quit_action = create_action(
            name="Quit...",
            handler=self.quit,
            shortcut="Ctrl+Q",
            icon=get_svg_icon("quit"),
            status_tip="Offers to quit ReChess.",
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

        # Edit area > Play move now
        edit_area.addAction(self.play_move_now_action)

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
        self.statusBar().addWidget(self._opening_label)
        self.statusBar().addPermanentWidget(self._engine_name_label)
        self._engine_name_label.setText(self._engine.name)

    def set_grid_layout(self) -> None:
        """Set a grid layout for widgets on the main window."""
        self._grid_layout: QGridLayout = QGridLayout()
        self._grid_layout.addWidget(self._black_clock, 0, 0, 1, 1, TOP)
        self._grid_layout.addWidget(self._white_clock, 0, 0, 1, 1, BOTTOM)
        self._grid_layout.addWidget(self._svg_board, 0, 1, 1, 1)
        self._grid_layout.addWidget(self._evaluation_bar, 0, 2, 1, 1)
        self._grid_layout.addWidget(self._table_view, 0, 3, 1, 2)
        self._grid_layout.addWidget(self._notifications_label, 1, 3, 1, 1)
        self._grid_layout.addWidget(self._fen_editor, 1, 1, 1, 1)
        self._grid_layout.addWidget(self._engine_analysis_label, 2, 1, 1, 1, TOP)

        self._widget_container: QWidget = QWidget()
        self._widget_container.setLayout(self._grid_layout)
        self.setCentralWidget(self._widget_container)

        if self._game.is_perspective_flipped():
            self.flip_clock_positions()

    def set_minimum_size(self) -> None:
        """Set a minimum size to be 1000 by 700 pixels."""
        self.setMinimumSize(1000, 700)

    def adjust_engine_buttons(self) -> None:
        """Adjust the state of the engine's tool bar buttons."""
        self.play_move_now_action.setEnabled(True)
        self.start_analysis_action.setEnabled(True)
        self.stop_analysis_action.setDisabled(True)

        if self._game.is_game_over():
            self.play_move_now_action.setDisabled(True)
            self.stop_analysis_action.setDisabled(True)
            self.start_analysis_action.setDisabled(True)

    def connect_events_with_handlers(self) -> None:
        """Connect various events with specific handlers."""
        self._game.move_played.connect(self.on_move_played)
        self._engine.move_played.connect(self.on_move_played)
        self._table_view.index_selected.connect(self.on_index_selected)
        self._engine.best_move_analyzed.connect(self.on_best_move_analyzed)
        self._engine.white_score_analyzed.connect(self.on_white_score_analyzed)
        self._black_clock.time_expired.connect(self.on_black_clock_time_expired)
        self._white_clock.time_expired.connect(self.on_white_clock_time_expired)
        self._engine.san_variation_analyzed.connect(self.on_san_variation_analyzed)

    def invoke_engine(self) -> None:
        """Invoke the loaded engine to play a move."""
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
        """Flip the current perspective."""
        self.flip_clock_positions()
        self._game.flip_perspective()
        self._evaluation_bar.flip_perspective()
        self._svg_board.draw()

    def play_move_now(self) -> None:
        """Pass the turn to the loaded engine to play a move."""
        self._game.pass_turn_to_engine()

        self.flip()
        self.invoke_engine()

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
            self.start_new_engine(engine_file)

    def start_new_engine(self, engine_file: str) -> None:
        """Load a new engine from `engine_file`."""
        self.stop_analysis()
        self._game.arrow.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self._engine.load(engine_file)
        self._engine_name_label.setText(self._engine.name)

        self._svg_board.draw()

        if self._game.is_engine_on_turn():
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

    def flip_clock_positions(self) -> None:
        """Flip the position of the top and the bottom clocks."""
        if TOP in self._grid_layout.itemAt(0).alignment():
            self._grid_layout.itemAt(0).setAlignment(BOTTOM)
            self._grid_layout.itemAt(1).setAlignment(TOP)
        else:
            self._grid_layout.itemAt(0).setAlignment(TOP)
            self._grid_layout.itemAt(1).setAlignment(BOTTOM)

        self._grid_layout.update()

    def start_analysis(self) -> None:
        """Start analyzing the current position."""
        self.invoke_analysis()
        self._evaluation_bar.show()
        self.stop_analysis_action.setEnabled(True)
        self.start_analysis_action.setDisabled(True)

    def stop_analysis(self) -> None:
        """Stop analyzing the current position."""
        self._engine.stop_analysis()
        self.adjust_engine_buttons()

    def show_fen(self) -> None:
        """Show a FEN (Forsyth-Edwards Notation) in the FEN editor."""
        self._fen_editor.reset_background_color()
        self._fen_editor.setText(self._game.fen)

    def show_opening(self) -> None:
        """Show an ECO code along with an opening name."""
        fen: str = self._game.fen
        openings: dict[str, tuple[str, str]] = get_openings()

        if fen in openings:
            eco_code, opening_name = openings[fen]
            self._opening_label.setText(f"{eco_code}: {opening_name}")

    def refresh_ui(self) -> None:
        """Refresh the current UI's state to a new state."""
        self._engine.stop_analysis()
        self._table_model.refresh_view()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.show_opening()
        self.switch_clock_timers()
        self.adjust_engine_buttons()

        self._svg_board.draw()

        if self._game.is_game_over():
            self._black_clock.stop_timer()
            self._white_clock.stop_timer()
            self._notifications_label.setText(self._game.result)
            self.offer_new_game()

        if self._game.is_engine_on_turn() and not self._table_view.has_selection():
            self.invoke_engine()

    def switch_clock_timers(self) -> None:
        """Activate the clock's timer for the player on turn."""
        if self._game.is_white_on_turn():
            self._black_clock.stop_timer()
            self._white_clock.start_timer()
        else:
            self._white_clock.stop_timer()
            self._black_clock.start_timer()

    def offer_new_game(self) -> None:
        """Show a dialog offering to start a new game."""
        answer: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "New Game",
            "Do you want to start a new game?",
        )

        if answer == answer.Yes:
            self.start_new_game()

    def start_new_game(self) -> None:
        """Start a new game by resetting everything."""
        if self._game.is_perspective_flipped():
            self.flip_clock_positions()

        self._black_clock.reset()
        self._white_clock.reset()
        self._opening_label.clear()

        self._game.set_new_game()
        self._table_model.reset()
        self._engine.stop_analysis()
        self._notifications_label.clear()
        self._engine_analysis_label.clear()
        self._evaluation_bar.reset_appearance()

        self.show_fen()
        self.switch_clock_timers()
        self.adjust_engine_buttons()

        self._svg_board.draw()

        if self._game.is_engine_on_turn():
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
            self._table_view.select_previous_item()
        elif downward_roll:
            self._table_view.select_next_item()

    @Slot()
    def on_black_clock_time_expired(self) -> None:
        """Notify that White wins on time."""
        self._notifications_label.setText("White wins on time")

    @Slot()
    def on_white_clock_time_expired(self) -> None:
        """Notify that Black wins on time."""
        self._notifications_label.setText("Black wins on time")

    @Slot(Move)
    def on_best_move_analyzed(self, best_move: Move) -> None:
        """Show the given `best_move` from engine analysis."""
        self._game.set_arrow_for(best_move)
        self._svg_board.draw()

    @Slot(int)
    def on_index_selected(self, index: int) -> None:
        """Set a position and an arrow by the `index`."""
        if index < 0:
            self._game.clear_arrow()
            self._opening_label.clear()
            self._game.set_root_position()
        else:
            move: Move = self._game.set_move_by(index)
            self._game.play_sound_effect_for(move)
            self._game.set_arrow_for(move)

        self.refresh_ui()

    @Slot(Move)
    def on_move_played(self, move: Move) -> None:
        """Play the `move` by pushing it and refreshing the UI."""
        if self._game.is_legal(move):
            if self._table_view.has_selection():
                self._table_view.clearFocus()
                self._table_view.clearSelection()
                self._game.delete_data_after(self._table_view.linear_index)

            self._game.push(move)
            self.refresh_ui()

    @Slot(str)
    def on_san_variation_analyzed(self, san_variation: str) -> None:
        """Show the `san_variation` from engine analysis."""
        self._engine_analysis_label.setText(san_variation)

    @Slot(Score)
    def on_white_score_analyzed(self, white_score: Score) -> None:
        """Show a position evaluation as per the `white_score`."""
        self._evaluation_bar.animate(white_score)
