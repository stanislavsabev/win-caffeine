"""Main GUI window."""
import logging
from types import TracebackType
from typing import Callable, Tuple, Type

from win_caffeine import settings
from win_caffeine import qt
from win_caffeine import utils
from win_caffeine import theme
from win_caffeine import custom_widgets as widgets
from win_caffeine import screen_lock
from win_caffeine import qworker

logger = logging.getLogger(__name__)


class MainWindow(qt.QMainWindow):
    """Main window."""

    def __init__(
        self,
        parent: qt.QWidget | None = None,
        flags: qt.Qt.WindowFlags | None = None,
    ) -> None:
        """Main window."""
        flags = flags or qt.Qt.WindowFlags()
        super().__init__(parent, flags)
        self.suspend_action: Callable = self.release_suspend_lock
        self.thread_pool = qt.QThreadPool()
        self.duration_widget = widgets.DurationWidget()
        self.method_widget = widgets.RadioButtonGroup(
            options=[strategy.name for strategy in screen_lock.strategies],
            exclusive=True,
        )
        self.state_label = qt.QLabel()
        self.toggle_button = qt.QPushButton()
        self.settings_button = qt.QPushButton()
        self.exit_button = qt.QPushButton()
        self.central_widget = qt.QWidget()
        self._settings = qt.QSettings(qt.QSettings.UserScope, "User", settings.APP_NAME)
        self.setup_ui()
        self.setup_model()
        self.connect_signals()
        self.update_toggle_state()

    def setup_ui(self):
        central_layout = qt.QVBoxLayout()
        method_layout = qt.QVBoxLayout()
        method_layout.addWidget(qt.QLabel("Suspend method"))
        method_layout.addWidget(self.method_widget)
        self.setup_buttons()
        buttons_layout = qt.QHBoxLayout()
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.settings_button)
        buttons_layout.addWidget(self.exit_button)
        central_layout.addLayout(method_layout)
        central_layout.addWidget(self.duration_widget)
        central_layout.addWidget(self.state_label)
        central_layout.addLayout(buttons_layout)
        self.central_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_widget)
        self.setup_window()
        self.settings_button.setVisible(False)

    def setup_window(self):
        self._settings.beginGroup("WindowSettings")
        window_pos = self._settings.value("window_pos", settings.WINDOW_POSITION)
        self.move(qt.QPoint(*window_pos))
        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(qt.QIcon(theme.icon_path.coffee_on))
        self.setFixedWidth(settings.WINDOW_FIXED_WIDTH)
        self.setFixedHeight(settings.WINDOW_FIXED_HEIGHT)
        self._settings.endGroup()

    def setup_buttons(self):
        self.toggle_button.setObjectName("toggle_button")
        self.settings_button.setObjectName("settings_button")
        self.exit_button.setObjectName("exit_button")
        for btn in [self.settings_button, self.exit_button]:
            btn.setFixedSize(qt.QSize(25, 25))
        self.settings_button.setIcon(qt.QIcon(theme.icon_path.settings))
        self.exit_button.setIcon(qt.QIcon(theme.icon_path.exit))
        self.settings_button.setToolTip("Settings")
        self.exit_button.setToolTip("Exit")
        self.method_widget.setToolTip("Suspend method")

    def setup_model(self):
        self._settings.beginGroup("ModelSettings")
        strategy_ndx = self._settings.value(
            "strategy_index", settings.DEFAULT_STRATEGY_INDEX
        )
        duration_checked = self._settings.value(
            "duration_checked", qt.Qt.CheckState.Unchecked
        )
        duration_minutes = self._settings.value(
            "duration_minutes", settings.DEFAULT_DURATION_MINUTES, int
        )
        refresh_interval_seconds = self._settings.value(
            "refresh_interval_seconds", settings.DEFAULT_REFRESH_INTERVAL_SECONDS, int
        )

        self.method_widget.setButtonChecked(strategy_ndx)
        screen_lock.set_strategy(strategy_ndx)
        screen_lock.set_suspended(False)

        self.state_label.setText(self.get_state_message())
        self.duration_widget.checkbox.setChecked(duration_checked)
        self.duration_widget.on_enable_duration_changed(duration_checked)
        self.duration_widget.duration.setValue(duration_minutes)
        self.duration_widget.interval.setValue(refresh_interval_seconds)

        self._settings.endGroup()

    def connect_signals(self):
        self.toggle_button.clicked.connect(self.on_toggle_button_clicked)
        self.settings_button.clicked.connect(self.on_settings_button_clicked)
        self.exit_button.clicked.connect(self.on_window_exit_clicked)
        self.method_widget.buttons_group.buttonClicked.connect(
            self.on_method_button_clicked
        )

    def save_settings(self):
        self.save_window_settings()
        self.save_model_settings()

    def save_window_settings(self):
        self._settings.beginGroup("WindowSettings")
        self._settings.setValue("window_pos", self.pos().toTuple())
        self._settings.endGroup()

    def save_model_settings(self):
        self._settings.beginGroup("ModelSettings")
        self._settings.setValue("strategy_index", screen_lock.get_strategy())
        self._settings.setValue(
            "duration_checked", self.duration_widget.checkbox.checkState()
        )
        self._settings.setValue(
            "duration_minutes", self.duration_widget.duration.value()
        )
        self._settings.setValue(
            "refresh_interval_seconds", self.duration_widget.interval.value()
        )
        self._settings.endGroup()

    def close(self) -> bool:
        return self.hide()

    def update_toggle_state(self):
        logger.debug("update_toggle_state")
        mode = "off"
        next_mode = "on"
        icon: qt.QIcon = None
        if screen_lock.get_suspended():
            mode, next_mode = next_mode, mode
            icon = qt.QIcon(theme.icon_path.coffee_on)
            self.suspend_action = self.release_suspend_lock
            self.method_widget.setEnabled(False)
            action_name = "release_suspend_lock"
        else:
            self.suspend_action = self.run_suspend_lock
            self.method_widget.setEnabled(True)
            icon = qt.QIcon(theme.icon_path.coffee_off)
            action_name = "run_suspend_lock"

        logger.debug("Next suspend_action = {}".format(action_name))
        self.toggle_button.setIcon(icon)
        self.toggle_button.setText(f"Turn {next_mode}")
        self.state_label.setText(self.get_state_message())

    def get_state_message(self) -> str:
        state = "disabled" if not screen_lock.get_suspended() else "enabled"
        return f"Suspend screen lock is {state}"

    def on_toggle_button_clicked(self):
        logger.debug("on_toggle_button_clicked")
        try:
            self.suspend_action()
        except Exception:
            self.statusBar().showMessage(
                "Suspend action failed!", settings.STATUS_MESSAGE_DURATION_MSECONDS
            )

    def on_settings_button_clicked(self):
        logger.debug("Show settings dialog")

    def on_method_button_clicked(self, object):
        ndx = self.method_widget.buttons_group.id(object)
        screen_lock.set_strategy(ndx)

    def on_window_exit_clicked(self):
        if screen_lock.get_suspended():
            self.release_suspend_lock()
        self.save_settings()
        qt.QApplication.instance().quit()

    def release_suspend_lock(self):
        screen_lock.release_screen_lock_suspend()

    def run_suspend_lock(self):
        if screen_lock.get_suspended():
            self.statusBar().showMessage(
                "Duration lock suspend is running!",
                settings.STATUS_MESSAGE_DURATION_MSECONDS,
            )
            return

        worker = None
        if self.duration_widget.checkbox.isChecked():
            worker = qworker.QWorker(
                screen_lock.duration_suspend_screen_lock,
                self.duration_widget.duration.spin_box.value(),
                self.duration_widget.interval.spin_box.value(),
            )
        else:
            worker = qworker.QWorker(screen_lock.suspend_screen_lock)

        worker.signals.error.connect(self.on_duration_error)
        worker.signals.before_start.connect(self.on_before_start)
        worker.signals.finished.connect(self.on_finished)
        worker.signals.progress.connect(self.on_progress)
        if settings.MULTITHREADING:
            self.thread_pool.start(worker)
        else:
            worker.run()

    def on_duration_error(
        self,
        exc_info: Tuple[Type[BaseException], BaseException, TracebackType],
    ):
        _, exc, _ = exc_info
        logger.debug(exc.args)

    def on_before_start(
        self,
    ):
        screen_lock.set_suspended(True)
        self.duration_widget.setEnabled(False)
        self.update_toggle_state()

    def on_finished(
        self,
    ):
        screen_lock.set_suspended(False)
        self.duration_widget.setEnabled(True)
        self.update_toggle_state()

    def on_progress(self, msg: str):
        td_str = utils.get_time_hh_mm_ss(int(msg))
        self.state_label.setText(self.get_state_message() + f" ({td_str})")
